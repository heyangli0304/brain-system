"""
算力适配服务 - Mock SDK
严格遵循《算力网络北向接口规范》
作为编排服务的内部南向适配模块
"""
from typing import Dict, Any

MOCK_TOKEN = "compute-brain-token-20260422"

MOCK_CLUSTERS = [
    {
        "cluster_name": "ShaoGuan-DC-A",
        "cluster_type": "ai",
        "total_card": 8,
        "card_info": [{"card_type": "A100-80G", "card_available_count": 4}]
    },
    {
        "cluster_name": "GuangZhou-DC-B",
        "cluster_type": "ai",
        "total_card": 8,
        "card_info": [{"card_type": "A100-80G", "card_available_count": 4}]
    }
]

MOCK_JOBS: Dict[int, Dict[str, Any]] = {}
_job_counter = 10000


def get_token(username: str, password: str) -> Dict[str, Any]:
    if username == "admin" and password == "123456":
        return {
            "respCode": 0,
            "respError": "",
            "respMessage": "success",
            "respBody": {"core-sctoken": MOCK_TOKEN},
            "custCode": 0
        }
    return {
        "respCode": 1,
        "respError": "auth failed",
        "respMessage": "invalid credentials",
        "respBody": {},
        "custCode": 0
    }


def get_cluster_resource() -> Dict[str, Any]:
    return {
        "respCode": 0,
        "respError": "",
        "respMessage": "success",
        "respBody": {"data": MOCK_CLUSTERS},
        "custCode": 0
    }


def submit_infer_job(taskjob_name: str, cluster_name: str, role: str,
                     gpu_count: int = 1, gpu_type: str = "A100-80G",
                     llm_model_id: int = 1001) -> Dict[str, Any]:
    global _job_counter
    _job_counter += 1
    job_id = _job_counter
    MOCK_JOBS[job_id] = {
        "jobId": job_id,
        "TaskjobName": taskjob_name,
        "ClusterName": cluster_name,
        "role": role,
        "status": "running"
    }
    return {
        "respCode": 0,
        "respError": "",
        "respMessage": "success",
        "respBody": {"jobId": job_id},
        "custCode": 0
    }


def get_job_metrics(job_id: int) -> Dict[str, Any]:
    if job_id not in MOCK_JOBS:
        return {
            "respCode": 1,
            "respError": "job not found",
            "respMessage": "job not found",
            "respBody": {},
            "custCode": 0
        }
    return {
        "respCode": 0,
        "respError": "",
        "respMessage": "success",
        "respBody": {
            "jobId": job_id,
            "metrics": [
                {"metric_types": "infer_ttft", "value_current": 150, "unit": "ms"},
                {"metric_types": "infer_tpot", "value_current": 20, "unit": "ms"}
            ]
        },
        "custCode": 0
    }
