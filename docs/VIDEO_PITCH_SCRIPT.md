# RazorShield AI: 5-Minute Pitch & Live Demo Script

**Submission Video Guide for Razorpay AI Buildathon 2026 (Track 02: AI Risk Manager)**
*Target Video Duration: 4 minutes 30 seconds – 5 minutes 00 seconds*

---

## 🎬 Act 1: The Hook & The Problem (0:00 - 0:45)

**[Camera on Speaker / Screen showing Razorpay & E-commerce checkout stats]**
> *"Hi Razorpay team! In Indian FinTech and D2C commerce, revenue isn't just lost when payments fail — it's systematically drained by fraud, COD/RTO abuse, and un-defended chargebacks.
> 
> When a merchant ships a Cash-on-Delivery order to a fake address, they bleed ₹180 to ₹250 in logistics. When bot syndicates run card-testing attacks, merchants face heavy gateway penalties. And when friendly fraud strikes, merchants have just 7 days to compile complex banking evidence or lose the money forever.
> 
> As a builder with a strong cybersecurity background, I realized what's missing isn't another black-box LLM — it's a **Defense-First, Explainable, and Cryptographically Verifiable AI Risk Sentinel**. 
> 
> Meet **RazorShield AI**."*

---

## 🏗️ Act 2: Architecture & Defense-in-Depth (0:45 - 1:45)

**[Screen sharing Architecture Diagram in docs/ARCHITECTURE.md]**
> *"RazorShield AI sits directly between incoming Razorpay transactions, webhook events, and the merchant’s fulfillment pipeline. It is built on three core pillars:
> 
> 1. **Multi-Vector Risk Classifier**: We combine Shannon Character Entropy and Indian PIN code geographic routing to catch fake addresses and disposable identities; sliding-window velocity limiters to catch bot automation; and a real-time NetworkX Bipartite Entity Graph to uncover distributed Sybil fraud rings.
> 
> 2. **SHAP-Style Factor Explainability**: Every score from 0 to 100 has a transparent attribution breakdown and clear merchant advisories — no guesswork.
> 
> 3. **Autonomous Dispute Defender**: When a `dispute.created` webhook fires, our agent correlates 3D-Secure 2FA auth codes, Courier Proof-of-Delivery timestamps, and invoices to synthesize a bank-ready Visa/Mastercard Compelling Evidence dossier in seconds.
> 
> 4. **Cryptographic SHA-256 Audit Chain**: Every decision is sealed in an immutable, tamper-evident Merkle ledger with HMAC verification."*

---

## 💻 Act 3: Live Interactive Demo (1:45 - 3:30)

**[Switching to live RazorShield SOC Dashboard UI]**

### Scenario 1: Clean Customer Transaction (Green Path)
> *"Let's test a clean UPI transaction. Notice the latency: **0.25 milliseconds**. RazorShield validates the address against Bengaluru PIN 560038, observes normal 18-second checkout duration, rewards past customer history with trust credits, and issues an instant `ALLOW`."*

### Scenario 2: RTO / Address Entropy Abuse (Orange Path)
> *"Now let's simulate a malicious COD order with keyboard-smashed address `asdfghjk 123` and a disposable email. RazorShield flags high entropy, detects the fake phone pattern, and executes a targeted policy action: `COD_RESTRICTED`. It advises offering a ₹50 discount to convert the buyer to prepaid UPI, protecting the merchant from logistics loss."*

### Scenario 3: Bot-Driven Card Testing & Sybil Ring Attack (Red Path)
> *"Next, we simulate a distributed card testing bot. Notice the sub-second checkout time (0.4s) and proxy relay. The Sybil Graph Sentinel immediately identifies that this device fingerprint is hopping across 4 different accounts. Action: `BLOCK` with 98% confidence. The transaction is rejected, saving the merchant from gateway penalties."*

### Scenario 4: Autonomous Chargeback Defense in Action
> *"Now let's head over to the **Chargeback Defense Studio**. We receive a ₹3,499 dispute for 'Unauthorized Transaction'. With 1 click, our Autonomous Agent harvests the 3DS liability shift token, BlueDart tracking AWB, OTP delivery confirmation, and invoice to compile this formal legal rebuttal letter ready for bank submission. And notice the SHA-256 cryptographic seal guaranteeing non-tampering."*

---

## 📊 Act 4: Verifiable Metrics & False Positive Cost (3:30 - 4:15)

**[Switching to Benchmark Suite Tab]**
> *"Track 02 demands honest metrics. We built an automated benchmark suite evaluated on **1,000 synthetic Indian FinTech transactions**.
> 
> Look at the verified results:
> - **Accuracy**: 98.6%
> - **Precision**: 100.0%
> - **Recall**: 93.64%
> - **Average Latency**: 0.25ms
> - **Net Money Saved**: Over **₹17.5 Lakhs INR** in prevented fraud losses with **zero false-positive friction cost** on clean buyers.
> 
> With our interactive threshold slider, merchants can tune sensitivity in real time to perfectly balance fraud prevention with user checkout friction."*

---

## 🎯 Act 5: Conclusion & Why Razorpay (4:15 - 5:00)

**[Camera on Speaker / GitHub Repo on Screen]**
> *"RazorShield AI isn't a theoretical prototype. It has a complete FastAPI backend, full Pytest test suite, Next.js/React SOC dashboard, Docker support, and exhaustive threat model documentation.
> 
> As an AI Builder Intern at Razorpay, this is exactly the kind of robust, defense-in-depth, high-throughput infrastructure I want to build and scale.
> 
> Thank you, and I look forward to meeting the panel!"*
