"""
算力适配 - 文件操作
整合自同事的 compute_adapter_service/sdk/fs.py
支持 Mock 模式（本地测试）和真实算力控制器调用
"""
from typing import Dict, Any

USE_MOCK = True


class FsClient:

    def __init__(self, base_url: str = "http://算力控制器IP:8001", token: str = ""):
        self.base_url = base_url
        self.headers = {"Authorization": token}

    def create_directory(self, fs_dir: str, cluster: str) -> Dict[str, Any]:
        if USE_MOCK:
            return {
                "respCode": 0, "respError": "", "respMessage": "success",
                "respBody": f"directory {fs_dir} created on {cluster}",
                "custCode": 0,
            }
        import requests
        url = f"{self.base_url}/filesystem/fsposix/dir/create"
        payload = {"fsDir": fs_dir, "cluster": cluster}
        response = requests.post(url, json=payload, headers=self.headers)
        return response.json()

    def upload_file_chunk(self, chunk_index: int, md5_hash: str, path: str, chunk_data) -> Dict[str, Any]:
        if USE_MOCK:
            return {
                "respCode": 0, "respError": "", "respMessage": "success",
                "respBody": f"chunk {chunk_index} uploaded",
                "custCode": 0,
            }
        import requests
        url = f"{self.base_url}/filesystem/fsposix/upload"
        files = {"ChunkData": chunk_data}
        data = {"ChunkIndex": chunk_index, "Md5Hash": md5_hash, "Path": path}
        response = requests.post(url, data=data, files=files, headers=self.headers)
        return response.json()

    def merge_file_chunks(self, chunk_dir: str, file_hash: str, file_name: str, total_chunks: str) -> Dict[str, Any]:
        if USE_MOCK:
            return {
                "respCode": 0, "respError": "", "respMessage": "success",
                "respBody": f"file {file_name} merged from {total_chunks} chunks",
                "custCode": 0,
            }
        import requests
        url = f"{self.base_url}/filesystem/fsposix/merge"
        payload = {
            "ChunkDir": chunk_dir, "FileHash": file_hash,
            "FileName": file_name, "TotalChunks": total_chunks,
        }
        response = requests.post(url, json=payload, headers=self.headers)
        return response.json()
