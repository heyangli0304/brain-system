"""
算力适配客户端 - 直接调用内部 SDK（本地模块调用，非 HTTP）
整合同事的完整算力接口
"""
from typing import Dict, Any, Optional, List
from adapters.compute.sdk.auth import AuthClient
from adapters.compute.sdk.job import JobClient
from adapters.compute.sdk.fs import FsClient
from adapters.compute.sdk.monitor import MonitorClient


class ComputeClient:
    def __init__(self):
        self.auth = AuthClient()
        self.job = JobClient()
        self.fs = FsClient()
        self.monitor = MonitorClient()

    def _sync(self):
        try:
            h = self.auth.auth_header
            self.job.headers = h
            self.fs.headers = h
            self.monitor.headers = h
        except RuntimeError:
            pass

    def get_token(self, username: str = "admin", password: str = "123456") -> Dict[str, Any]:
        result = self.auth.login(username, password)
        self._sync()
        return result

    def get_cluster_resource(self, cluster_names: str = None, region: str = None) -> Dict[str, Any]:
        return self.monitor.get_cluster_overview(cluster_names, region)

    def submit_infer_job(
        self, taskjob_name: str, cluster_name: str, role: str,
        gpu_count: int = 1, gpu_type: str = "A100-80G", llm_model_id: int = 1001
    ) -> Dict[str, Any]:
        return self.job.submit_infer_job(
            taskjob_name=taskjob_name, cluster_name=cluster_name,
            account="default", partition="default", qos="default",
            node_count=1, gpu_count=gpu_count, gpu_type=gpu_type,
            memory_mb=32768, core_count=8, time_limit_minutes=60,
            mount_points=["/data"], dataset=0, model=0, algorithm=0,
            vram=0, working_directory="/workspace",
            llm_model_id=llm_model_id, role=role,
        )

    def submit_full_infer_job(
        self, taskjob_name, cluster_name, account, partition, qos,
        node_count, gpu_count, gpu_type, memory_mb, core_count,
        time_limit_minutes, mount_points, dataset, model, algorithm,
        vram, working_directory, llm_model_id, role, proxy_export_url=None
    ) -> Dict[str, Any]:
        return self.job.submit_infer_job(
            taskjob_name, cluster_name, account, partition, qos,
            node_count, gpu_count, gpu_type, memory_mb, core_count,
            time_limit_minutes, mount_points, dataset, model, algorithm,
            vram, working_directory, llm_model_id, role, proxy_export_url,
        )

    def get_job_metrics(self, job_id: int, cluster: str = "default") -> Dict[str, Any]:
        return self.monitor.get_job_metrics(job_id, cluster)

    def get_job_detail(self, job_id: int, cluster: str, job_type: str) -> Dict[str, Any]:
        return self.job.get_job_detail(job_id, cluster, job_type)

    def chat_completions(self, job_id, model, messages, stream) -> Dict[str, Any]:
        return self.job.chat_completions(job_id, model, messages, stream)

    def create_directory(self, fs_dir: str, cluster: str) -> Dict[str, Any]:
        return self.fs.create_directory(fs_dir, cluster)

    def merge_file_chunks(self, chunk_dir, file_hash, file_name, total_chunks) -> Dict[str, Any]:
        return self.fs.merge_file_chunks(chunk_dir, file_hash, file_name, total_chunks)

    def create_image(self, img_name, img_tags, source, source_path, cluster_id, is_public, **kwargs) -> Dict[str, Any]:
        return self.job.create_image(img_name, img_tags, source, source_path, cluster_id, is_public, **kwargs)

    def create_model(self, llm_name, cluster_name, llm_tags, llm_description, cluster, llm_is_public) -> Dict[str, Any]:
        return self.job.create_model(llm_name, cluster_name, llm_tags, llm_description, cluster, llm_is_public)

    def create_algorithm(self, algorithm_name, algorithm_description, algorithm_is_public, cluster, **kwargs) -> Dict[str, Any]:
        return self.job.create_algorithm(algorithm_name, algorithm_description, algorithm_is_public, cluster, **kwargs)
