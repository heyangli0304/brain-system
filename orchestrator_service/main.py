from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import orchestrator_router
from adapters.network.api import actn_router
from adapters.compute.api import compute_router

app = FastAPI(
    title="算网大脑编排服务",
    description="核心编排服务（大管家/算网中枢）- 管控光网南向适配 + 算力南向适配",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(orchestrator_router.router, prefix="/api/v1/orchestrator", tags=["编排服务 - 北向接口"])
app.include_router(actn_router.router, prefix="/api/v1/actn", tags=["光网南向适配 - ACTN接口"])
app.include_router(compute_router.router, prefix="/api/v1/compute", tags=["算力南向适配 - 算力接口"])

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "orchestrator"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
