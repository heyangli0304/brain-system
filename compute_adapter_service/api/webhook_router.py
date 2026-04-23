"""
算力南向适配服务 - Webhook通知接收
文件位置：compute_adapter_service/api/webhook_router.py
接收真实算力控制器发来的 OOM、状态变更等异步通知
脏数据不上浮：清洗过滤成标准格式，再往上报给大管家
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any

router = APIRouter()


class WebhookEvent(BaseModel):
    event_type: str
    event_data: Dict[str, Any]
    timestamp: Optional[int] = None


class JobStatusChangeData(BaseModel):
    job_id: int
    cluster: str
    old_status: str
    new_status: str
    reason: Optional[str] = None


class ResourceAlarmData(BaseModel):
    cluster_name: str
    alarm_type: str
    alarm_level: str
    message: str
    current_value: Optional[float] = None
    threshold: Optional[float] = None


job_status_store: Dict[int, Dict[str, Any]] = {}
pending_notifications: list = []


@router.post("/webhook/status_update")
def receive_status_update(event: WebhookEvent):
    event_type = event.event_type

    if event_type == "JOB_STATUS_CHANGE":
        data = event.event_data
        job_id = data.get("job_id")
        new_status = data.get("new_status")

        if job_id:
            job_status_store[job_id] = {
                "status": new_status,
                "cluster": data.get("cluster", ""),
                "reason": data.get("reason", ""),
                "updated_at": event.timestamp,
            }

        pending_notifications.append({
            "type": "JOB_STATUS_CHANGE",
            "job_id": job_id,
            "new_status": new_status,
            "cluster": data.get("cluster", ""),
        })

        return {"status": "received", "event": "JOB_STATUS_CHANGE", "job_id": job_id, "new_status": new_status}

    elif event_type == "RESOURCE_ALARM":
        data = event.event_data
        pending_notifications.append({
            "type": "RESOURCE_ALARM",
            "cluster": data.get("cluster_name", ""),
            "alarm_type": data.get("alarm_type", ""),
            "alarm_level": data.get("alarm_level", ""),
        })

        return {"status": "received", "event": "RESOURCE_ALARM", "cluster": data.get("cluster_name", "")}

    return {"status": "received", "event": event_type}


@router.get("/webhook/job_status/{job_id}")
def get_job_status(job_id: int):
    if job_id in job_status_store:
        return {"job_id": job_id, **job_status_store[job_id]}
    return {"job_id": job_id, "status": "unknown", "message": "未收到该作业的状态变更通知"}


@router.get("/webhook/notifications")
def get_pending_notifications():
    notifications = pending_notifications.copy()
    pending_notifications.clear()
    return {"count": len(notifications), "notifications": notifications}
