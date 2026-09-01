"""
算力南向适配服务 - 内部接口
文件位置：compute_adapter_service/api/internal_router.py
接收大管家(orchestrator)发来的内部命令，调用SDK干活后返回结果
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List

from sdk.auth import AuthClient
from sdk.job import JobClient
from sdk.fs import FsClient
from sdk.monitor import MonitorClient

router = APIRouter()

auth_client = AuthClient(base_url="http://算力控制器IP:8001")
job_client = JobClient(base_url="http://算力控制器IP:8001", token="placeholder")
fs_client = FsClient(base_url="http://算力控制器IP:8001", token="placeholder")
monitor_client = MonitorClient(base_url="http://算力控制器IP:8001", token="placeholder")


# ==========================================
# 认证
# ==========================================

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/auth/login")
def api_login(req: LoginRequest):
    result = auth_client.login(req.username, req.password)
    if result.get("respCode") != 0:
        raise HTTPException(status_code=401, detail=result.get("respError", "登录失败"))
    token = auth_client.token
    job_client.headers = auth_client.auth_header
    fs_client.headers = auth_client.auth_header
    monitor_client.headers = auth_client.auth_header
    return {"token": token, "message": "登录成功，Token已同步到所有客户端"}


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
    job_id: int = Query(..., alias="jobId"), cluster: Optional[str] = None,
    metric_types: Optional[List[str]] = Query(None, alias="metricTypes"),
    start_time: Optional[str] = Query(None, alias="startTime"),
    end_time: Optional[str] = Query(None, alias="endTime"),
):
    return monitor_client.get_job_metrics(job_id, cluster, metric_types, start_time, end_time)


@router.get("/monitor/metrics/job")
def api_job_metrics_compat(job_id: int, cluster: Optional[str] = None,
                           metric_types: Optional[str] = None,
                           start_time: Optional[str] = None,
                           end_time: Optional[str] = None):
    metrics = metric_types.split(",") if metric_types else None
    return monitor_client.get_job_metrics(job_id, cluster, metrics, start_time, end_time)


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
    return StreamingResponse(job_client.stream_events(), media_type="text/event-stream")


@router.delete("/notification/webhook/unsubscribe")
def api_unsubscribe_events(subscription_id: Optional[str] = None):
    return job_client.unsubscribe_events(subscription_id)


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


# ==========================================
# 获取作业详情
# ==========================================

@router.get("/adapter/getSpecPDJob")
def api_get_pd_job_detail(job_id: int = Query(..., alias="jobId"),
                          cluster: Optional[str] = None, type: str = "pd"):
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
