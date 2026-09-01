"""
算力南向适配服务 - 作业与对象注册
文件位置：compute_adapter_service/sdk/job.py
提交推理作业、模型/算法/镜像注册、事件订阅、响应用户请求

对应 提取.MARKDOWN 章节：
  - 消息通知功能
  - 环境镜像
  - 模型对象注册
  - 算法对象注册
  - 提交proxy作业
  - 获取Proxy节点url
  - 提交P/D作业
  - 响应用户请求
"""

import requests
from pydantic import BaseModel
from typing import Iterable, Optional, List, Dict, Any


# ==========================================
# 消息通知功能 - 返回数据结构
# POST /sys/notification/webhook/subscribe
# ==========================================

class EventSubscriptionRespBody(BaseModel):
    subscription_id: str

class EventSubscriptionResponse(BaseModel):
    respCode: int
    respError: str
    respBody: EventSubscriptionRespBody
    custCode: int


# ==========================================
# 环境镜像 - 返回数据结构
# POST /ai_sc/image/insert
# ==========================================

class CreateImageRespBody(BaseModel):
    id: int
    uuid: Optional[str] = None
    img_name: str
    img_type: str
    created_at: str
    updated_at: str
    soft_deleted: bool
    img_spec: str
    img_tags: str
    created_by: str
    updated_by: Optional[str] = None
    img_description: str

class CreateImageResponse(BaseModel):
    respCode: int
    respError: str
    respMessage: Optional[str] = None
    respBody: CreateImageRespBody
    custCode: int


# ==========================================
# 模型对象注册 - 返回数据结构
# POST /llm/model/insert
# ==========================================

class ModelData(BaseModel):
    id: int
    uuid: str
    llm_name: str
    llm_type: str
    created_at: str
    updated_at: str
    soft_deleted: bool
    llm_spec: str
    llm_tags: str
    created_by: str
    updated_by: str
    llm_description: str
    llm_status: int
    llm_icon: str
    llm_path: str
    llm_isPublic: int
    cluster: str
    public_tenant_id: int
    algorithm_name: Optional[str] = None
    algorithm_framework: Optional[str] = None
    hardware: Optional[str] = None
    cuda_version: Optional[str] = None
    cann_version: Optional[str] = None
    python_version: Optional[str] = None
    scene: Optional[str] = None
    is_large_model: Optional[str] = None

class CreateModelRespBody(BaseModel):
    data: ModelData

class CreateModelResponse(BaseModel):
    respCode: int
    respError: str
    respMessage: Optional[str] = None
    respBody: CreateModelRespBody
    custCode: int


# ==========================================
# 模型版本插入 - 返回数据结构
# POST /llm_specversion/llmversion/insert
# ==========================================

class ModelVersionData(BaseModel):
    id: int
    uuid: str
    spec_version_name: str
    spec_version_type: str
    created_at: str
    updated_at: str
    soft_deleted: bool
    version_spec: str
    spec_version_tags: str
    created_by: str
    updated_by: str
    spec_version_description: str
    spec_version_status: int
    spec_version_icon: str
    spec_version_path: str
    llm_models_id: int
    version_isPublic: int
    spec_version_sample_path: str
    cluster_fs: str
    public_tenant_id: int
    algorithm_version: str

class CreateModelVersionRespBody(BaseModel):
    data: ModelVersionData

class CreateModelVersionResponse(BaseModel):
    respCode: int
    respError: str
    respMessage: Optional[str] = None
    respBody: CreateModelVersionRespBody
    custCode: int


# ==========================================
# 算法对象注册 - 返回数据结构
# POST /ai_sc/algorithm/insert
# ==========================================

class AlgorithmData(BaseModel):
    id: int
    uuid: str
    algorithm_name: str
    favorite: int
    created_by: str
    created_at: str
    updated_by: Optional[str] = None
    updated_at: str
    soft_deleted: bool
    algorithm_version: str
    algorithm_source: str
    algorithm_location: str
    algorithm_description: str
    algorithm_tags: str
    algorithm_status: int
    algorithm_logo: str
    cluster: str
    algorithm_isPublic: bool
    public_tenant_id: int

class CreateAlgorithmRespBody(BaseModel):
    data: AlgorithmData

class CreateAlgorithmResponse(BaseModel):
    respCode: int
    respError: str
    respMessage: Optional[str] = None
    respBody: CreateAlgorithmRespBody
    custCode: int


# ==========================================
# 算法版本插入 - 返回数据结构
# POST /ai_sc/algorithmversion/insert
# ==========================================

class AlgorithmVersionData(BaseModel):
    id: int
    uuid: str
    version_name: str
    favorite: bool
    created_by: str
    created_at: str
    updated_by: Optional[str] = None
    updated_at: str
    soft_deleted: bool
    version_source: str
    version_location: str
    version_description: str
    version_tags: str
    version_status: int
    version_logo: str
    version_isPublic: int
    algorithm_id: int
    version_sample_location: str
    cluster_fs: str
    public_tenant_id: int

class CreateAlgorithmVersionRespBody(BaseModel):
    data: AlgorithmVersionData

class CreateAlgorithmVersionResponse(BaseModel):
    respCode: int
    respError: str
    respMessage: Optional[str] = None
    respBody: CreateAlgorithmVersionRespBody
    custCode: int


# ==========================================
# 提交推理作业 - 返回数据结构
# POST /ai_sc/adapter/inferjobs
# ==========================================

class SubmitInferJobRespBody(BaseModel):
    jobId: int
    adapterJobId: Optional[int] = None
    inferenceAddr: Optional[str] = None
    role: Optional[str] = None

class SubmitInferJobResponse(BaseModel):
    respCode: int
    respError: str
    respMessage: Optional[str] = None
    respBody: SubmitInferJobRespBody
    custCode: int


# ==========================================
# 获取作业详情 - 返回数据结构
# GET /ai_sc/adapter/getSpecJob
# ==========================================

class RuntimeMetrics(BaseModel):
    timestamp: int
    active_reqs: int
    gpu_util_avg: float
    kv_cache_usage: float
    gpu_mem_used: int
    infer_tpot: Optional[float] = None
    infer_ttft: Optional[float] = None

class GetJobDetailRespBody(BaseModel):
    deducted_coretime: float
    id: int
    reason: str
    taskjob_algorithm_path: str
    taskjob_app_id: int
    taskjob_cluster: str
    taskjob_cluster_type: str
    taskjob_config: str
    taskjob_coretime: float
    taskjob_cpu_count: int
    taskjob_data_path: str
    taskjob_dataset_path: str
    taskjob_finished_at: int
    taskjob_gpu_count: int
    taskjob_gpu_type: str
    taskjob_id_adapter: int
    taskjob_image_path: str
    taskjob_mem: int
    taskjob_model_addr: str
    taskjob_model_export_url: str
    taskjob_model_name: str
    taskjob_model_path: str
    taskjob_mountpoints: str
    taskjob_name: str
    taskjob_node_count: int
    taskjob_partition: str
    taskjob_qos: str
    taskjob_sshd_host: str
    taskjob_sshd_passwd: str
    taskjob_sshd_port: int
    taskjob_sshd_user: str
    taskjob_started_at: int
    taskjob_status_enum: int
    taskjob_submitted_by: str
    taskjob_summitted_at: int
    taskjob_timelimit: int
    taskjob_type: str
    taskjob_varm: int
    taskjob_workingdirectory: str
    type_enum: int
    runtime_metrics: Optional[RuntimeMetrics] = None

class GetJobDetailResponse(BaseModel):
    respCode: int
    respError: str
    respMessage: Optional[str] = None
    respBody: GetJobDetailRespBody
    custCode: int


# ==========================================
# 响应用户请求 - 返回数据结构
# POST /modelProxy/:jobId/v1/chat/completions
# ==========================================

class ChatCompletionsResponse(BaseModel):
    respCode: int
    respError: str
    respMessage: Optional[str] = None
    respBody: Optional[Dict[str, Any]] = None
    custCode: int


# ==========================================
# 客户端类
# ==========================================

class JobClient:

    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {"Authorization": token}

    # ==========================================
    # 消息通知功能
    # ==========================================

    def subscribe_events(self, event_types: list, description: str = None) -> dict:
        """
        POST /sys/notification/webhook/subscribe

        算网大脑需要实时感知任务状态变化和资源变化
        让控制器知道往哪里发送通知
        """
        url = f"{self.base_url}/sys/notification/webhook/subscribe"
        payload = {"event_types": event_types}
        if description:
            payload["description"] = description
        response = requests.post(url, json=payload, headers=self.headers)
        return response.json()

    def stream_events(self) -> Iterable[bytes]:
        url = f"{self.base_url}/sys/notification/stream"
        with requests.get(url, headers=self.headers, stream=True, timeout=(10, None)) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                yield line + b"\n"

    def unsubscribe_events(self, subscription_id: str = None) -> dict:
        url = f"{self.base_url}/sys/notification/webhook/unsubscribe"
        params = {"subscription_id": subscription_id} if subscription_id else None
        return requests.delete(url, headers=self.headers, params=params).json()

    # ==========================================
    # 环境镜像
    # ==========================================

    def create_image(self, img_name, img_tags, source, source_path, cluster_id, is_public, **kwargs) -> dict:
        """
        POST /ai_sc/image/insert

        注册支持PD分离的推理引擎镜像（如vLLM）
        source取值：INTERNAL / EXTERNAL
        """
        url = f"{self.base_url}/ai_sc/image/insert"
        payload = {
            "img_name": img_name, "img_tags": img_tags,
            "source": source, "sourcePath": source_path,
            "cluster_id": cluster_id, "is_public": is_public,
        }
        for k in ("hardware", "framework", "framework_version", "cuda_version",
                   "cann_version", "python_version", "extra_install", "scene", "img_description"):
            if k in kwargs:
                payload[k] = kwargs[k]
        response = requests.post(url, json=payload, headers=self.headers)
        return response.json()

    # ==========================================
    # 模型对象注册
    # ==========================================

    def create_model(self, llm_name, cluster_name, llm_tags, llm_description, cluster, llm_is_public) -> dict:
        """
        POST /llm/model/insert

        注册模型对象（如 Llama-3-70B）
        """
        url = f"{self.base_url}/llm/model/insert"
        payload = {
            "llm_name": llm_name, "clusterName": cluster_name,
            "llm_tags": llm_tags, "llm_description": llm_description,
            "cluster": cluster, "llm_isPublic": llm_is_public,
        }
        response = requests.post(url, json=payload, headers=self.headers)
        return response.json()

    def create_model_version(self, spec_version_path, cluster_fs, version_is_public,
                             spec_version_name, version_spec, spec_version_description, **kwargs) -> dict:
        """
        POST /llm_specversion/llmversion/insert

        注册模型的具体版本
        spec_version_path指向创建的文件夹路径
        """
        url = f"{self.base_url}/llm_specversion/llmversion/insert"
        payload = {
            "spec_version_path": spec_version_path, "cluster_fs": cluster_fs,
            "version_isPublic": version_is_public, "spec_version_name": spec_version_name,
            "version_spec": version_spec, "spec_version_description": spec_version_description,
        }
        for k in ("spec_version_type", "spec_version_tags", "spec_version_icon"):
            if k in kwargs:
                payload[k] = kwargs[k]
        response = requests.post(url, json=payload, headers=self.headers)
        return response.json()

    # ==========================================
    # 算法对象注册
    # ==========================================

    def create_algorithm(self, algorithm_name, algorithm_description, algorithm_is_public, cluster, **kwargs) -> dict:
        """
        POST /ai_sc/algorithm/insert

        注册算法对象（如 vLLM-PD）
        """
        url = f"{self.base_url}/ai_sc/algorithm/insert"
        payload = {
            "algorithm_name": algorithm_name, "algorithm_description": algorithm_description,
            "algorithm_isPublic": algorithm_is_public, "cluster": cluster,
        }
        for k in ("algorithm_version", "algorithm_source", "algorithm_location",
                   "algorithm_tags", "algorithm_status", "algorithm_logo"):
            if k in kwargs:
                payload[k] = kwargs[k]
        response = requests.post(url, json=payload, headers=self.headers)
        return response.json()

    def create_algorithm_version(self, version_name, cluster_fs, version_source,
                                 version_location, version_is_public, algorithm_id, **kwargs) -> dict:
        """
        POST /ai_sc/algorithmversion/insert

        拉起跨域P/D分离服务需创建三个不同角色的算法版本：
          Version-Proxy:   algorithm_role = "proxy"
          Version-Prefill:  algorithm_role = "prefill"
          Version-Decode:   algorithm_role = "decode"
        """
        url = f"{self.base_url}/ai_sc/algorithmversion/insert"
        payload = {
            "version_name": version_name, "cluster_fs": cluster_fs,
            "version_source": version_source, "version_location": version_location,
            "version_isPublic": version_is_public, "algorithm_id": algorithm_id,
        }
        for k in ("version_tags", "favorite", "version_description",
                   "version_status", "version_logo", "algorithm_role"):
            if k in kwargs:
                payload[k] = kwargs[k]
        response = requests.post(url, json=payload, headers=self.headers)
        return response.json()

    # ==========================================
    # 提交推理作业
    # ==========================================

    def submit_pd_infer_job(
        self, taskjob_name, cluster_name, account, partition, qos=None,
        node_count=1, gpu_count=None, gpu_type=None, memory_mb=None,
        core_count=1, time_limit_minutes=None, mount_points=None, dataset=None,
        model=None, algorithm=None, vram=None, data_dir=None,
        working_directory=None, llm_model_id=None, role="",
        prefiller_hosts=None, prefiller_ports=None, decoder_hosts=None,
        decoder_ports=None, _allow_incomplete_proxy=False,
    ) -> dict:
        """
        POST /ai_sc/adapter/pdinferjobs
        """
        role = {"prefill": "Prefill", "decode": "Decode", "proxy": "Proxy"}.get(
            (role or "").lower(), role or ""
        )
        if role not in {"", "Prefill", "Decode", "Proxy"}:
            raise ValueError("Role must be one of: '', Prefill, Decode, Proxy")
        addresses = (prefiller_hosts, prefiller_ports, decoder_hosts, decoder_ports)
        if role == "" and any(addresses):
            raise ValueError("Ordinary inference jobs cannot include Prefiller/Decoder addresses")
        if role == "Proxy" and not all(addresses) and not _allow_incomplete_proxy:
            raise ValueError("Proxy jobs require PrefillerHosts/Ports and DecoderHosts/Ports")

        url = f"{self.base_url}/ai_sc/adapter/pdinferjobs"
        payload = {
            "TaskjobName": taskjob_name, "ClusterName": cluster_name,
            "Account": account, "Partition": partition, "Qos": qos,
            "NodeCount": node_count, "GpuCount": gpu_count, "GpuType": gpu_type,
            "MemoryMb": memory_mb, "CoreCount": core_count,
            "TimeLimitMinutes": time_limit_minutes, "MountPoints": mount_points,
            "Dataset": dataset, "Model": model, "Algorithm": algorithm,
            "Vram": vram, "DataDir": data_dir, "WorkingDirectory": working_directory,
            "LlmModelId": llm_model_id, "Role": role,
            "PrefillerHosts": prefiller_hosts, "PrefillerPorts": prefiller_ports,
            "DecoderHosts": decoder_hosts, "DecoderPorts": decoder_ports,
        }
        payload = {key: value for key, value in payload.items() if value is not None}
        response = requests.post(url, json=payload, headers=self.headers)
        return response.json()

    def submit_infer_job(self, taskjob_name, cluster_name, account, partition,
                         qos, node_count, gpu_count, gpu_type, memory_mb, core_count,
                         time_limit_minutes, mount_points, dataset, model, algorithm,
                         vram, working_directory, llm_model_id, role,
                         proxy_export_url=None, **kwargs) -> dict:
        return self.submit_pd_infer_job(
            taskjob_name, cluster_name, account, partition, qos, node_count,
            gpu_count, gpu_type, memory_mb, core_count, time_limit_minutes,
            mount_points, str(dataset) if dataset is not None else None,
            str(model) if model is not None else None,
            str(algorithm) if algorithm is not None else None, vram,
            kwargs.get("data_dir"), working_directory, llm_model_id, role,
            kwargs.get("prefiller_hosts"), kwargs.get("prefiller_ports"),
            kwargs.get("decoder_hosts"), kwargs.get("decoder_ports"), True,
        )

    # ==========================================
    # 获取作业详情
    # ==========================================

    def get_job_detail(self, job_id, cluster=None, job_type="pd") -> dict:
        """
        GET /ai_sc/adapter/getSpecPDJob

        当算网大脑接收Proxy启动成功的作业状态变更消息时调用
        用这个接口获取proxy的url，作为PD作业的参数进行部署
        """
        url = f"{self.base_url}/ai_sc/adapter/getSpecPDJob"
        params = {"jobId": job_id, "type": job_type}
        if cluster:
            params["cluster"] = cluster
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def cancel_pd_job(self, job_id, cluster=None) -> dict:
        url = f"{self.base_url}/ai_sc/adapter/CancelSpecPDJob"
        params = {"jobId": job_id}
        if cluster:
            params["cluster"] = cluster
        return requests.delete(url, headers=self.headers, params=params).json()

    def query_pd_job_time_limit(self, job_id, cluster=None) -> dict:
        url = f"{self.base_url}/ai_sc/adapter/queryPDJobTimeLimit"
        params = {"jobId": job_id}
        if cluster:
            params["cluster"] = cluster
        return requests.get(url, headers=self.headers, params=params).json()

    def change_pd_job_time_limit(self, job_id, delta_minutes, cluster=None) -> dict:
        url = f"{self.base_url}/ai_sc/adapter/changePDJobTimeLimit"
        payload = {"JobId": job_id, "DeltaMinutes": delta_minutes}
        if cluster:
            payload["Cluster"] = cluster
        return requests.post(url, json=payload, headers=self.headers).json()

    # ==========================================
    # 请求模型推理
    # ==========================================

    def chat_completions(self, inference_addr, model, messages, stream=False,
                         max_tokens=None, content_type="application/json") -> dict:
        """
        POST http://{inferenceAddr}/v1/chat/completions

        等待所有P/D作业状态变更为RUNNING后调用
        算网大脑直接将用户请求转发到proxy所在集群
        proxy负责调度用户请求到具体的P/D实例
        """
        url = f"{inference_addr.rstrip('/')}/v1/chat/completions"
        headers = {"Content-Type": content_type}
        payload = {"model": model, "messages": messages, "stream": stream}
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        response = requests.post(url, json=payload, headers=headers)
        return response.json()

    def chat_completions_for_job(self, job_id, model, messages, stream=False,
                                 max_tokens=None) -> dict:
        detail = self.get_job_detail(int(job_id))
        body = detail.get("respBody", {})
        inference_addr = body.get("taskjob_model_export_url") or body.get("taskjob_model_addr")
        if not inference_addr:
            raise RuntimeError("Inference address is not ready")
        return self.chat_completions(inference_addr, model, messages, stream, max_tokens)
