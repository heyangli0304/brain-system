"""
ACTN 光网接口路由
严格遵循 standard.txt 定义的接口规范
作为编排服务的内部南向适配模块
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from adapters.network.sdk.topology import get_topology, get_simplified_topology, precompute_path
from adapters.network.sdk.tunnel import tunnel_manager

router = APIRouter()


class PathPrecomputeRequest(BaseModel):
    request_id: str
    source_node: str
    destination_node: str
    odu_type: Optional[str] = "ietf-otn-types:prot-ODU4"
    bandwidth: Optional[str] = "100000"
    optimization_metric: Optional[str] = "ietf-te-types:path-metric-delay-average"


class TETunnelCreateRequest(BaseModel):
    tunnel_name: str
    source: str
    destination: str
    path_id: str
    encoding: Optional[str] = "ietf-te-types:lsp-encoding-oduk"
    switching_type: Optional[str] = "ietf-te-types:switching-otn"
    provisioning_state: Optional[str] = "ietf-te-types:tunnel-admin-state-up"
    te_bandwidth: Optional[Dict[str, Any]] = None
    protection: Optional[Dict[str, Any]] = None


@router.get("/topology")
def api_get_topology():
    return {"code": 0, "message": "success", "data": get_topology()}


@router.get("/topology/simplified")
def api_get_simplified_topology():
    return {"code": 0, "message": "success", "data": get_simplified_topology()}


@router.post("/path/precompute")
def api_precompute_path(request: PathPrecomputeRequest):
    paths = precompute_path(request.source_node, request.destination_node, request.odu_type)
    return {
        "code": 0,
        "message": "success",
        "data": {
            "request-id": request.request_id,
            "path-count": len(paths),
            "path-list": paths
        }
    }


@router.post("/te/tunnel")
def api_create_te_tunnel(request: TETunnelCreateRequest):
    result = tunnel_manager.create_tunnel(
        tunnel_name=request.tunnel_name,
        source=request.source,
        destination=request.destination,
        path_id=request.path_id,
        encoding=request.encoding,
        switching_type=request.switching_type,
        provisioning_state=request.provisioning_state,
        te_bandwidth=request.te_bandwidth,
        protection=request.protection
    )
    return result


@router.get("/te/tunnel/{tunnel_name}")
def api_get_te_tunnel(tunnel_name: str):
    return tunnel_manager.get_tunnel(tunnel_name)


@router.delete("/te/tunnel/{tunnel_name}")
def api_delete_te_tunnel(tunnel_name: str):
    return tunnel_manager.delete_tunnel(tunnel_name)


@router.get("/te/tunnels")
def api_list_te_tunnels():
    return {"code": 0, "message": "success", "data": tunnel_manager.list_tunnels()}
