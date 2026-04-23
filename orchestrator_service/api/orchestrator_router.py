"""
编排服务 API 路由 - 北向接口
编排服务是算网中枢，管控光网和算力两个南向适配模块
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from core.workflow import PDWorkflow
from clients.network_client import NetworkClient
from clients.compute_client import ComputeClient

router = APIRouter()


class PDDeployRequest(BaseModel):
    source_node: str
    dest_node: str
    odu_type: Optional[str] = "ietf-otn-types:prot-ODU4"
    bandwidth: Optional[str] = "100000"
    p_cluster: Optional[str] = "ShaoGuan-DC-A"
    d_cluster: Optional[str] = "GuangZhou-DC-B"


class RollbackRequest(BaseModel):
    tunnel_name: str


@router.post("/pd/deploy")
def pd_deploy(request: PDDeployRequest):
    """
    P/D 分离拉远部署全流程
    POST /api/v1/orchestrator/pd/deploy
    """
    wf = PDWorkflow()
    result = wf.pd_deploy_workflow(
        source_node=request.source_node,
        dest_node=request.dest_node,
        odu_type=request.odu_type,
        bandwidth=request.bandwidth,
        p_cluster=request.p_cluster,
        d_cluster=request.d_cluster
    )
    if result["status"] == "failed":
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result


@router.post("/pd/rollback")
def pd_rollback(request: RollbackRequest):
    """
    全链路回滚
    POST /api/v1/orchestrator/pd/rollback
    """
    wf = PDWorkflow()
    return wf.full_rollback(request.tunnel_name)


@router.get("/actn/topology")
def get_topology():
    """查询光网拓扑（通过内部适配器）"""
    client = NetworkClient()
    return client.get_topology()


@router.post("/actn/path/precompute")
def precompute_path(
    request_id: str, source_node: str, destination_node: str,
    odu_type: str = "ietf-otn-types:prot-ODU4", bandwidth: str = "100000"
):
    """路径预计算（通过内部适配器）"""
    client = NetworkClient()
    return client.precompute_path(request_id, source_node, destination_node, odu_type, bandwidth)


@router.post("/actn/te/tunnel")
def create_te_tunnel(
    tunnel_name: str, source: str, destination: str, path_id: str,
    odu_type: str = "ietf-otn-types:prot-ODU4"
):
    """创建 TE 隧道（通过内部适配器）"""
    client = NetworkClient()
    return client.create_te_tunnel(tunnel_name, source, destination, path_id, odu_type)


@router.delete("/actn/te/tunnel/{tunnel_name}")
def delete_te_tunnel(tunnel_name: str):
    """删除 TE 隧道（通过内部适配器）"""
    client = NetworkClient()
    return client.delete_te_tunnel(tunnel_name)


@router.post("/compute/auth/token")
def compute_get_token(username: str = "admin", password: str = "123456"):
    """获取算力 Token（通过内部适配器）"""
    client = ComputeClient()
    return client.get_token(username, password)


@router.get("/compute/resource/cluster/overview")
def compute_get_resource():
    """查询集群资源（通过内部适配器）"""
    client = ComputeClient()
    client.get_token()
    return client.get_cluster_resource()


@router.post("/compute/inferjob")
def compute_submit_job(
    TaskjobName: str, ClusterName: str, role: str,
    GpuCount: int = 1, GpuType: str = "A100-80G", LlmModelId: int = 1001
):
    """提交推理作业（通过内部适配器）"""
    client = ComputeClient()
    client.get_token()
    return client.submit_infer_job(TaskjobName, ClusterName, role, GpuCount, GpuType, LlmModelId)
