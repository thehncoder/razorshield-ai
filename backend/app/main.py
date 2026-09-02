from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes_transactions import router as transactions_router
from app.api.routes_disputes import router as disputes_router
from app.api.routes_benchmarks import router as benchmarks_router
from app.api.routes_audit import router as audit_router

app = FastAPI(
    title="RazorShield AI — Autonomous FinTech Risk Sentinel & Chargeback Defense Engine",
    description="Built for Razorpay AI Buildathon 2026 (Track 02: AI Risk Manager). Defense-First Explainable AI Risk & Dispute Auto-Responder.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(transactions_router, prefix=settings.API_PREFIX)
app.include_router(disputes_router, prefix=settings.API_PREFIX)
app.include_router(benchmarks_router, prefix=settings.API_PREFIX)
app.include_router(audit_router, prefix=settings.API_PREFIX)


@app.get("/")
async def root_healthcheck():
    return {
        "system": "RazorShield AI",
        "status": "OPERATIONAL",
        "track": "Track 02: AI Risk Manager",
        "buildathon": "Razorpay AI Buildathon 2026",
        "api_docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
