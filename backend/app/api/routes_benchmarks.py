import os
import sys
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import BenchmarkSummary

# Add evaluation path
sys.path.insert(0, os.path.abspath("C:/Users/HARSHIT/.gemini/antigravity/scratch/razorshield-ai"))
from evaluation.run_benchmark import run_full_benchmark

router = APIRouter(prefix="/benchmarks", tags=["Evaluation & Benchmarking"])

# Cached benchmark results
cached_benchmark: Dict[str, Any] = {}


@router.post("/run", response_model=BenchmarkSummary)
async def trigger_benchmark_run(
    block_threshold: float = Query(65.0, ge=20.0, le=95.0, description="Risk score threshold to trigger BLOCK")
):
    """
    Executes full test-suite benchmark across 1,000 synthetic Indian FinTech transactions.
    Computes precision, recall, ROC-AUC, latency, and business cost savings.
    """
    try:
        summary = run_full_benchmark(block_threshold=block_threshold)
        cached_benchmark["latest"] = summary.model_dump()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Benchmark execution error: {str(e)}")


@router.get("/latest", response_model=BenchmarkSummary)
async def get_latest_benchmark():
    """Retrieves cached benchmark summary metrics."""
    if "latest" not in cached_benchmark:
        summary = run_full_benchmark()
        cached_benchmark["latest"] = summary.model_dump()
    return cached_benchmark["latest"]


@router.get("/roc-curve-data")
async def get_roc_curve_data():
    """
    Generates ROC & Cost curve points across various risk thresholds (30 to 90)
    for interactive frontend threshold tuning.
    """
    thresholds = [30.0, 40.0, 50.0, 60.0, 65.0, 70.0, 75.0, 80.0, 85.0]
    curve_points = []
    
    for th in thresholds:
        summary = run_full_benchmark(block_threshold=th)
        curve_points.append({
            "threshold": th,
            "precision": summary.precision,
            "recall": summary.recall,
            "f1_score": summary.f1_score,
            "net_savings_inr": summary.net_merchant_savings_inr,
            "false_positives": summary.confusion_matrix["false_positives"],
            "true_positives": summary.confusion_matrix["true_positives"]
        })
        
    return {"points": curve_points}
