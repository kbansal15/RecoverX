"""
Main FastAPI Application Entrypoint.
RecoverX - Autonomous AI Revenue Recovery Agent.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.services.demo_seed import seed_demo_data
from app.models.entities import Merchant

# Import all API routers
from app.routers import (
    auth, dashboard, recovery_cases, dropoffs, mandates,
    invoices, promise_to_pay, voice, evaluation, webhooks, policy, audit
)

# Ensure tables exist at module load
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure demo merchant data is seeded
    db = SessionLocal()
    try:
        demo_merchant = db.query(Merchant).first()
        if not demo_merchant:
            print("[Startup] Seeding initial canonical demo data...")
            seed_demo_data(db)
            print("[Startup] Demo data initialized.")
    finally:
        db.close()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(dashboard.router, prefix=settings.API_PREFIX)
app.include_router(recovery_cases.router, prefix=settings.API_PREFIX)
app.include_router(dropoffs.router, prefix=settings.API_PREFIX)
app.include_router(mandates.router, prefix=settings.API_PREFIX)
app.include_router(invoices.router, prefix=settings.API_PREFIX)
app.include_router(promise_to_pay.router, prefix=settings.API_PREFIX)
app.include_router(voice.router, prefix=settings.API_PREFIX)
app.include_router(evaluation.router, prefix=settings.API_PREFIX)
app.include_router(webhooks.router, prefix=settings.API_PREFIX)
app.include_router(policy.router, prefix=settings.API_PREFIX)
app.include_router(audit.router, prefix=settings.API_PREFIX)

@app.get("/")
def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs_url": "/docs",
        "mode": "RAZORPAY_TEST_MODE"
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "razorpay_mode": "TEST_MODE"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
