import pytest
from app.models.schemas import TransactionRequest, CustomerProfile, ShippingAddress, PaymentDetails, TelemetryData
from app.engine.velocity_engine import VelocityTracker
from app.engine.graph_sentinel import SybilGraphSentinel


def create_dummy_txn(txn_id, cust_id, dev_fp, ip, checkout_sec=10.0):
    return TransactionRequest(
        transaction_id=txn_id,
        merchant_id="rzp_mid_test",
        order_id=f"ord_{txn_id}",
        customer=CustomerProfile(
            customer_id=cust_id,
            name="Test Customer",
            email=f"{cust_id}@gmail.com",
            phone="+91 9845012345"
        ),
        shipping_address=ShippingAddress(
            line1="123 MG Road",
            city="Bengaluru",
            state="Karnataka",
            pincode="560001",
            country="IN"
        ),
        payment=PaymentDetails(
            payment_method="card",
            amount=1500.0,
            currency="INR",
            card_bin="411111",
            card_last4="1234"
        ),
        telemetry=TelemetryData(
            ip_address=ip,
            user_agent="Mozilla/5.0",
            device_fingerprint=dev_fp,
            session_duration_sec=60.0,
            checkout_time_sec=checkout_sec,
            is_vpn_or_proxy=False
        )
    )


def test_sub_second_bot_velocity():
    tracker = VelocityTracker()
    txn = create_dummy_txn("txn_bot_01", "cust_01", "dev_01", "103.12.1.1", checkout_sec=0.45)
    factors = tracker.record_and_evaluate(txn)
    bot_factors = [f for f in factors if "Sub-Human" in f.name]
    assert len(bot_factors) == 1
    assert bot_factors[0].severity == "high"


def test_device_multi_account_hopping():
    tracker = VelocityTracker()
    shared_device = "fingerprint_sybil_device_abc"
    
    # 3 transactions from different customers on same device
    for i in range(3):
        txn = create_dummy_txn(f"txn_{i}", f"cust_{i}", shared_device, f"103.12.1.{i}")
        factors = tracker.record_and_evaluate(txn)
    
    hopping_factors = [f for f in factors if f.name == "Device Multi-Account Hopping"]
    assert len(hopping_factors) == 1
    assert hopping_factors[0].severity == "critical"


def test_sybil_graph_clustering():
    sentinel = SybilGraphSentinel()
    shared_dev = "dev_ring_leader"
    
    # Connect 4 accounts to the same device
    for i in range(4):
        txn = create_dummy_txn(f"txn_g_{i}", f"cust_g_{i}", shared_dev, f"192.168.1.{i}")
        factors = sentinel.add_and_evaluate_transaction(txn)
    
    ring_factors = [f for f in factors if "Sybil Abuse-Ring" in f.name]
    assert len(ring_factors) == 1
    assert ring_factors[0].evidence["linked_accounts_count"] >= 3
