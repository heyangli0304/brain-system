"""
算力南向适配接口路由
整合同事的完整算力接口：认证/资源/监控/文件/镜像/模型/算法/作业/Webhook
作为编排服务的内部南向适配模块
"""
from fastapi import APIRouter, Header, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from adapters.compute.sdk.auth import AuthClient
from adapters.compute.sdk.job import JobClient
from adapters.compute.sdk.fs import FsClient
from adapters.compute.sdk.monitor import MonitorClient

router = APIRouter()

auth_client = AuthClient()
job_client = JobClient()
fs_client = FsClient()
monitor_client = MonitorClient()


def _sync_headers():
    try:
        h = auth_client.auth_header
        job_client.headers = h
        fs_client.headers = h
        monitor_client.headers = h
    except RuntimeError:
        pass


# ==========================================
# 认证
# ==========================================

class LoginRequest(BaseModel):
    username: str
    password: str

class AuthTokenRequest(BaseModel):
    username: str
    password: str

@router.post("/auth/login")
def api_login(req: LoginRequest):
    result = auth_client.login(req.username, req.password)
    if result.get("respCode") != 0:
        raise HTTPException(status_code=401, detail=result.get("respError", "login failed"))
    _sync_headers()
    return result

@router.post("/auth/token")
def api_get_token(req: AuthTokenRequest):
    result = auth_client.login(req.username, req.password)
    if result.get("respCode") != 0:
        raise HTTPException(status_code=401, detail=result.get("respError", "auth failed"))
    _sync_headers()
    return result


# ==========================================
# 资源查询
# ==========================================

@router.get("/resource/cluster/overview")
def api_cluster_overview(cluster_names: Optional[str] = None, region: Optional[str] = None):
    return monitor_client.get_cluster_overview(cluster_names, region)


# ==========================================
# 性能监控
# ==========================================

@router.get("/adapter/getPDJobMonitorMetrics")
def api_job_metrics(
    job_id: int = Query(..., alias="jobId"),
    cluster: Optional[str] = None,
    metric_types: Optional[List[str]] = Query(None, alias="metricTypes"),
    start_time: Optional[str] = Query(None, alias="startTime"),
    end_time: Optional[str] = Query(None, alias="endTime"),
):
    return monitor_client.get_job_metrics(job_id, cluster, metric_types, start_time, end_time)


@router.get("/monitor/metrics/job")
def api_job_metrics_compat(
    job_id: int, cluster: Optional[str] = None, metric_types: Optional[str] = None,
    start_time: Optional[str] = None, end_time: Optional[str] = None,
):
    metrics = metric_types.split(",") if metric_types else None
    return monitor_client.get_job_metrics(job_id, cluster, metrics, start_time, end_time)

@router.get("/monitor/job/{job_id}")
def api_get_job_metrics_legacy(job_id: int):
    return monitor_client.get_job_metrics(job_id, cluster="default")


# ==========================================
# 消息通知
# ==========================================

class SubscribeEventsRequest(BaseModel):
    event_types: list
    description: Optional[str] = None

@router.post("/notification/webhook/subscribe")
def api_subscribe_events(req: SubscribeEventsRequest):
    return job_client.subscribe_events(req.event_types, req.description)


@router.post("/notification/subscribe")
def api_subscribe_events_compat(req: SubscribeEventsRequest):
    return api_subscribe_events(req)


@router.get("/notification/stream")
def api_stream_events():
    return StreamingResponse(
        job_client.stream_events(), media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.delete("/notification/webhook/unsubscribe")
def api_unsubscribe_events(subscription_id: Optional[str] = None):
    return job_client.unsubscribe_events(subscription_id)


# ==========================================
# Webhook 通知接收
# ==========================================

job_status_store: Dict[int, Dict[str, Any]] = {}
pending_notifications: list = []

class WebhookEvent(BaseModel):
    event_type: str
    event_data: Dict[str, Any]
    timestamp: Optional[int] = None

@router.post("/webhook/status_update")
def receive_status_update(event: WebhookEvent):
    event_type = event.event_type
    if event_type == "JOB_STATUS_CHANGE":
        data = event.event_data
        job_id = data.get("job_id")
        new_status = data.get("new_status")
        if job_id:
            job_status_store[job_id] = {
                "status": new_status, "cluster": data.get("cluster", ""),
                "reason": data.get("reason", ""), "updated_at": event.timestamp,
            }
        pending_notifications.append({
            "type": "JOB_STATUS_CHANGE", "job_id": job_id,
            "new_status": new_status, "cluster": data.get("cluster", ""),
        })
        return {"status": "received", "event": "JOB_STATUS_CHANGE", "job_id": job_id, "new_status": new_status}
    elif event_type == "RESOURCE_ALARM":
        data = event.event_data
        pending_notifications.append({
            "type": "RESOURCE_ALARM", "cluster": data.get("cluster_name", ""),
            "alarm_type": data.get("alarm_type", ""), "alarm_level": data.get("alarm_level", ""),
        })
        return {"status": "received", "event": "RESOURCE_ALARM", "cluster": data.get("cluster_name", "")}
    return {"status": "received", "event": event_type}

@router.get("/webhook/job_status/{job_id}")
def get_job_status(job_id: int):
    if job_id in job_status_store:
        return {"job_id": job_id, **job_status_store[job_id]}
    return {"job_id": job_id, "status": "unknown", "message": "no status update received"}

@router.get("/webhook/notifications")
def get_pending_notifications():
    notifications = pending_notifications.copy()
    pending_notifications.clear()
    return {"count": len(notifications), "notifications": notifications}


# ==========================================
# 文件操作
# ==========================================

class CreateDirectoryRequest(BaseModel):
    fs_dir: str
    cluster: str

@router.post("/fs/dir/create")
def api_create_directory(req: CreateDirectoryRequest):
    return fs_client.create_directory(req.fs_dir, req.cluster)

class MergeFileChunksRequest(BaseModel):
    chunk_dir: str
    file_hash: str
    file_name: str
    total_chunks: str

@router.post("/fs/merge")
def api_merge_file_chunks(req: MergeFileChunksRequest):
    return fs_client.merge_file_chunks(req.chunk_dir, req.file_hash, req.file_name, req.total_chunks)


# ==========================================
# 环境镜像
# ==========================================

class CreateImageRequest(BaseModel):
    img_name: str
    img_tags: str
    source: str
    source_path: str
    cluster_id: str
    is_public: bool
    hardware: Optional[str] = None
    framework: Optional[str] = None
    framework_version: Optional[str] = None
    cuda_version: Optional[str] = None
    cann_version: Optional[str] = None
    python_version: Optional[str] = None
    extra_install: Optional[List[str]] = None
    scene: Optional[List[str]] = None
    img_description: Optional[str] = None

@router.post("/image/insert")
def api_create_image(req: CreateImageRequest):
    kwargs = {k: v for k, v in req.model_dump().items()
              if k not in ("img_name", "img_tags", "source", "source_path", "cluster_id", "is_public") and v is not None}
    return job_client.create_image(
        req.img_name, req.img_tags, req.source, req.source_path,
        req.cluster_id, req.is_public, **kwargs,
    )


# ==========================================
# 模型对象注册
# ==========================================

class CreateModelRequest(BaseModel):
    llm_name: str
    cluster_name: str
    llm_tags: str
    llm_description: str
    cluster: str
    llm_is_public: int

@router.post("/model/insert")
def api_create_model(req: CreateModelRequest):
    return job_client.create_model(
        req.llm_name, req.cluster_name, req.llm_tags,
        req.llm_description, req.cluster, req.llm_is_public,
    )

class CreateModelVersionRequest(BaseModel):
    spec_version_path: str
    cluster_fs: str
    version_is_public: int
    spec_version_name: str
    version_spec: str
    spec_version_description: str
    spec_version_type: Optional[str] = None
    spec_version_tags: Optional[str] = None
    spec_version_icon: Optional[str] = None

@router.post("/model/version/insert")
def api_create_model_version(req: CreateModelVersionRequest):
    kwargs = {k: v for k, v in req.model_dump().items()
              if k not in ("spec_version_path", "cluster_fs", "version_is_public",
                           "spec_version_name", "version_spec", "spec_version_description") and v is not None}
    return job_client.create_model_version(
        req.spec_version_path, req.cluster_fs, req.version_is_public,
        req.spec_version_name, req.version_spec, req.spec_version_description, **kwargs,
    )


# ==========================================
# 算法对象注册
# ==========================================

class CreateAlgorithmRequest(BaseModel):
    algorithm_name: str
    algorithm_description: str
    algorithm_is_public: int
    cluster: str
    algorithm_version: Optional[str] = None
    algorithm_source: Optional[str] = None
    algorithm_location: Optional[str] = None
    algorithm_tags: Optional[str] = None
    algorithm_status: Optional[str] = None
    algorithm_logo: Optional[str] = None

@router.post("/algorithm/insert")
def api_create_algorithm(req: CreateAlgorithmRequest):
    kwargs = {k: v for k, v in req.model_dump().items()
              if k not in ("algorithm_name", "algorithm_description", "algorithm_is_public", "cluster") and v is not None}
    return job_client.create_algorithm(
        req.algorithm_name, req.algorithm_description, req.algorithm_is_public, req.cluster, **kwargs,
    )

class CreateAlgorithmVersionRequest(BaseModel):
    version_name: str
    cluster_fs: str
    version_source: str
    version_location: str
    version_is_public: int
    algorithm_id: str
    version_tags: Optional[str] = None
    favorite: Optional[str] = None
    version_description: Optional[str] = None
    version_status: Optional[str] = None
    version_logo: Optional[str] = None
    algorithm_role: Optional[str] = None

@router.post("/algorithm/version/insert")
def api_create_algorithm_version(req: CreateAlgorithmVersionRequest):
    kwargs = {k: v for k, v in req.model_dump().items()
              if k not in ("version_name", "cluster_fs", "version_source",
                           "version_location", "version_is_public", "algorithm_id") and v is not None}
    return job_client.create_algorithm_version(
        req.version_name, req.cluster_fs, req.version_source,
        req.version_location, req.version_is_public, req.algorithm_id, **kwargs,
    )


# ==========================================
# 提交推理作业
# ==========================================

class SubmitPDInferJobRequest(BaseModel):
    TaskjobName: str
    ClusterName: str
    Account: str
    Partition: str
    Qos: Optional[str] = None
    NodeCount: int
    GpuCount: Optional[int] = None
    GpuType: Optional[str] = None
    MemoryMb: Optional[int] = None
    CoreCount: int
    TimeLimitMinutes: Optional[int] = None
    MountPoints: Optional[List[str]] = None
    Dataset: Optional[str] = None
    Model: Optional[str] = None
    Algorithm: Optional[str] = None
    Vram: Optional[int] = None
    DataDir: Optional[str] = None
    WorkingDirectory: Optional[str] = None
    LlmModelId: Optional[int] = None
    Role: str = ""
    PrefillerHosts: Optional[str] = None
    PrefillerPorts: Optional[str] = None
    DecoderHosts: Optional[str] = None
    DecoderPorts: Optional[str] = None

@router.post("/adapter/pdinferjobs")
def api_submit_pd_infer_job(req: SubmitPDInferJobRequest):
    try:
        return job_client.submit_pd_infer_job(
            req.TaskjobName, req.ClusterName, req.Account, req.Partition,
            req.Qos, req.NodeCount, req.GpuCount, req.GpuType, req.MemoryMb,
            req.CoreCount, req.TimeLimitMinutes, req.MountPoints, req.Dataset,
            req.Model, req.Algorithm, req.Vram, req.DataDir,
            req.WorkingDirectory, req.LlmModelId, req.Role,
            req.PrefillerHosts, req.PrefillerPorts, req.DecoderHosts,
            req.DecoderPorts,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


class SubmitInferJobRequest(SubmitPDInferJobRequest):
    role: Optional[str] = None
    proxy_export_url: Optional[str] = None


@router.post("/adapter/inferjobs")
def api_submit_infer_job_compat(req: SubmitInferJobRequest):
    data = req.dict()
    data["Role"] = req.role if req.role is not None else req.Role
    data.pop("role", None)
    data.pop("proxy_export_url", None)
    return api_submit_pd_infer_job(SubmitPDInferJobRequest(**data))

class SimpleInferJobRequest(BaseModel):
    TaskjobName: str
    ClusterName: str
    Role: str = ""
    role: Optional[str] = None
    GpuCount: Optional[int] = 1
    GpuType: Optional[str] = "A100-80G"
    LlmModelId: Optional[int] = 1001

@router.post("/inferjob")
def api_submit_simple_infer_job(req: SimpleInferJobRequest):
    return job_client.submit_pd_infer_job(
        taskjob_name=req.TaskjobName, cluster_name=req.ClusterName,
        account="default", partition="default", qos="default",
        node_count=1, gpu_count=req.GpuCount, gpu_type=req.GpuType,
        memory_mb=32768, core_count=8, time_limit_minutes=60,
        mount_points=["/data"], dataset="0", model="0", algorithm="0",
        vram=0, working_directory="/workspace",
        llm_model_id=req.LlmModelId, role=req.role if req.role is not None else req.Role,
    )


# ==========================================
# 获取作业详情
# ==========================================

@router.get("/adapter/getSpecPDJob")
def api_get_pd_job_detail(
    job_id: int = Query(..., alias="jobId"), cluster: Optional[str] = None,
    type: str = "pd",
):
    return job_client.get_job_detail(job_id, cluster, type)


@router.get("/adapter/getSpecJob")
def api_get_job_detail_compat(job_id: int, cluster: Optional[str] = None, type: str = "pd"):
    return job_client.get_job_detail(job_id, cluster, type)


@router.delete("/adapter/CancelSpecPDJob")
def api_cancel_pd_job(job_id: int = Query(..., alias="jobId"), cluster: Optional[str] = None):
    return job_client.cancel_pd_job(job_id, cluster)


@router.get("/adapter/queryPDJobTimeLimit")
def api_query_pd_job_time_limit(job_id: int = Query(..., alias="jobId"), cluster: Optional[str] = None):
    return job_client.query_pd_job_time_limit(job_id, cluster)


class ChangePDJobTimeLimitRequest(BaseModel):
    JobId: int
    DeltaMinutes: int
    Cluster: Optional[str] = None


@router.post("/adapter/changePDJobTimeLimit")
def api_change_pd_job_time_limit(req: ChangePDJobTimeLimitRequest):
    return job_client.change_pd_job_time_limit(req.JobId, req.DeltaMinutes, req.Cluster)


# ==========================================
# 请求模型推理
# ==========================================

class ChatCompletionsRequest(BaseModel):
    inferenceAddr: Optional[str] = None
    model: str
    messages: list
    stream: bool = False
    max_tokens: Optional[int] = None


@router.post("/inference/chat/completions")
def api_direct_chat_completions(req: ChatCompletionsRequest):
    if not req.inferenceAddr:
        raise HTTPException(status_code=400, detail="inferenceAddr is required")
    return job_client.chat_completions(
        req.inferenceAddr, req.model, req.messages, req.stream, req.max_tokens,
    )

@router.post("/modelProxy/{job_id}/v1/chat/completions")
def api_chat_completions_compat(job_id: str, req: ChatCompletionsRequest):
    try:
        return job_client.chat_completions_for_job(
            job_id, req.model, req.messages, req.stream, req.max_tokens,
        )
    except (TypeError, ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
