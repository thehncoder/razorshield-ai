import pytest
from datetime import datetime, timedelta
from app.models.schemas import DisputeEvent
from app.engine.dispute_agent import AutonomousDisputeAgent
from app.core.security_ledger import CryptographicAuditLedger


def test_dispute_rebuttal_generation():
    agent = AutonomousDisputeAgent()
    disp = DisputeEvent(
        dispute_id="disp_test_001",
        payment_id="pay_test_001",
        order_id="ord_test_001",
        merchant_id="rzp_merch_001",
        amount=2999.0,
        reason_code="unauthorized_transaction",
        opened_at=datetime.utcnow() - timedelta(days=1),
        respond_by=datetime.utcnow() + timedelta(days=6)
    )
    dossier = agent.auto_defend_dispute(disp)
    
    assert dossier.dossier_id.startswith("dossier_")
    assert "FORMAL DISPUTE REBUTTAL" in dossier.rebuttal_letter
    assert "BlueDart Express" in dossier.rebuttal_letter
    assert len(dossier.dossier_hash) == 64  # SHA-256 length
    assert dossier.compliance_checklist["proof_of_delivery_verified"] is True


def test_audit_ledger_cryptographic_integrity():
    ledger = CryptographicAuditLedger(secret_salt="test_salt_123")
    
    # Record 5 events
    for i in range(5):
        ledger.record_event("TEST_EVENT", f"entity_{i}", {"val": i * 100})
    
    # Verify chain integrity
    report = ledger.verify_ledger_integrity()
    assert report["valid"] is True
    assert report["total_blocks"] == 5
    assert len(report["tampered_blocks"]) == 0

    # Simulate malicious tamper in middle block
    ledger.chain[2].event_data["val"] = 999999  # Tampered!
    tamper_report = ledger.verify_ledger_integrity()
    assert tamper_report["valid"] is False
    assert len(tamper_report["tampered_blocks"]) > 0
