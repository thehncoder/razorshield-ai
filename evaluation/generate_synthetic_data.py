import json
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any

INDIAN_CITIES_STATES = [
    ("Bengaluru", "Karnataka", "560001", "560038", "560100"),
    ("Mumbai", "Maharashtra", "400001", "400050", "400099"),
    ("Delhi", "Delhi", "110001", "110020", "110092"),
    ("Hyderabad", "Telangana", "500001", "500034", "500081"),
    ("Chennai", "Tamil Nadu", "600001", "600028", "600100"),
    ("Kolkata", "West Bengal", "700001", "700020", "700091"),
    ("Pune", "Maharashtra", "411001", "411014", "411045"),
    ("Ahmedabad", "Gujarat", "380001", "380015", "380054"),
    ("Jaipur", "Rajasthan", "302001", "302015", "302020"),
    ("Lucknow", "Uttar Pradesh", "226001", "226010", "226024"),
]

FIRST_NAMES = ["Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan", "Krishna", "Ishaan", "Ananya", "Diya", "Pari", "Aditi", "Riya", "Sneha", "Kavya", "Pooja", "Priya", "Meera", "Rohan", "Vikram", "Neha", "Rahul", "Siddharth"]
LAST_NAMES = ["Sharma", "Verma", "Patel", "Reddy", "Iyer", "Nair", "Gupta", "Kumar", "Singh", "Joshi", "Bose", "Mehta", "Rao", "Das", "Choudhury", "Bhat", "Mishra", "Agarwal"]

DISPOSABLE_DOMAINS = ["mailinator.com", "tempmail.com", "10minutemail.com", "guerrillamail.com", "fakemailgenerator.com"]
VALID_DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "icloud.com", "rediffmail.com"]


def generate_synthetic_dataset(num_samples: int = 1000, fraud_ratio: float = 0.22) -> List[Dict[str, Any]]:
    random.seed(42)
    records = []

    num_fraud = int(num_samples * fraud_ratio)
    num_legit = num_samples - num_fraud

    # Shared device/IP pools for Sybil rings and Bot attacks
    sybil_device_pool = [f"dev_sybil_ring_{i}" for i in range(5)]
    sybil_ip_pool = ["103.45.12.89", "103.45.12.90", "103.45.12.91"]
    bot_ip = "185.220.101.5" # Tor exit node style

    # 1. Generate Legitimate Transactions
    for i in range(num_legit):
        city, state, *pins = random.choice(INDIAN_CITIES_STATES)
        first, last = random.choice(FIRST_NAMES), random.choice(LAST_NAMES)
        name = f"{first} {last}"
        email = f"{first.lower()}.{last.lower()}{random.randint(10, 999)}@{random.choice(VALID_DOMAINS)}"
        phone = f"+91 {random.choice(['98', '97', '99', '91', '88', '77'])}{random.randint(10000000, 99999999)}"
        pincode = random.choice(pins)
        
        hist_orders = random.randint(1, 15)
        success_orders = max(1, hist_orders - random.choice([0, 0, 0, 1]))
        rto_count = 0 if random.random() > 0.1 else 1

        rec = {
            "transaction_id": f"txn_legit_{i:04d}",
            "merchant_id": "rzp_mid_demo_merch",
            "order_id": f"ord_legit_{i:04d}",
            "customer": {
                "customer_id": f"cust_legit_{i:04d}",
                "name": name,
                "email": email,
                "phone": phone,
                "historical_orders_count": hist_orders,
                "successful_orders_count": success_orders,
                "rto_count": rto_count,
                "dispute_count": 0
            },
            "shipping_address": {
                "line1": f"Flat #{random.randint(101, 804)}, Sector {random.randint(1, 45)}, Road #{random.randint(1, 12)}",
                "line2": f"Near {random.choice(['Metro Station', 'Apollo Hospital', 'City Mall', 'Central Park', 'Temple'])}",
                "city": city,
                "state": state,
                "pincode": pincode,
                "country": "IN"
            },
            "payment": {
                "payment_method": random.choice(["upi", "card", "netbanking", "cod"]),
                "amount": round(random.uniform(499.0, 8999.0), 2),
                "currency": "INR",
                "card_bin": "411111" if random.random() > 0.5 else "524128",
                "card_last4": f"{random.randint(1000, 9999)}",
                "upi_vpa": f"{first.lower()}@okhdfcbank"
            },
            "telemetry": {
                "ip_address": f"{random.randint(49, 150)}.{random.randint(10, 200)}.{random.randint(1, 250)}.{random.randint(1, 250)}",
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "device_fingerprint": f"fp_legit_{uuid.uuid4().hex[:10]}",
                "session_duration_sec": round(random.uniform(45.0, 360.0), 1),
                "checkout_time_sec": round(random.uniform(6.0, 45.0), 1),
                "is_vpn_or_proxy": False,
                "geo_city": city,
                "geo_state": state
            },
            "ground_truth_is_fraud": False,
            "fraud_type": "none"
        }
        records.append(rec)

    # 2. Generate Fraudulent Transactions (Multi-vector)
    fraud_types = ["rto_entropy_abuse", "card_testing_bot", "sybil_fraud_ring", "mismatched_geo_spoof"]
    
    for i in range(num_fraud):
        ftype = random.choice(fraud_types)
        city, state, *pins = random.choice(INDIAN_CITIES_STATES)
        first, last = random.choice(FIRST_NAMES), random.choice(LAST_NAMES)
        
        if ftype == "rto_entropy_abuse":
            # Gibberish address, fake phone, disposable email, COD payment
            gibberish_lines = ["asdfghjk qwerty 123", "street nowhere zzzxxx", "hno 0000 test road fake", "kjsdhfkjshdf kjshdf"]
            line1 = random.choice(gibberish_lines)
            pincode = "999999" if random.random() > 0.5 else random.choice(pins)
            email = f"user_{uuid.uuid4().hex[:8]}@{random.choice(DISPOSABLE_DOMAINS)}"
            phone = "9999999999" if random.random() > 0.5 else "9876543210"
            pay_method = "cod"
            checkout_sec = random.uniform(3.0, 8.0)
            is_vpn = False
            dev_fp = f"fp_rto_{uuid.uuid4().hex[:8]}"
            ip_addr = "103.22.44.11"

        elif ftype == "card_testing_bot":
            # Sub-second checkout, VPN proxy, rapid card retries
            line1 = f"Flat {random.randint(1, 20)}, Main Street"
            pincode = random.choice(pins)
            email = f"bot_{random.randint(100, 999)}@gmail.com"
            phone = f"+91 91{random.randint(10000000, 99999999)}"
            pay_method = "card"
            checkout_sec = round(random.uniform(0.2, 0.9), 2) # Sub-second bot!
            is_vpn = True
            dev_fp = "fp_bot_card_tester_01"
            ip_addr = bot_ip

        elif ftype == "sybil_fraud_ring":
            # Coordinated accounts sharing same device & IP pool
            line1 = f"Plot #{random.randint(10, 50)}, Ring Colony"
            pincode = random.choice(pins)
            email = f"sybil_{i}_{random.randint(10, 99)}@mailinator.com"
            phone = f"+91 97{random.randint(10000000, 99999999)}"
            pay_method = random.choice(["upi", "card"])
            checkout_sec = round(random.uniform(2.0, 5.0), 1)
            is_vpn = random.random() > 0.5
            dev_fp = random.choice(sybil_device_pool)
            ip_addr = random.choice(sybil_ip_pool)

        else: # mismatched_geo_spoof
            # PIN code belongs to Delhi (110001) but entered state is Karnataka
            line1 = "12th Cross, Indiranagar"
            pincode = "110001" # Delhi pin in Bangalore address
            state = "Karnataka"
            city = "Bengaluru"
            email = f"spoofed_{i}@tempmail.com"
            phone = f"+91 88{random.randint(10000000, 99999999)}"
            pay_method = "cod"
            checkout_sec = round(random.uniform(4.0, 10.0), 1)
            is_vpn = True
            dev_fp = f"fp_spoof_{uuid.uuid4().hex[:8]}"
            ip_addr = "194.26.29.112"

        rec = {
            "transaction_id": f"txn_fraud_{i:04d}",
            "merchant_id": "rzp_mid_demo_merch",
            "order_id": f"ord_fraud_{i:04d}",
            "customer": {
                "customer_id": f"cust_fraud_{i:04d}",
                "name": f"{first} {last}",
                "email": email,
                "phone": phone,
                "historical_orders_count": random.randint(0, 2),
                "successful_orders_count": 0,
                "rto_count": random.choice([1, 2, 3]) if ftype == "rto_entropy_abuse" else 0,
                "dispute_count": 1 if random.random() > 0.6 else 0
            },
            "shipping_address": {
                "line1": line1,
                "line2": "Opposite Sector Complex",
                "city": city,
                "state": state,
                "pincode": pincode,
                "country": "IN"
            },
            "payment": {
                "payment_method": pay_method,
                "amount": round(random.uniform(1200.0, 14999.0), 2),
                "currency": "INR",
                "card_bin": "411111",
                "card_last4": f"{random.randint(1000, 9999)}",
                "upi_vpa": "fraud_tester@upi"
            },
            "telemetry": {
                "ip_address": ip_addr,
                "user_agent": "Python-urllib/3.10" if ftype == "card_testing_bot" else "Mozilla/5.0",
                "device_fingerprint": dev_fp,
                "session_duration_sec": round(random.uniform(2.0, 20.0), 1),
                "checkout_time_sec": checkout_sec,
                "is_vpn_or_proxy": is_vpn,
                "geo_city": city,
                "geo_state": state
            },
            "ground_truth_is_fraud": True,
            "fraud_type": ftype
        }
        records.append(rec)

    random.shuffle(records)
    return records


if __name__ == "__main__":
    data = generate_synthetic_dataset(1000, 0.22)
    with open("C:/Users/HARSHIT/.gemini/antigravity/scratch/razorshield-ai/backend/data/benchmark_dataset.json", "w") as f:
        json.dump(data, f, indent=2)
    print(f"Successfully generated {len(data)} synthetic Indian FinTech transactions.")
