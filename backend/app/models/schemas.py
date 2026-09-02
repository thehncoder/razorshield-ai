from datetime import datetime, timezone
from typing import List, Dict, Optional, Any, Literal
from pydantic import BaseModel, Field


def get_utc_now():
    return datetime.now(timezone.utc)


class CustomerProfile(BaseModel):
    customer_id: str
    name: str
    email: str
    phone: str
    created_at: Optional[datetime] = None
    historical_orders_count: int = 0
    successful_orders_count: int = 0
    rto_count: int = 0
    dispute_count: int = 0


class ShippingAddress(BaseModel):
    line1: str
    line2: Optional[str] = ""
    city: str
    state: str
    pincode: str
    country: str = "IN"


class PaymentDetails(BaseModel):
    payment_method: Literal["upi", "card", "netbanking", "wallet", "cod", "emi"]
    amount: float = Field(..., gt=0, description="Amount in INR")
    currency: str = "INR"
    card_bin: Optional[str] = None
    card_last4: Optional[str] = None
    card_network: Optional[str] = None
    card_type: Optional[str] = None
    upi_vpa: Optional[str] = None
    bank: Optional[str] = None
    vpa_provider: Optional[str] = None


class TelemetryData(BaseModel):
    ip_address: str
    user_agent: str
    device_fingerprint: str
    session_duration_sec: float
    checkout_time_sec: float
    is_vpn_or_proxy: bool = False
    geo_lat: Optional[float] = None
    geo_lon: Optional[float] = None
    geo_city: Optional[str] = None
    geo_state: Optional[str] = None


class TransactionRequest(BaseModel):
    transaction_id: str
    merchant_id: str
    order_id: str
    timestamp: datetime = Field(default_factory=get_utc_now)
    customer: CustomerProfile
    shipping_address: ShippingAddress
    payment: PaymentDetails
    telemetry: TelemetryData
    items_count: int = 1
    items_categories: List[str] = Field(default_factory=list)


class RiskFactor(BaseModel):
    name: str
    category: Literal["entropy", "velocity", "graph_sybil", "behavioral", "reputation", "courier_pincode"]
    impact_score: float = Field(..., description="Contribution to total score (+/-)")
    severity: Literal["low", "medium", "high", "critical"]
    description: str
    evidence: Dict[str, Any] = Field(default_factory=dict)


class ActionRecommendation(BaseModel):
    action: Literal["ALLOW", "CHALLENGE_STEP_UP_AUTH", "BLOCK", "COD_RESTRICTED"]
    confidence: float
    reason: str
    merchant_advisory: str


class RiskEvaluationResponse(BaseModel):
    evaluation_id: str
    transaction_id: str
    timestamp: datetime
    overall_risk_score: float = Field(..., ge=0, le=100, description="0 (safe) to 100 (critical fraud)")
    rto_risk_score: float = Field(..., ge=0, le=100)
    payment_fraud_score: float = Field(..., ge=0, le=100)
    sybil_ring_score: float = Field(..., ge=0, le=100)
    recommendation: ActionRecommendation
    risk_factors: List[RiskFactor]
    explainability_narrative: str
    tamper_proof_hash: str
    latency_ms: float


class DisputeEvent(BaseModel):
    dispute_id: str
    payment_id: str
    order_id: str
    merchant_id: str
    amount: float
    currency: str = "INR"
    reason_code: str  # e.g., "unauthorized_charge", "product_not_received", "fraudulent"
    opened_at: datetime
    respond_by: datetime
    status: Literal["open", "evidence_submitted", "won", "lost", "under_review"] = "open"


class DisputeEvidencePack(BaseModel):
    dossier_id: str
    dispute_id: str
    order_id: str
    generated_at: datetime
    customer_summary: Dict[str, Any]
    transaction_telemetry_proof: Dict[str, Any]
    delivery_pod_proof: Dict[str, Any]
    merchant_invoice_proof: Dict[str, Any]
    rebuttal_letter: str
    compliance_checklist: Dict[str, bool]
    dossier_hash: str
    status: Literal["draft", "ready_for_submission", "submitted"]


class AuditLogEntry(BaseModel):
    index: int
    timestamp: datetime
    event_type: str
    entity_id: str
    event_data: Dict[str, Any]
    previous_hash: str
    current_hash: str
    signature: str


class BenchmarkSummary(BaseModel):
    total_samples: int
    fraud_samples: int
    legitimate_samples: int
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    avg_latency_ms: float
    fraud_loss_prevented_inr: float
    false_positive_friction_cost_inr: float
    net_merchant_savings_inr: float
    confusion_matrix: Dict[str, int]
