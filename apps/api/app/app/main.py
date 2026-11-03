from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.tenants import router as tenants_router

app = FastAPI(title="SENNA ECL Cloud API", version="0.1.0")
app.include_router(health_router)
app.include_router(tenants_router)
