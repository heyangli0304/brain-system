"""
算力适配 - 性能监控
整合自同事的 compute_adapter_service/sdk/monitor.py
支持 Mock 模式（本地测试）和真实算力控制器调用
"""
from typing import Dict, Any, Optional, List, Sequence, Union

USE_MOCK = True

MOCK_CLUSTERS = [
    {
        "control_plane_uuid": "cp-001", "control_plane_name": "SG-ControlPlane",
        "control_plane_status": 1, "cluster_name": "ShaoGuan-DC-A",
        "cluster_type": "ai", "region": "guangdong", "total_node": 4, "total_card": 8,
        "node_metrics_info": [{
            "node_type": "gpu", "node_total_count": 4, "node_available_count": 2,
            "card_info": [{"card_type": "A100-80G", "card_memory": 81920, "card_total_count": 8,
                           "card_available_count": 4, "card_connect_type": "NVLink", "card_connect_speed": 600}],
            "net_info": {"network_type": "RoCE", "nic_speed_gbps": 100},
        }],
    },
    {
        "control_plane_uuid": "cp-002", "control_plane_name": "GZ-ControlPlane",
        "control_plane_status": 1, "cluster_name": "GuangZhou-DC-B",
        "cluster_type": "ai", "region": "guangdong", "total_node": 4, "total_card": 8,
        "node_metrics_info": [{
            "node_type": "gpu", "node_total_count": 4, "node_available_count": 2,
            "card_info": [{"card_type": "A100-80G", "card_memory": 81920, "card_total_count": 8,
                           "card_available_count": 4, "card_connect_type": "NVLink", "card_connect_speed": 600}],
            "net_info": {"network_type": "RoCE", "nic_speed_gbps": 100},
        }],
    },
]


class MonitorClient:

    def __init__(self, base_url: str = "http://算力控制器IP:8001", token: str = ""):
        self.base_url = base_url
        self.headers = {"Authorization": token}

    def get_cluster_overview(self, cluster_names: str = None, region: str = None) -> Dict[str, Any]:
        if USE_MOCK:
            clusters = MOCK_CLUSTERS
            if cluster_names:
                names = [n.strip() for n in cluster_names.split(",")]
                clusters = [c for c in clusters if c["cluster_name"] in names]
            if region:
                clusters = [c for c in clusters if c["region"] == region]
            return {
                "respCode": 0, "respError": "", "respMessage": "success",
                "respBody": {"data": clusters}, "custCode": 0,
            }
        import requests
        url = f"{self.base_url}/ai_sc/resource/cluster/overview"
        params = {}
        if cluster_names:
            params["cluster_names"] = cluster_names
        if region:
            params["region"] = region
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def get_job_metrics(
        self, job_id: int, cluster: str = None,
        metric_types: Union[str, Sequence[str]] = None,
        start_time: str = None, end_time: str = None,
    ) -> Dict[str, Any]:
        if USE_MOCK:
            return {
                "respCode": 0, "respError": "", "respMessage": "success",
                "respBody": {
                    "jobId": job_id,
                    "metrics": [
                        {"metric_types": "ttft", "unit": "ms", "timestamp": 0,
                         "value_current": 150.0, "value_mean": 145.0, "value_max": 200.0},
                        {"metric_types": "tpot", "unit": "ms", "timestamp": 0,
                         "value_current": 20.0, "value_mean": 18.0, "value_max": 25.0},
                        {"metric_types": "gpu_utilization", "unit": "%", "timestamp": 0,
                         "value_current": 80.0, "value_mean": 75.0, "value_max": 95.0},
                        {"metric_types": "kvcache_usage", "unit": "%", "timestamp": 0,
                         "value_current": 50.0, "value_mean": 45.0, "value_max": 70.0},
                    ],
                },
                "custCode": 0,
            }
        import requests
        url = f"{self.base_url}/ai_sc/adapter/getPDJobMonitorMetrics"
        params = {"jobId": job_id}
        if cluster:
            params["cluster"] = cluster
        if metric_types:
            params["metricTypes"] = metric_types
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()
