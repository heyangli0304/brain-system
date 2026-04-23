"""
算力适配服务接口路由
严格遵循 standard.txt 定义的接口规范
作为编排服务的内部南向适配模块
"""
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from typing import Optional
from adapters.compute.sdk.compute_sdk import get_token, get_cluster_resource, submit_infer_job, get_job_metrics, MOCK_TOKEN

router = APIRouter()


class AuthRequest(BaseModel):
    username: str
    password: str


class InferJobRequest(BaseModel):
    TaskjobName: str
    ClusterName: str
    role: str
    GpuCount: Optional[int] = 1
    GpuType: Optional[str] = "A100-80G"
    LlmModelId: Optional[int] = 1001


def verify_token(authorization: str = Header(None)):
    if not authorization or MOCK_TOKEN not in authorization:
        raise HTTPException(status_code=401, detail="unauthorized")
    return authorization


@router.post("/auth/token")
def api_get_token(request: AuthRequest):
    return get_token(request.username, request.password)


@router.get("/resource/cluster/overview")
def api_get_cluster_resource(authorization: str = Header(None)):
    verify_token(authorization)
    return get_cluster_resource()


@router.post("/inferjob")
def api_submit_infer_job(request: InferJobRequest, authorization: str = Header(None)):
    verify_token(authorization)
    return submit_infer_job(
        taskjob_name=request.TaskjobName,
        cluster_name=request.ClusterName,
        role=request.role,
        gpu_count=request.GpuCount,
        gpu_type=request.GpuType,
        llm_model_id=request.LlmModelId
    )


@router.get("/monitor/job/{job_id}")
def api_get_job_metrics(job_id: int, authorization: str = Header(None)):
    verify_token(authorization)
    return get_job_metrics(job_id)
