from datetime import datetime, timedelta
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from app.models.schemas import DisputeEvent, DisputeEvidencePack
from app.engine.dispute_agent import dispute_agent

router = APIRouter(prefix="/disputes", tags=["Dispute & Chargeback Auto-Defense"])

# In-memory storage for active disputes and generated defense packs
active_disputes: List[Dict[str, Any]] = []

# Seed sample active dispute for live testing
seed_dispute = DisputeEvent(
    dispute_id="disp_rzp_98234710",
    payment_id="pay_K9z2xL81mnQ",
    order_id="order_77192834",
    merchant_id="rzp_mid_blr_demo",
    amount=3499.00,
    currency="INR",
    reason_code="unauthorized_transaction",
    opened_at=datetime.utcnow() - timedelta(days=1),
    respond_by=datetime.utcnow() + timedelta(days=6),
    status="open"
)


@router.post("/webhook", response_model=DisputeEvidencePack)
async def handle_dispute_webhook(dispute: DisputeEvent):
    """
    Ingests Razorpay 'dispute.created' webhook and triggers
    autonomous evidence harvesting and rebuttal dossier generation.
    """
    try:
        evidence_pack = dispute_agent.auto_defend_dispute(dispute)
        record = {
            "dispute": dispute.model_dump(),
            "evidence_pack": evidence_pack.model_dump(),
            "status": "ready_for_submission",
            "created_at": datetime.utcnow().isoformat()
        }
        active_disputes.insert(0, record)
        return evidence_pack
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dispute auto-defense error: {str(e)}")


@router.post("/defend-sample", response_model=DisputeEvidencePack)
async def defend_sample_dispute():
    """Generates an instant bank rebuttal dossier for a sample live dispute."""
    return dispute_agent.auto_defend_dispute(seed_dispute)


@router.get("/all")
async def get_all_disputes():
    """Returns all tracked disputes and compiled defense dossiers."""
    if not active_disputes:
        # Generate initial dossier for sample dispute so UI has data
        pack = dispute_agent.auto_defend_dispute(seed_dispute)
        active_disputes.append({
            "dispute": seed_dispute.model_dump(),
            "evidence_pack": pack.model_dump(),
            "status": "ready_for_submission",
            "created_at": datetime.utcnow().isoformat()
        })
    return active_disputes
