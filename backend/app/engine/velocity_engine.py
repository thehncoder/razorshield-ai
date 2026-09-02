import time
from collections import defaultdict
from typing import List, Dict, Tuple
from app.models.schemas import TransactionRequest, RiskFactor


class VelocityTracker:
    """
    In-memory sliding window velocity tracker for real-time transaction streams.
    Tracks IP velocity, device fingerprint velocity, card testing attempts, and bot latency.
    """
    def __init__(self, window_seconds: int = 300): # 5-minute sliding window
        self.window_seconds = window_seconds
        self.ip_events: Dict[str, List[float]] = defaultdict(list)
        self.device_events: Dict[str, List[float]] = defaultdict(list)
        self.device_accounts: Dict[str, set] = defaultdict(set)
        self.card_events: Dict[str, List[float]] = defaultdict(list)
        self.customer_events: Dict[str, List[float]] = defaultdict(list)

    def _clean_old_events(self, event_list: List[float], current_time: float):
        cutoff = current_time - self.window_seconds
        while event_list and event_list[0] < cutoff:
            event_list.pop(0)

    def record_and_evaluate(self, txn: TransactionRequest) -> List[RiskFactor]:
        now = time.time()
        factors: List[RiskFactor] = []

        ip = txn.telemetry.ip_address
        device = txn.telemetry.device_fingerprint
        cust_id = txn.customer.customer_id
        
        card_identifier = None
        if txn.payment.payment_method == "card" and txn.payment.card_bin and txn.payment.card_last4:
            card_identifier = f"{txn.payment.card_bin}_{txn.payment.card_last4}"

        # 1. IP Velocity
        self._clean_old_events(self.ip_events[ip], now)
        self.ip_events[ip].append(now)
        ip_count = len(self.ip_events[ip])
        
        if ip_count >= 5:
            factors.append(RiskFactor(
                name="High IP Request Velocity",
                category="velocity",
                impact_score=min(40.0, 15.0 + (ip_count - 5) * 5.0),
                severity="critical" if ip_count >= 8 else "high",
                description=f"IP {ip} made {ip_count} transaction attempts within {self.window_seconds // 60} minutes",
                evidence={"ip": ip, "attempts_in_window": ip_count, "window_sec": self.window_seconds}
            ))

        # 2. Device Fingerprint Multi-Account Hopping (Sybil indicator)
        self._clean_old_events(self.device_events[device], now)
        self.device_events[device].append(now)
        self.device_accounts[device].add(cust_id)
        
        device_count = len(self.device_events[device])
        unique_accounts = len(self.device_accounts[device])
        
        if unique_accounts >= 3:
            factors.append(RiskFactor(
                name="Device Multi-Account Hopping",
                category="velocity",
                impact_score=35.0,
                severity="critical",
                description=f"Same device fingerprint ({device[:8]}...) used across {unique_accounts} distinct customer accounts",
                evidence={"device_fingerprint": device, "unique_accounts_count": unique_accounts}
            ))
        elif device_count >= 5:
            factors.append(RiskFactor(
                name="High Device Velocity",
                category="velocity",
                impact_score=25.0,
                severity="high",
                description=f"High transaction frequency from device fingerprint: {device_count} requests in 5 minutes",
                evidence={"device_fingerprint": device, "attempts": device_count}
            ))

        # 3. Card Velocity (Card Testing Attack indicator)
        if card_identifier:
            self._clean_old_events(self.card_events[card_identifier], now)
            self.card_events[card_identifier].append(now)
            card_count = len(self.card_events[card_identifier])
            if card_count >= 3:
                factors.append(RiskFactor(
                    name="Rapid Card Retry / Testing Pattern",
                    category="velocity",
                    impact_score=30.0,
                    severity="critical" if card_count >= 5 else "high",
                    description=f"Same card BIN/last4 targeted {card_count} times in under {self.window_seconds // 60} minutes",
                    evidence={"card_identifier": card_identifier, "attempts": card_count}
                ))

        # 4. Bot & Automation Latency (Sub-second checkout)
        if txn.telemetry.checkout_time_sec < 1.5:
            factors.append(RiskFactor(
                name="Sub-Human Checkout Velocity (Automated Bot)",
                category="behavioral",
                impact_score=28.0,
                severity="high",
                description=f"Checkout completed in {txn.telemetry.checkout_time_sec:.2f}s (physically impossible for human form-filling)",
                evidence={"checkout_time_sec": txn.telemetry.checkout_time_sec}
            ))

        # 5. VPN / Proxy / Anonymizer Flag
        if txn.telemetry.is_vpn_or_proxy:
            factors.append(RiskFactor(
                name="VPN / Datacenter Proxy Relay",
                category="behavioral",
                impact_score=20.0,
                severity="medium",
                description="Transaction originated from a known VPN, Tor exit node, or commercial proxy relay",
                evidence={"is_vpn_or_proxy": True, "ip": ip}
            ))

        return factors


# Global singleton instance
velocity_engine = VelocityTracker()
