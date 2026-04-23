"""
算力南向适配服务 - 文件操作
文件位置：compute_adapter_service/sdk/fs.py
创建文件夹、分片上传模型文件、合并分片

对应 提取.MARKDOWN 章节：文件准备与对象注册
"""

import requests
from pydantic import BaseModel
from typing import Optional


# ==========================================
# 创建文件夹 - 返回数据结构
# POST /filesystem/fsposix/dir/create
# ==========================================

class CreateDirectoryResponse(BaseModel):
    respCode: int
    respError: str
    respMessage: Optional[str] = None
    respBody: Optional[str] = None
    custCode: int


# ==========================================
# 文件分片上传 - 返回数据结构
# POST /filesystem/fsposix/upload
# ==========================================

class UploadFileChunkResponse(BaseModel):
    respCode: int
    respError: str
    respMessage: Optional[str] = None
    respBody: Optional[str] = None
    custCode: int


# ==========================================
# 合并文件分片 - 返回数据结构
# POST /filesystem/fsposix/merge
# ==========================================

class MergeFileChunksResponse(BaseModel):
    respCode: int
    respError: str
    respMessage: Optional[str] = None
    respBody: Optional[str] = None
    custCode: int


# ==========================================
# 客户端类
# ==========================================

class FsClient:

    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {"Authorization": token}

    def create_directory(self, fs_dir, cluster) -> dict:
        """
        POST /filesystem/fsposix/dir/create

        由于跨域，物理文件需要在两端就绪
        cluster分别填DC-A和DC-B，路径保持一致（如 /models/llama3）
        """
        url = f"{self.base_url}/filesystem/fsposix/dir/create"
        payload = {"fsDir": fs_dir, "cluster": cluster}
        response = requests.post(url, json=payload, headers=self.headers)
        return response.json()

    def upload_file_chunk(self, chunk_index, md5_hash, path, chunk_data) -> dict:
        """
        POST /filesystem/fsposix/upload

        文件分片上传，单块不超过5MB
        需对DC-A和DC-B分别执行，确保两地都有模型权重文件
        """
        url = f"{self.base_url}/filesystem/fsposix/upload"
        files = {"ChunkData": chunk_data}
        data = {"ChunkIndex": chunk_index, "Md5Hash": md5_hash, "Path": path}
        response = requests.post(url, data=data, files=files, headers=self.headers)
        return response.json()

    def merge_file_chunks(self, chunk_dir, file_hash, file_name, total_chunks) -> dict:
        """
        POST /filesystem/fsposix/merge
        """
        url = f"{self.base_url}/filesystem/fsposix/merge"
        payload = {
            "ChunkDir": chunk_dir, "FileHash": file_hash,
            "FileName": file_name, "TotalChunks": total_chunks,
        }
        response = requests.post(url, json=payload, headers=self.headers)
        return response.json()
