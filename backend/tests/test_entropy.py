import pytest
from app.models.schemas import ShippingAddress, CustomerProfile
from app.engine.entropy_analyzer import EntropyRiskAnalyzer, detect_gibberish, calculate_shannon_entropy


def test_address_gibberish_detection():
    # Test obvious keyboard smash
    is_gib, conf, reason = detect_gibberish("asdfghjkl qwerty 12345")
    assert is_gib is True
    assert conf >= 0.75

    # Test clean realistic address
    is_gib, conf, reason = detect_gibberish("Flat 402, Royal Palms Apartment, Indiranagar 100ft Road")
    assert is_gib is False


def test_pincode_state_mismatch():
    addr = ShippingAddress(
        line1="12th Main Road, Koramangala",
        city="Bengaluru",
        state="Karnataka",
        pincode="110001",  # Delhi PIN code
        country="IN"
    )
    factors = EntropyRiskAnalyzer.analyze_shipping_address(addr)
    mismatch_factors = [f for f in factors if f.name == "PIN Code & State Mismatch"]
    assert len(mismatch_factors) == 1
    assert mismatch_factors[0].severity == "high"


def test_disposable_email_detection():
    cust = CustomerProfile(
        customer_id="cust_test_01",
        name="Test User",
        email="bot_user_99@mailinator.com",
        phone="+91 9845012345"
    )
    factors = EntropyRiskAnalyzer.analyze_customer_identity(cust)
    disposable_factors = [f for f in factors if f.name == "Disposable Email Domain Detected"]
    assert len(disposable_factors) == 1
    assert disposable_factors[0].severity == "critical"


def test_fake_phone_detection():
    cust = CustomerProfile(
        customer_id="cust_test_02",
        name="Test User",
        email="genuine.user@gmail.com",
        phone="9999999999"
    )
    factors = EntropyRiskAnalyzer.analyze_customer_identity(cust)
    phone_factors = [f for f in factors if f.name == "Fake / Repetitive Phone Number"]
    assert len(phone_factors) == 1
