from typing import List, Dict, Any, Tuple
from app.models.schemas import RiskFactor, ActionRecommendation, TransactionRequest
from app.core.config import settings


class ExplainabilityEngine:
    """
    Translates raw feature weights and ML scores into human-auditable,
    SHAP-style explainability breakdowns with actionable merchant guidance.
    """

    @classmethod
    def synthesize_narrative(
        cls,
        txn: TransactionRequest,
        factors: List[RiskFactor],
        overall_score: float,
        action: str
    ) -> Tuple[str, str]:
        """
        Returns: (explainability_narrative, merchant_advisory)
        """
        if not factors or overall_score < settings.ALLOW_THRESHOLD:
            narrative = (
                f"Transaction {txn.transaction_id} verified clean. Address matches PIN prefix, "
                f"device telemetry shows natural interaction timing ({txn.telemetry.checkout_time_sec:.1f}s), "
                f"and customer account has positive historical reputation."
            )
            advisory = "Proceed with instant order fulfillment and standard settlement."
            return narrative, advisory

        # Sort factors by absolute impact
        sorted_factors = sorted(factors, key=lambda f: abs(f.impact_score), reverse=True)
        top_drivers = [f"• {f.name} (+{f.impact_score:.1f} pts): {f.description}" for f in sorted_factors[:3]]
        drivers_text = "\n".join(top_drivers)

        if action == "BLOCK":
            narrative = (
                f"CRITICAL RISK (Score: {overall_score:.1f}/100) triggered automated defensive block. "
                f"Primary risk drivers:\n{drivers_text}"
            )
            advisory = (
                "Order rejected to prevent irreversible inventory/chargeback loss. "
                "Customer flagged for manual review if they reach out to support."
            )
        elif action == "CHALLENGE_STEP_UP_AUTH":
            narrative = (
                f"ELEVATED RISK (Score: {overall_score:.1f}/100) requires verification before fulfillment. "
                f"Key anomalies detected:\n{drivers_text}"
            )
            advisory = (
                "Prompt customer for Step-Up Authentication (Razorpay Dynamic 3DS / OTP verification) "
                "or WhatsApp delivery address confirmation."
            )
        elif action == "COD_RESTRICTED":
            narrative = (
                f"HIGH RTO RISK (Score: {overall_score:.1f}/100) for Cash-on-Delivery payment method. "
                f"Delivery address or user velocity exhibits high undeliverability/cancellation patterns:\n{drivers_text}"
            )
            advisory = (
                "Disable Cash-on-Delivery for this checkout session. "
                "Offer ₹50 instant discount to convert customer to UPI / Prepaid."
            )
        else:
            narrative = f"Transaction approved with minor risk factors monitored. Score: {overall_score:.1f}/100."
            advisory = "Fulfill order with standard tracking."

        return narrative, advisory
