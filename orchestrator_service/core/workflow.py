"""
P/D 分离拉远部署编排工作流
核心流程：路径预计算 -> 选择路径 -> 创建TE隧道 -> 获取ODU资源 -> 提交算力作业
直接调用内部适配器 SDK，无需 HTTP 转发
"""
import uuid
from typing import Dict, Any, Optional
from clients.network_client import NetworkClient
from clients.compute_client import ComputeClient


class PDWorkflow:
    def __init__(self):
        self.network = NetworkClient()
        self.compute = ComputeClient()

    def pd_deploy_workflow(
        self,
        source_node: str,
        dest_node: str,
        odu_type: str = "ietf-otn-types:prot-ODU4",
        bandwidth: str = "100000",
        p_cluster: str = "ShaoGuan-DC-A",
        d_cluster: str = "GuangZhou-DC-B"
    ) -> Dict[str, Any]:
        """
        P/D 分离拉远部署全流程
        1. 路径预计算
        2. 选择路径
        3. 创建 TE 隧道
        4. 获取 ODU 资源
        5. 提交 P/D 推理作业
        """
        request_id = f"req-{uuid.uuid4().hex[:8]}"
        tunnel_name = f"tunnel-{uuid.uuid4().hex[:8]}"
        result = {"request_id": request_id, "tunnel_name": tunnel_name, "steps": {}}

        try:
            path_result = self.network.precompute_path(
                request_id=request_id,
                source_node=source_node,
                dest_node=dest_node,
                odu_type=odu_type,
                bandwidth=bandwidth
            )
            path_list = path_result.get("data", {}).get("path-list", [])
            if not path_list:
                raise Exception("no available path")
            result["steps"]["precompute"] = {"status": "success", "path_count": len(path_list)}

            selected_path = min(path_list, key=lambda p: p.get("delay", 99999))
            path_id = selected_path["path-id"]
            result["steps"]["path_select"] = {"status": "success", "path_id": path_id, "delay": selected_path["delay"]}

            tunnel_result = self.network.create_te_tunnel(
                tunnel_name=tunnel_name,
                source=source_node,
                destination=dest_node,
                path_id=path_id,
                odu_type=odu_type
            )
            tunnel_data = tunnel_result.get("data", {})
            odu_info = tunnel_data.get("odu-resource-info", [])
            result["steps"]["tunnel_create"] = {
                "status": "success",
                "provisioning_state": tunnel_data.get("provisioning-state"),
                "odu_resource_info": odu_info
            }

            auth_result = self.compute.get_token()
            if auth_result.get("respCode") != 0:
                raise Exception("compute auth failed")
            result["steps"]["compute_auth"] = {"status": "success"}

            proxy_job = self.compute.submit_infer_job(
                taskjob_name=f"pd-proxy-{uuid.uuid4().hex[:6]}",
                cluster_name=d_cluster, role="proxy"
            )
            prefill_job = self.compute.submit_infer_job(
                taskjob_name=f"pd-prefill-{uuid.uuid4().hex[:6]}",
                cluster_name=p_cluster, role="prefill"
            )
            decode_job = self.compute.submit_infer_job(
                taskjob_name=f"pd-decode-{uuid.uuid4().hex[:6]}",
                cluster_name=d_cluster, role="decode"
            )
            result["steps"]["jobs"] = {
                "status": "success",
                "proxy_job_id": proxy_job.get("respBody", {}).get("jobId"),
                "prefill_job_id": prefill_job.get("respBody", {}).get("jobId"),
                "decode_job_id": decode_job.get("respBody", {}).get("jobId")
            }

            result["status"] = "success"
            result["message"] = "P/D deploy success"

        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            try:
                self.network.delete_te_tunnel(tunnel_name)
                result["rollback"] = "tunnel deleted"
            except Exception:
                result["rollback"] = "tunnel delete failed"

        return result

    def full_rollback(self, tunnel_name: str, job_ids: list = None) -> Dict[str, Any]:
        """全链路回滚"""
        result = {"steps": {}}
        try:
            r = self.network.delete_te_tunnel(tunnel_name)
            result["steps"]["tunnel_delete"] = r
        except Exception as e:
            result["steps"]["tunnel_delete"] = {"error": str(e)}
        result["status"] = "completed"
        return result
