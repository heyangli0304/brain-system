"""
算力南向适配服务 - 性能监控
文件位置：compute_adapter_service/sdk/monitor.py
查询GPU水位、TTFT/TPOT性能监控指标

对应 提取.MARKDOWN 章节：全局资源感知与调度决策 - 资源查询 / 性能监控
"""

import requests  
from pydantic import BaseModel
from typing import List, Optional


# ==========================================
# 集群资源概览 - 返回数据结构
# GET /ai_sc/resource/cluster/overview
# ==========================================

class NetInfo(BaseModel):
    network_type: str
    nic_speed_gbps: int

class CardInfo(BaseModel):
    card_type: str
    card_memory: int
    card_total_count: int
    card_available_count: int
    card_connect_type: str
    card_connect_speed: int

class NodeMetricsInfo(BaseModel):
    node_type: str
    node_total_count: int
    node_available_count: int
    card_info: List[CardInfo]
    net_info: NetInfo

class ClusterData(BaseModel):
    control_plane_uuid: str
    control_plane_name: str
    control_plane_status: int
    cluster_name: str
    cluster_type: str
    region: str
    total_node: int
    total_card: int
    node_metrics_info: List[NodeMetricsInfo]

class ClusterOverviewRespBody(BaseModel):
    data: List[ClusterData]

class ClusterOverviewResponse(BaseModel):
    respCode: int
    respError: str
    respMessage: Optional[str] = None
    respBody: ClusterOverviewRespBody
    custCode: int


# ==========================================
# 作业监控指标 - 返回数据结构
# GET /ai_sc/monitor/metrics/job
# ==========================================

class MetricItem(BaseModel):
    metric_types: str
    unit: str
    timestamp: int
    value_current: float
    value_mean: Optional[float] = None
    value_max: Optional[float] = None

class JobMetricsRespBody(BaseModel):
    jobId: int
    metrics: List[MetricItem]

class GetJobMetricsResponse(BaseModel):
    respCode: int
    respError: str
    respMessage: Optional[str] = None
    respBody: JobMetricsRespBody
    custCode: int


# ==========================================
# 客户端类
# ==========================================

class MonitorClient:

    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {"Authorization": token}

    # ==========================================
    # 资源查询
    # ==========================================

    def get_cluster_overview(self, cluster_names=None, region=None) -> dict:
        """
        GET /ai_sc/resource/cluster/overview

        算网大脑在调度前，需要查询所有纳管数据中心的资源水位
        card_connect_type（如NVLink）决定是否支持模型并行
        network_type（如RoCE）决定是否支持跨节点KV Transfer
        调度P节点时需同时满足两者
        """
        url = f"{self.base_url}/ai_sc/resource/cluster/overview"
        params = {}
        if cluster_names:
            params["cluster_names"] = cluster_names
        if region:
            params["region"] = region
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    # ==========================================
    # 性能监控
    # ==========================================

    def get_job_metrics(self, job_id, cluster, metric_types=None, start_time=None, end_time=None) -> dict:
        """
        GET /ai_sc/monitor/metrics/job

        metric_types可选值：gpu_utilization, kvcache_usage, gpu_mem_used,
                           ttft, tpot, qps（逗号分隔）
        """
        url = f"{self.base_url}/ai_sc/monitor/metrics/job"
        params = {"jobId": job_id, "cluster": cluster}
        if metric_types:
            params["metric_types"] = metric_types
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

