"""
算力南向适配服务 - 服务入口
文件位置：compute_adapter_service/main.py
暴露 8001 端口，挂载内部接口和Webhook通知接口
"""

from fastapi import FastAPI
from api.internal_router import router as internal_router
from api.webhook_router import router as webhook_router

app = FastAPI(title="算力南向适配服务", version="1.0")

app.include_router(internal_router, prefix="/api/v1/compute", tags=["大管家内部接口"])
app.include_router(webhook_router, prefix="/api/v1/notification", tags=["算力控制器异步通知"])


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "compute_adapter_service", "port": 8001}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
