import time
import uuid
from datetime import datetime
from typing import List, Dict, Any
from app.models.schemas import (
    TransactionRequest, RiskEvaluationResponse,
    RiskFactor, ActionRecommendation
)
from app.core.config import settings
from app.core.security_ledger import audit_ledger
from app.engine.entropy_analyzer import EntropyRiskAnalyzer
from app.engine.velocity_engine import velocity_engine
from app.engine.graph_sentinel import graph_sentinel
from app.engine.explainability import ExplainabilityEngine


class RazorShieldRiskClassifier:
    """
    Production-grade multi-vector risk engine combining address entropy,
    behavioral velocity, graph abuse-ring detection, and historical reputation.
    """

    def evaluate_transaction(self, txn: TransactionRequest) -> RiskEvaluationResponse:
        start_time = time.perf_counter()
        evaluation_id = f"eval_{uuid.uuid4().hex[:12]}"
        
        all_factors: List[RiskFactor] = []

        # 1. Address & PIN Entropy Analysis
        addr_factors = EntropyRiskAnalyzer.analyze_shipping_address(txn.shipping_address)
        all_factors.extend(addr_factors)

        # 2. Customer Identity Entropy & Reputation
        id_factors = EntropyRiskAnalyzer.analyze_customer_identity(txn.customer)
        all_factors.extend(id_factors)

        # 3. Behavioral Velocity & Latency
        vel_factors = velocity_engine.record_and_evaluate(txn)
        all_factors.extend(vel_factors)

        # 4. Graph Abuse Ring Detection
        graph_factors = graph_sentinel.add_and_evaluate_transaction(txn)
        all_factors.extend(graph_factors)

        # 5. Customer Historical Reputation Credit / Penalty
        cust = txn.customer
        if cust.historical_orders_count > 0:
            success_rate = cust.successful_orders_count / cust.historical_orders_count
            if success_rate > 0.8 and cust.historical_orders_count >= 3 and cust.rto_count == 0:
                all_factors.append(RiskFactor(
                    name="Verified Customer Trust History",
                    category="reputation",
                    impact_score=-20.0,
                    severity="low",
                    description=f"Loyal customer with {cust.successful_orders_count} successful orders and 0 RTOs",
                    evidence={"success_rate": success_rate, "past_orders": cust.successful_orders_count}
                ))
            elif cust.rto_count >= 2:
                all_factors.append(RiskFactor(
                    name="Serial RTO / Return History",
                    category="reputation",
                    impact_score=30.0,
                    severity="high",
                    description=f"Customer account has {cust.rto_count} past Return-To-Origin incidents",
                    evidence={"past_rtos": cust.rto_count}
                ))

        # Separate component scores
        rto_component = sum(f.impact_score for f in all_factors if f.category in ("entropy", "courier_pincode", "reputation") and f.impact_score > 0)
        fraud_component = sum(f.impact_score for f in all_factors if f.category in ("velocity", "behavioral", "reputation") and f.impact_score > 0)
        sybil_component = sum(f.impact_score for f in all_factors if f.category == "graph_sybil" and f.impact_score > 0)
        trust_credit = sum(f.impact_score for f in all_factors if f.impact_score < 0)

        # Normalization to 0 - 100 bounded scale
        rto_risk_score = min(100.0, max(0.0, rto_component + (trust_credit * 0.5)))
        payment_fraud_score = min(100.0, max(0.0, fraud_component + (trust_credit * 0.5)))
        sybil_ring_score = min(100.0, max(0.0, sybil_component))

        # Overall composite score with weighted blend
        base_composite = (rto_risk_score * 0.35) + (payment_fraud_score * 0.40) + (sybil_ring_score * 0.25)
        overall_risk_score = round(min(100.0, max(0.0, base_composite)), 1)

        # Policy Decision Gating
        if overall_risk_score >= settings.BLOCK_THRESHOLD or sybil_ring_score >= 40:
            action = "BLOCK"
            confidence = min(0.98, 0.75 + (overall_risk_score / 400))
            reason = "High probability of malicious fraud or syndicate attack."
        elif txn.payment.payment_method == "cod" and rto_risk_score >= 45:
            action = "COD_RESTRICTED"
            confidence = 0.88
            reason = "High RTO delivery failure risk for Cash-on-Delivery."
        elif overall_risk_score >= settings.ALLOW_THRESHOLD:
            action = "CHALLENGE_STEP_UP_AUTH"
            confidence = 0.82
            reason = "Moderate risk factors detected; requires secondary authorization."
        else:
            action = "ALLOW"
            confidence = 0.94
            reason = "Transaction within verified safe parameters."

        narrative, advisory = ExplainabilityEngine.synthesize_narrative(
            txn=txn,
            factors=all_factors,
            overall_score=overall_risk_score,
            action=action
        )

        recommendation = ActionRecommendation(
            action=action,
            confidence=confidence,
            reason=reason,
            merchant_advisory=advisory
        )

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        
        # Record into Tamper-Proof Cryptographic Ledger
        audit_entry = audit_ledger.record_event(
            event_type="TRANSACTION_RISK_EVALUATION",
            entity_id=txn.transaction_id,
            event_data={
                "evaluation_id": evaluation_id,
                "overall_risk_score": overall_risk_score,
                "action": action,
                "rto_score": rto_risk_score,
                "fraud_score": payment_fraud_score,
                "sybil_score": sybil_ring_score,
                "factors_count": len(all_factors)
            }
        )

        return RiskEvaluationResponse(
            evaluation_id=evaluation_id,
            transaction_id=txn.transaction_id,
            timestamp=datetime.utcnow(),
            overall_risk_score=overall_risk_score,
            rto_risk_score=round(rto_risk_score, 1),
            payment_fraud_score=round(payment_fraud_score, 1),
            sybil_ring_score=round(sybil_ring_score, 1),
            recommendation=recommendation,
            risk_factors=all_factors,
            explainability_narrative=narrative,
            tamper_proof_hash=audit_entry.current_hash,
            latency_ms=elapsed_ms
        )


# Global singleton instance
risk_classifier = RazorShieldRiskClassifier()
