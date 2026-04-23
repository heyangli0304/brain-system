"""
算力适配客户端 - 直接调用内部 SDK（本地模块调用，非 HTTP）
"""
from typing import Dict, Any
from adapters.compute.sdk.compute_sdk import get_token, get_cluster_resource, submit_infer_job, get_job_metrics


class ComputeClient:
    def __init__(self):
        self.token: str = ""

    def get_token(self, username: str = "admin", password: str = "123456") -> Dict[str, Any]:
        result = get_token(username, password)
        if result.get("respCode") == 0:
            self.token = result["respBody"]["core-sctoken"]
        return result

    def get_cluster_resource(self) -> Dict[str, Any]:
        return get_cluster_resource()

    def submit_infer_job(
        self, taskjob_name: str, cluster_name: str, role: str,
        gpu_count: int = 1, gpu_type: str = "A100-80G", llm_model_id: int = 1001
    ) -> Dict[str, Any]:
        return submit_infer_job(taskjob_name, cluster_name, role, gpu_count, gpu_type, llm_model_id)

    def get_job_metrics(self, job_id: int) -> Dict[str, Any]:
        return get_job_metrics(job_id)
