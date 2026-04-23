"""
光网适配客户端 - 直接调用内部 SDK（本地模块调用，非 HTTP）
"""
from typing import Dict, Any, Optional, List
from adapters.network.sdk.topology import get_topology, get_simplified_topology, precompute_path
from adapters.network.sdk.tunnel import tunnel_manager


class NetworkClient:
    def get_topology(self) -> Dict[str, Any]:
        return {"code": 0, "message": "success", "data": get_topology()}

    def get_simplified_topology(self) -> Dict[str, Any]:
        return {"code": 0, "message": "success", "data": get_simplified_topology()}

    def precompute_path(
        self, request_id: str, source_node: str, dest_node: str,
        odu_type: str = "ietf-otn-types:prot-ODU4",
        bandwidth: str = "100000",
        optimization_metric: str = "ietf-te-types:path-metric-delay-average"
    ) -> Dict[str, Any]:
        paths = precompute_path(source_node, dest_node, odu_type)
        return {
            "code": 0,
            "message": "success",
            "data": {
                "request-id": request_id,
                "path-count": len(paths),
                "path-list": paths
            }
        }

    def create_te_tunnel(
        self, tunnel_name: str, source: str, destination: str, path_id: str,
        odu_type: str = "ietf-otn-types:prot-ODU4",
        encoding: str = "ietf-te-types:lsp-encoding-oduk",
        switching_type: str = "ietf-te-types:switching-otn"
    ) -> Dict[str, Any]:
        return tunnel_manager.create_tunnel(
            tunnel_name=tunnel_name,
            source=source,
            destination=destination,
            path_id=path_id,
            encoding=encoding,
            switching_type=switching_type,
            te_bandwidth={"ietf-otn-tunnel:odu-type": odu_type},
            protection={"enable": True, "protection-type": "bidir-1-to-1"}
        )

    def get_te_tunnel(self, tunnel_name: str) -> Dict[str, Any]:
        return tunnel_manager.get_tunnel(tunnel_name)

    def delete_te_tunnel(self, tunnel_name: str) -> Dict[str, Any]:
        return tunnel_manager.delete_tunnel(tunnel_name)
