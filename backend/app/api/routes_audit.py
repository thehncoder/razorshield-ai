from typing import List, Dict, Any
from fastapi import APIRouter
from app.models.schemas import AuditLogEntry
from app.core.security_ledger import audit_ledger

router = APIRouter(prefix="/audit", tags=["Cryptographic Audit Ledger"])


@router.get("/ledger", response_model=List[AuditLogEntry])
async def get_audit_ledger_entries(limit: int = 100):
    """
    Returns immutable SHA-256 cryptographically linked audit ledger entries.
    Provides verifiable proof for all risk decisions and dispute responses.
    """
    return audit_ledger.get_entries(limit=limit)


@router.get("/verify")
async def verify_ledger_integrity():
    """
    Cryptographic verification endpoint: Walks the entire hash chain
    and verifies SHA-256 links and HMAC signatures for non-tampering.
    """
    return audit_ledger.verify_ledger_integrity()
