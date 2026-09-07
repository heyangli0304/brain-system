"""
算力适配 - 作业与对象注册
整合自同事的 compute_adapter_service/sdk/job.py
支持 Mock 模式（本地测试）和真实算力控制器调用
"""
import uuid
from typing import Dict, Any, Optional, List

USE_MOCK = True

MOCK_JOBS: Dict[int, Dict[str, Any]] = {}
_job_counter = 10000


class JobClient:

    def __init__(self, base_url: str = "http://算力控制器IP:8001", token: str = ""):
        self.base_url = base_url
        self.headers = {"Authorization": token}

    def subscribe_events(self, event_types: list, description: str = None) -> Dict[str, Any]:
        if USE_MOCK:
            return {
                "respCode": 0, "respError": "", "respMessage": "success",
                "respBody": {"subscription_id": f"sub-{uuid.uuid4().hex[:8]}"},
                "custCode": 0,
            }
        import requests
        url = f"{self.base_url}/sys/notification/webhook/subscribe"
        payload = {"event_types": event_types}
        if description:
            payload["description"] = description
        response = requests.post(url, json=payload, headers=self.headers)
        return response.json()

    def create_image(self, img_name, img_tags, source, source_path, cluster_id, is_public, **kwargs) -> Dict[str, Any]:
        if USE_MOCK:
            return {
                "respCode": 0, "respError": "", "respMessage": "success",
                "respBody": {
                    "id": 1, "uuid": uuid.uuid4().hex, "img_name": img_name,
                    "img_type": "infer", "created_at": "2026-04-23", "updated_at": "2026-04-23",
                    "soft_deleted": False, "img_spec": "", "img_tags": img_tags,
                    "created_by": "admin", "img_description": kwargs.get("img_description", ""),
                },
                "custCode": 0,
            }
        import requests
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

    def create_model(self, llm_name, cluster_name, llm_tags, llm_description, cluster, llm_is_public) -> Dict[str, Any]:
        if USE_MOCK:
            return {
                "respCode": 0, "respError": "", "respMessage": "success",
                "respBody": {
                    "data": {
                        "id": 1, "uuid": uuid.uuid4().hex, "llm_name": llm_name,
                        "llm_type": "llm", "created_at": "2026-04-23", "updated_at": "2026-04-23",
                        "soft_deleted": False, "llm_spec": "", "llm_tags": llm_tags,
                        "created_by": "admin", "updated_by": "admin",
                        "llm_description": llm_description, "llm_status": 1,
                        "llm_icon": "", "llm_path": f"/models/{llm_name}",
                        "llm_isPublic": llm_is_public, "cluster": cluster,
                        "public_tenant_id": 1,
                    }
                },
                "custCode": 0,
            }
        import requests
        url = f"{self.base_url}/llm/model/insert"
        payload = {
            "llm_name": llm_name, "clusterName": cluster_name,
            "llm_tags": llm_tags, "llm_description": llm_description,
            "cluster": cluster, "llm_isPublic": llm_is_public,
        }
        response = requests.post(url, json=payload, headers=self.headers)
        return response.json()

    def create_model_version(self, spec_version_path, cluster_fs, version_is_public,
                             spec_version_name, version_spec, spec_version_description, **kwargs) -> Dict[str, Any]:
        if USE_MOCK:
            return {
                "respCode": 0, "respError": "", "respMessage": "success",
                "respBody": {
                    "data": {
                        "id": 1, "uuid": uuid.uuid4().hex,
                        "spec_version_name": spec_version_name,
                        "spec_version_type": kwargs.get("spec_version_type", ""),
                        "created_at": "2026-04-23", "updated_at": "2026-04-23",
                        "soft_deleted": False, "version_spec": version_spec,
                        "spec_version_tags": kwargs.get("spec_version_tags", ""),
                        "created_by": "admin", "updated_by": "admin",
                        "spec_version_description": spec_version_description,
                        "spec_version_status": 1, "spec_version_icon": "",
                        "spec_version_path": spec_version_path,
                        "llm_models_id": 1, "version_isPublic": version_is_public,
                        "spec_version_sample_path": "", "cluster_fs": cluster_fs,
                        "public_tenant_id": 1, "algorithm_version": "",
                    }
                },
                "custCode": 0,
            }
        import requests
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

    def create_algorithm(self, algorithm_name, algorithm_description, algorithm_is_public, cluster, **kwargs) -> Dict[str, Any]:
        if USE_MOCK:
            return {
                "respCode": 0, "respError": "", "respMessage": "success",
                "respBody": {
                    "data": {
                        "id": 1, "uuid": uuid.uuid4().hex, "algorithm_name": algorithm_name,
                        "favorite": 0, "created_by": "admin", "created_at": "2026-04-23",
                        "updated_at": "2026-04-23", "soft_deleted": False,
                        "algorithm_version": kwargs.get("algorithm_version", ""),
                        "algorithm_source": kwargs.get("algorithm_source", ""),
                        "algorithm_location": kwargs.get("algorithm_location", ""),
                        "algorithm_description": algorithm_description,
                        "algorithm_tags": kwargs.get("algorithm_tags", ""),
                        "algorithm_status": 1, "algorithm_logo": "",
                        "cluster": cluster, "algorithm_isPublic": bool(algorithm_is_public),
                        "public_tenant_id": 1,
                    }
                },
                "custCode": 0,
            }
        import requests
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
                                 version_location, version_is_public, algorithm_id, **kwargs) -> Dict[str, Any]:
        if USE_MOCK:
            return {
                "respCode": 0, "respError": "", "respMessage": "success",
                "respBody": {
                    "data": {
                        "id": 1, "uuid": uuid.uuid4().hex, "version_name": version_name,
                        "favorite": False, "created_by": "admin", "created_at": "2026-04-23",
                        "updated_at": "2026-04-23", "soft_deleted": False,
                        "version_source": version_source, "version_location": version_location,
                        "version_description": kwargs.get("version_description", ""),
                        "version_tags": kwargs.get("version_tags", ""),
                        "version_status": 1, "version_logo": "",
                        "version_isPublic": version_is_public, "algorithm_id": int(algorithm_id),
                        "version_sample_location": "", "cluster_fs": cluster_fs,
                        "public_tenant_id": 1,
                    }
                },
                "custCode": 0,
            }
        import requests
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

    def submit_infer_job(self, taskjob_name, cluster_name, account, partition,
                         qos, node_count, gpu_count, gpu_type, memory_mb, core_count,
                         time_limit_minutes, mount_points, dataset, model, algorithm,
                         vram, working_directory, llm_model_id, role, proxy_export_url=None) -> Dict[str, Any]:
        global _job_counter
        if USE_MOCK:
            _job_counter += 1
            job_id = _job_counter
            MOCK_JOBS[job_id] = {
                "jobId": job_id, "TaskjobName": taskjob_name,
                "ClusterName": cluster_name, "role": role, "status": "running",
            }
            return {
                "respCode": 0, "respError": "", "respMessage": "success",
                "respBody": {"jobId": job_id}, "custCode": 0,
            }
        import requests
        url = f"{self.base_url}/ai_sc/adapter/inferjobs"
        payload = {
            "TaskjobName": taskjob_name, "ClusterName": cluster_name,
            "Account": account, "Partition": partition, "Qos": qos,
            "NodeCount": node_count, "GpuCount": gpu_count, "GpuType": gpu_type,
            "MemoryMb": memory_mb, "CoreCount": core_count,
            "TimeLimitMinutes": time_limit_minutes, "MountPoints": mount_points,
            "Dataset": dataset, "Model": model, "Algorithm": algorithm,
            "Vram": vram, "WorkingDirectory": working_directory,
            "LlmModelId": llm_model_id, "role": role,
        }
        if proxy_export_url:
            payload["proxy_export_url"] = proxy_export_url
        response = requests.post(url, json=payload, headers=self.headers)
        return response.json()

    def get_job_detail(self, job_id, cluster, job_type) -> Dict[str, Any]:
        if USE_MOCK:
            if job_id in MOCK_JOBS:
                job = MOCK_JOBS[job_id]
                return {
                    "respCode": 0, "respError": "", "respMessage": "success",
                    "respBody": {
                        "id": job_id, "taskjob_name": job.get("TaskjobName", ""),
                        "taskjob_cluster": job.get("ClusterName", cluster),
                        "taskjob_status_enum": 3, "taskjob_model_export_url": f"http://proxy-{job_id}:8000",
                        "runtime_metrics": {
                            "timestamp": 0, "active_reqs": 0, "gpu_util_avg": 0.8,
                            "kv_cache_usage": 0.5, "gpu_mem_used": 70000,
                            "infer_tpot": 20.0, "infer_ttft": 150.0,
                        },
                    },
                    "custCode": 0,
                }
            return {"respCode": 1, "respError": "job not found", "respMessage": "job not found", "respBody": {}, "custCode": 0}
        import requests
        url = f"{self.base_url}/ai_sc/adapter/getSpecJob"
        params = {"jobId": job_id, "cluster": cluster, "type": job_type}
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def chat_completions(self, job_id, model, messages, stream, content_type="application/json") -> Dict[str, Any]:
        if USE_MOCK:
            return {
                "respCode": 0, "respError": "", "respMessage": "success",
                "respBody": {
                    "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
                    "object": "chat.completion",
                    "model": model,
                    "choices": [{"index": 0, "message": {"role": "assistant", "content": "Hello! I am a mock response."}}],
                },
                "custCode": 0,
            }
        import requests
        url = f"{self.base_url}/modelProxy/{job_id}/v1/chat/completions"
        headers = {"Authorization": self.headers.get("Authorization", ""), "Content-Type": content_type}
        payload = {"model": model, "messages": messages, "stream": stream}
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
