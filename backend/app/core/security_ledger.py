import hashlib
import hmac
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.models.schemas import AuditLogEntry


class CryptographicAuditLedger:
    """
    Tamper-evident, cryptographically chained audit ledger.
    Every risk evaluation, policy override, and dispute dossier generation
    is immutably recorded with SHA-256 hash-chaining and HMAC signatures.
    """
    def __init__(self, secret_salt: str = settings.LEDGER_SALT):
        self.secret_salt = secret_salt.encode("utf-8")
        self.chain: List[AuditLogEntry] = []
        self._genesis_hash = hashlib.sha256(b"RAZORSHIELD_GENESIS_BLOCK_2026").hexdigest()

    @property
    def latest_hash(self) -> str:
        if not self.chain:
            return self._genesis_hash
        return self.chain[-1].current_hash

    def _compute_hash(self, index: int, timestamp_str: str, event_type: str, entity_id: str, event_data: Dict[str, Any], prev_hash: str) -> str:
        serialized_data = json.dumps(event_data, sort_keys=True)
        payload = f"{index}:{timestamp_str}:{event_type}:{entity_id}:{serialized_data}:{prev_hash}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def _compute_signature(self, current_hash: str) -> str:
        return hmac.new(self.secret_salt, current_hash.encode("utf-8"), hashlib.sha256).hexdigest()

    def record_event(self, event_type: str, entity_id: str, event_data: Dict[str, Any]) -> AuditLogEntry:
        index = len(self.chain)
        timestamp = datetime.utcnow()
        timestamp_str = timestamp.isoformat()
        prev_hash = self.latest_hash
        
        current_hash = self._compute_hash(index, timestamp_str, event_type, entity_id, event_data, prev_hash)
        signature = self._compute_signature(current_hash)
        
        entry = AuditLogEntry(
            index=index,
            timestamp=timestamp,
            event_type=event_type,
            entity_id=entity_id,
            event_data=event_data,
            previous_hash=prev_hash,
            current_hash=current_hash,
            signature=signature
        )
        self.chain.append(entry)
        return entry

    def verify_ledger_integrity(self) -> Dict[str, Any]:
        """
        Walks the entire chain to prove cryptographic non-tampering.
        Returns validation status, block count, and any corrupted blocks.
        """
        if not self.chain:
            return {
                "valid": True,
                "total_blocks": 0,
                "genesis_hash": self._genesis_hash,
                "latest_hash": self._genesis_hash,
                "tampered_blocks": []
            }

        tampered_blocks = []
        expected_prev_hash = self._genesis_hash

        for i, entry in enumerate(self.chain):
            if entry.previous_hash != expected_prev_hash:
                tampered_blocks.append({"index": i, "reason": "Previous hash mismatch"})
            
            recomputed_hash = self._compute_hash(
                entry.index,
                entry.timestamp.isoformat(),
                entry.event_type,
                entry.entity_id,
                entry.event_data,
                entry.previous_hash
            )
            if entry.current_hash != recomputed_hash:
                tampered_blocks.append({"index": i, "reason": "Current hash mismatch (data altered)"})
                
            recomputed_sig = self._compute_signature(entry.current_hash)
            if entry.signature != recomputed_sig:
                tampered_blocks.append({"index": i, "reason": "HMAC signature mismatch"})
                
            expected_prev_hash = entry.current_hash

        return {
            "valid": len(tampered_blocks) == 0,
            "total_blocks": len(self.chain),
            "genesis_hash": self._genesis_hash,
            "latest_hash": self.latest_hash,
            "tampered_blocks": tampered_blocks
        }

    def get_entries(self, limit: int = 100) -> List[AuditLogEntry]:
        return list(reversed(self.chain[-limit:]))


# Global singleton instance
audit_ledger = CryptographicAuditLedger()
