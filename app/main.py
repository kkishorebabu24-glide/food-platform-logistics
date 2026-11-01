from fastapi import FastAPI

from app.api.routes.admin import router as admin_router
from app.api.routes.analytics import router as analytics_router
from app.api.routes.auth import router as auth_router
from app.api.routes.batches import router as batches_router
from app.api.routes.orders import router as orders_router
from app.api.routes.pickups import router as pickups_router

app = FastAPI(
    title="Food Platform Logistics",
    version="0.1.0",
    description="Order queue, fulfillment, batch coordination, pickup verification, and analytics layer for the society food platform.",
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(orders_router, prefix="/api/v1")
app.include_router(batches_router, prefix="/api/v1")
app.include_router(pickups_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "service": "food-platform-logistics"}
