class Settings:
    PROJECT_NAME: str = "RazorShield AI"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    
    # Risk Thresholds
    ALLOW_THRESHOLD: float = 35.0          # Below 35 -> ALLOW
    CHALLENGE_THRESHOLD: float = 70.0      # 35 to 70 -> STEP UP AUTH
    BLOCK_THRESHOLD: float = 70.0          # 70+ -> BLOCK / RESTRICT
    
    # Financial Cost Parameters (INR)
    AVG_ORDER_VALUE_INR: float = 2400.0
    RTO_REVERSE_LOGISTICS_COST_INR: float = 180.0
    CHARGEBACK_PENALTY_FEE_INR: float = 1200.0
    FALSE_POSITIVE_FRICTION_MARGIN_LOSS_PCT: float = 0.20 # 20% margin lost if genuine customer churns
    
    # Razorpay Webhook Secret (Sandbox simulation)
    RAZORPAY_WEBHOOK_SECRET: str = "rzp_test_secret_razorshield_2026"
    
    # Cryptographic Ledger Salt
    LEDGER_SALT: str = "razorshield_merkle_tamper_evident_salt_2026"


settings = Settings()
