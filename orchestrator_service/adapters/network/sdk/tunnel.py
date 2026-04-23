"""
TE隧道管理模块 - 核心调度单元
创建TE隧道并返回ODUk资源信息
"""
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from adapters.network.sdk.topology import get_odu_resource_for_link, precompute_path


class TETunnelManager:
    def __init__(self):
        self.tunnels: Dict[str, Dict[str, Any]] = {}

    def create_tunnel(
        self,
        tunnel_name: str,
        source: str,
        destination: str,
        path_id: str,
        encoding: str = "ietf-te-types:lsp-encoding-oduk",
        switching_type: str = "ietf-te-types:switching-otn",
        provisioning_state: str = "ietf-te-types:tunnel-admin-state-up",
        te_bandwidth: Optional[Dict] = None,
        protection: Optional[Dict] = None
    ) -> Dict[str, Any]:
        paths = precompute_path(source, destination)
        matched_path = None
        for p in paths:
            if p["path-id"] == path_id:
                matched_path = p
                break

        if not matched_path:
            return {"code": 1, "message": f"path {path_id} not found between {source} and {destination}", "data": None}

        if tunnel_name in self.tunnels:
            return {"code": 1, "message": f"tunnel {tunnel_name} already exists", "data": None}

        odu_resource_info = []
        for link_id in matched_path.get("link-id-list", []):
            link_odu = get_odu_resource_for_link(link_id)
            if link_odu:
                odu_resource_info = link_odu
                break

        tunnel_data = {
            "tunnel-name": tunnel_name,
            "source": source,
            "destination": destination,
            "path-id": path_id,
            "encoding": encoding,
            "switching-type": switching_type,
            "provisioning-state": "up",
            "operational-state": "up",
            "te-bandwidth": te_bandwidth or {"ietf-otn-tunnel:odu-type": "ietf-otn-types:prot-ODU4"},
            "protection": protection or {"enable": True, "protection-type": "bidir-1-to-1"},
            "odu-resource-info": odu_resource_info,
            "create-time": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        }

        self.tunnels[tunnel_name] = tunnel_data

        return {
            "code": 0,
            "message": "success",
            "data": tunnel_data
        }

    def get_tunnel(self, tunnel_name: str) -> Dict[str, Any]:
        if tunnel_name not in self.tunnels:
            return {"code": 1, "message": f"tunnel {tunnel_name} not found", "data": None}
        return {"code": 0, "message": "success", "data": self.tunnels[tunnel_name]}

    def delete_tunnel(self, tunnel_name: str) -> Dict[str, Any]:
        if tunnel_name not in self.tunnels:
            return {"code": 1, "message": f"tunnel {tunnel_name} not found", "data": None}
        del self.tunnels[tunnel_name]
        return {
            "code": 0,
            "message": "success",
            "data": {"tunnel-name": tunnel_name, "status": "deleted"}
        }

    def list_tunnels(self) -> List[Dict[str, Any]]:
        return list(self.tunnels.values())


tunnel_manager = TETunnelManager()
