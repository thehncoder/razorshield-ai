import math
import re
from typing import Dict, Any, List, Tuple
from app.models.schemas import ShippingAddress, CustomerProfile, RiskFactor


# Known Indian State PIN prefix mappings
INDIAN_PINCODE_PREFIXES = {
    "11": ["delhi"],
    "12": ["haryana"],
    "13": ["haryana"],
    "14": ["punjab"],
    "15": ["punjab"],
    "16": ["chandigarh", "punjab"],
    "17": ["himachal pradesh"],
    "18": ["jammu and kashmir"],
    "19": ["jammu and kashmir"],
    "20": ["uttar pradesh"],
    "21": ["uttar pradesh"],
    "22": ["uttar pradesh"],
    "23": ["uttar pradesh"],
    "24": ["uttarakhand", "uttar pradesh"],
    "25": ["uttar pradesh"],
    "26": ["uttarakhand", "uttar pradesh"],
    "27": ["uttar pradesh"],
    "28": ["uttar pradesh"],
    "30": ["rajasthan"],
    "31": ["rajasthan"],
    "32": ["rajasthan"],
    "33": ["rajasthan"],
    "34": ["rajasthan"],
    "36": ["gujarat"],
    "37": ["gujarat"],
    "38": ["gujarat"],
    "39": ["gujarat"],
    "40": ["maharashtra", "goa"],
    "41": ["maharashtra"],
    "42": ["maharashtra"],
    "43": ["maharashtra"],
    "44": ["maharashtra"],
    "45": ["madhya pradesh"],
    "46": ["madhya pradesh"],
    "47": ["madhya pradesh"],
    "48": ["madhya pradesh"],
    "49": ["chhattisgarh"],
    "50": ["telangana", "andhra pradesh"],
    "51": ["andhra pradesh"],
    "52": ["andhra pradesh"],
    "53": ["andhra pradesh"],
    "56": ["karnataka"],
    "57": ["karnataka"],
    "58": ["karnataka"],
    "59": ["karnataka"],
    "60": ["tamil nadu"],
    "61": ["tamil nadu"],
    "62": ["tamil nadu"],
    "63": ["tamil nadu"],
    "64": ["tamil nadu"],
    "67": ["kerala"],
    "68": ["kerala"],
    "69": ["kerala"],
    "70": ["west bengal"],
    "71": ["west bengal"],
    "72": ["west bengal"],
    "73": ["west bengal"],
    "74": ["west bengal"],
    "75": ["odisha"],
    "76": ["odisha"],
    "77": ["odisha"],
    "78": ["assam"],
    "79": ["arunachal pradesh", "manipur", "meghalaya", "mizoram", "nagaland", "tripura"],
    "80": ["bihar"],
    "81": ["bihar", "jharkhand"],
    "82": ["bihar", "jharkhand"],
    "83": ["jharkhand"],
    "84": ["bihar"],
    "85": ["bihar"],
}

DISPOSABLE_DOMAINS = {
    "mailinator.com", "tempmail.com", "10minutemail.com", "guerrillamail.com",
    "yopmail.com", "trashmail.com", "getairmail.com", "sharklasers.com",
    "dispostable.com", "throwawaymail.com", "fakemailgenerator.com"
}

REPETITIVE_PHONE_REGEX = re.compile(r"^(\d)\1{9}$")
SEQUENTIAL_ASC_PHONE = "0123456789"
SEQUENTIAL_DESC_PHONE = "9876543210"


def calculate_shannon_entropy(text: str) -> float:
    """Calculates Shannon entropy of a string."""
    cleaned = re.sub(r"\s+", "", text.lower())
    if not cleaned:
        return 0.0
    freq: Dict[str, int] = {}
    for char in cleaned:
        freq[char] = freq.get(char, 0) + 1
    
    entropy = 0.0
    total_len = len(cleaned)
    for count in freq.values():
        p = count / total_len
        entropy -= p * math.log2(p)
    return entropy


def detect_gibberish(text: str) -> Tuple[bool, float, str]:
    """
    Detects keyboard smashing or low-entropy/unrealistic text.
    Returns: (is_gibberish, confidence_score, reason)
    """
    cleaned = re.sub(r"[^a-zA-Z0-9]", "", text).lower()
    if len(cleaned) < 4:
        return True, 0.9, "Address line abnormally short (less than 4 alphanumeric characters)"
    
    # 1. Repetitive character check (e.g., 'aaaaaa', 'abcabcabc')
    if len(cleaned) >= 6:
        repeated_char_ratio = max([cleaned.count(c) for c in set(cleaned)]) / len(cleaned)
        if repeated_char_ratio > 0.5:
            return True, 0.85, f"High single-character repetition ratio ({repeated_char_ratio:.2f})"

    # 2. Shannon Entropy check
    entropy = calculate_shannon_entropy(cleaned)
    if entropy < 1.8 and len(cleaned) > 8:
        return True, 0.8, f"Abnormally low character entropy ({entropy:.2f}), likely repetitive pattern"

    # 3. Vowel / Consonant ratio in alphabetic tokens
    alpha_only = re.sub(r"[^a-z]", "", cleaned)
    if len(alpha_only) >= 6:
        vowels = sum(1 for c in alpha_only if c in "aeiou")
        vowel_ratio = vowels / len(alpha_only)
        if vowel_ratio < 0.12:
            return True, 0.75, f"Excessive consonant clustering without vowels (vowel ratio {vowel_ratio:.2f})"
        if vowel_ratio > 0.80:
            return True, 0.70, f"Abnormally high vowel concentration (vowel ratio {vowel_ratio:.2f})"

    # 4. Common keyboard smash substrings
    smash_patterns = ["asdf", "qwer", "zxcv", "hjkl", "12345", "98765"]
    for pat in smash_patterns:
        if pat in cleaned:
            return True, 0.8, f"Keyboard smash pattern '{pat}' detected"

    return False, 0.0, "Address text passed lexical entropy filters"


class EntropyRiskAnalyzer:
    """
    Analyzes lexical entropy, address validity, geographic mismatch,
    and disposable identity indicators.
    """

    @classmethod
    def analyze_shipping_address(cls, address: ShippingAddress) -> List[RiskFactor]:
        factors: List[RiskFactor] = []
        full_address = f"{address.line1} {address.line2} {address.city}".strip()
        
        # 1. Check Gibberish / Entropy on Address
        is_gibberish, conf, reason = detect_gibberish(full_address)
        if is_gibberish:
            factors.append(RiskFactor(
                name="Address Gibberish & Entropy Anomaly",
                category="entropy",
                impact_score=35.0 * conf,
                severity="critical" if conf > 0.8 else "high",
                description=f"Shipping address appears invalid or generated: {reason}",
                evidence={"shannon_entropy": round(calculate_shannon_entropy(full_address), 2), "reason": reason}
            ))

        # 2. Pincode Structure Validation (India 6 digits)
        pincode_clean = address.pincode.strip()
        if not re.match(r"^[1-9][0-9]{5}$", pincode_clean):
            factors.append(RiskFactor(
                name="Malformed Indian PIN Code",
                category="courier_pincode",
                impact_score=30.0,
                severity="critical",
                description=f"PIN code '{pincode_clean}' does not match standard 6-digit Indian Postal format",
                evidence={"entered_pincode": pincode_clean}
            ))
        else:
            # 3. State & PIN Code Geographic Prefix Consistency
            prefix_2 = pincode_clean[:2]
            expected_states = INDIAN_PINCODE_PREFIXES.get(prefix_2, [])
            state_lower = address.state.strip().lower()
            
            if expected_states and not any(exp in state_lower or state_lower in exp for exp in expected_states):
                factors.append(RiskFactor(
                    name="PIN Code & State Mismatch",
                    category="courier_pincode",
                    impact_score=25.0,
                    severity="high",
                    description=f"PIN code prefix '{prefix_2}' maps to {expected_states}, but state given was '{address.state}'",
                    evidence={"prefix": prefix_2, "expected_states": expected_states, "provided_state": address.state}
                ))

        # 4. Lack of House/Street Number (High RTO correlation in Indian Logistics)
        has_number = bool(re.search(r"\d+", address.line1))
        if not has_number and len(address.line1.split()) < 3:
            factors.append(RiskFactor(
                name="Vague Incomplete House/Street Address",
                category="entropy",
                impact_score=15.0,
                severity="medium",
                description="Address lacks specific house/plot number or landmark, high probability of courier undeliverability",
                evidence={"line1": address.line1}
            ))

        return factors

    @classmethod
    def analyze_customer_identity(cls, customer: CustomerProfile) -> List[RiskFactor]:
        factors: List[RiskFactor] = []
        
        # 1. Email Domain check
        email_clean = customer.email.strip().lower()
        if "@" in email_clean:
            domain = email_clean.split("@")[-1]
            if domain in DISPOSABLE_DOMAINS:
                factors.append(RiskFactor(
                    name="Disposable Email Domain Detected",
                    category="reputation",
                    impact_score=30.0,
                    severity="critical",
                    description=f"Customer registered with temporary disposable email provider: {domain}",
                    evidence={"domain": domain}
                ))
            
            # Check randomness in local-part of email
            local_part = email_clean.split("@")[0]
            if len(local_part) > 12 and bool(re.search(r"\d{5,}", local_part)):
                factors.append(RiskFactor(
                    name="High-Entropy Auto-Generated Email",
                    category="entropy",
                    impact_score=15.0,
                    severity="medium",
                    description="Email username pattern suggests synthetic or programmatic creation",
                    evidence={"local_part": local_part}
                ))

        # 2. Phone Number Validation
        phone_clean = re.sub(r"[^0-9]", "", customer.phone)
        if len(phone_clean) >= 10:
            last10 = phone_clean[-10:]
            if REPETITIVE_PHONE_REGEX.match(last10) or last10 in (SEQUENTIAL_ASC_PHONE, SEQUENTIAL_DESC_PHONE):
                factors.append(RiskFactor(
                    name="Fake / Repetitive Phone Number",
                    category="reputation",
                    impact_score=35.0,
                    severity="critical",
                    description=f"Phone number '{last10}' is a dummy/repetitive sequence",
                    evidence={"phone": customer.phone}
                ))
            elif not last10[0] in "6789":
                factors.append(RiskFactor(
                    name="Invalid Indian Mobile Number Prefix",
                    category="reputation",
                    impact_score=20.0,
                    severity="high",
                    description=f"Indian mobile numbers must start with 6, 7, 8, or 9 (got: {last10[0]})",
                    evidence={"phone": customer.phone}
                ))
        else:
            factors.append(RiskFactor(
                name="Incomplete Phone Number Length",
                category="reputation",
                impact_score=25.0,
                severity="high",
                description="Phone number contains fewer than 10 digits",
                evidence={"phone": customer.phone}
            ))

        return factors
