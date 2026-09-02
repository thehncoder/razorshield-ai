import React, { useState } from 'react';
import { Play, ShieldAlert, ShieldCheck, AlertTriangle, Zap, User, MapPin, CreditCard, Clock, Lock, CheckCircle2, ChevronRight, Fingerprint, Network } from 'lucide-react';
import { evaluateTransaction } from '../services/api';

const SAMPLE_SCENARIOS = [
  {
    id: 'clean',
    title: 'Clean Verified Order',
    badge: 'Safe (Green Path)',
    badgeColor: 'text-emerald-400 border-emerald-800/40 bg-emerald-950/40',
    description: 'Genuine Bangalore user paying via UPI with 3 past successful orders.',
    payload: {
      transaction_id: `txn_clean_${Math.floor(1000 + Math.random() * 9000)}`,
      merchant_id: 'rzp_mid_blr_demo',
      order_id: `ord_${Math.floor(10000 + Math.random() * 90000)}`,
      customer: {
        customer_id: 'cust_priya_sharma_99',
        name: 'Priya Sharma',
        email: 'priya.sharma92@gmail.com',
        phone: '+91 98450 12891',
        historical_orders_count: 4,
        successful_orders_count: 4,
        rto_count: 0,
        dispute_count: 0
      },
      shipping_address: {
        line1: 'Flat #402, Royal Palms, 12th Main Road, Indiranagar',
        line2: 'Near Metro Station Pillar 84',
        city: 'Bengaluru',
        state: 'Karnataka',
        pincode: '560038',
        country: 'IN'
      },
      payment: {
        payment_method: 'upi',
        amount: 2499.00,
        currency: 'INR',
        upi_vpa: 'priyasharma@okhdfcbank'
      },
      telemetry: {
        ip_address: '49.37.12.84',
        user_agent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
        device_fingerprint: 'fp_mac_priya_9f81',
        session_duration_sec: 142.5,
        checkout_time_sec: 18.2,
        is_vpn_or_proxy: false,
        geo_city: 'Bengaluru',
        geo_state: 'Karnataka'
      },
      items_count: 2,
      items_categories: ['Apparel', 'Accessories']
    }
  },
  {
    id: 'rto_entropy',
    title: 'RTO / Address Entropy Abuse',
    badge: 'High RTO Risk',
    badgeColor: 'text-amber-400 border-amber-800/40 bg-amber-950/40',
    description: 'Cash-on-Delivery with keyboard-smashed address, disposable email, and dummy phone.',
    payload: {
      transaction_id: `txn_rto_${Math.floor(1000 + Math.random() * 9000)}`,
      merchant_id: 'rzp_mid_blr_demo',
      order_id: `ord_${Math.floor(10000 + Math.random() * 90000)}`,
      customer: {
        customer_id: 'cust_anon_rto_22',
        name: 'Rohan Test',
        email: 'temp_buyer_99@mailinator.com',
        phone: '9999999999',
        historical_orders_count: 1,
        successful_orders_count: 0,
        rto_count: 2,
        dispute_count: 0
      },
      shipping_address: {
        line1: 'asdfghjkl qwerty 12345 road',
        line2: 'unknown lane',
        city: 'Mumbai',
        state: 'Maharashtra',
        pincode: '999999',
        country: 'IN'
      },
      payment: {
        payment_method: 'cod',
        amount: 4899.00,
        currency: 'INR'
      },
      telemetry: {
        ip_address: '103.22.44.11',
        user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        device_fingerprint: 'fp_win_anon_4412',
        session_duration_sec: 8.0,
        checkout_time_sec: 4.1,
        is_vpn_or_proxy: false,
        geo_city: 'Mumbai',
        geo_state: 'Maharashtra'
      },
      items_count: 1,
      items_categories: ['Consumer Electronics']
    }
  },
  {
    id: 'bot_card_tester',
    title: 'Sub-Second Card Testing Bot',
    badge: 'Critical Attack',
    badgeColor: 'text-red-400 border-red-800/40 bg-red-950/40',
    description: 'Headless bot script executing sub-second checkouts via Tor/Proxy relay.',
    payload: {
      transaction_id: `txn_bot_${Math.floor(1000 + Math.random() * 9000)}`,
      merchant_id: 'rzp_mid_blr_demo',
      order_id: `ord_${Math.floor(10000 + Math.random() * 90000)}`,
      customer: {
        customer_id: 'cust_bot_probe_71',
        name: 'Alex Hunter',
        email: 'probe_card_992@tempmail.com',
        phone: '+91 91234 56789',
        historical_orders_count: 0,
        successful_orders_count: 0,
        rto_count: 0,
        dispute_count: 0
      },
      shipping_address: {
        line1: '12 Main Street',
        line2: '',
        city: 'Delhi',
        state: 'Delhi',
        pincode: '110001',
        country: 'IN'
      },
      payment: {
        payment_method: 'card',
        amount: 1.00,
        currency: 'INR',
        card_bin: '411111',
        card_last4: '9821'
      },
      telemetry: {
        ip_address: '185.220.101.5',
        user_agent: 'Python-urllib/3.12 (Headless Browser)',
        device_fingerprint: 'fp_bot_card_tester_01',
        session_duration_sec: 0.8,
        checkout_time_sec: 0.35,
        is_vpn_or_proxy: true,
        geo_city: 'Frankfurt',
        geo_state: 'Hesse'
      },
      items_count: 1,
      items_categories: ['Digital Voucher']
    }
  },
  {
    id: 'sybil_ring',
    title: 'Coordinated Sybil Fraud Ring',
    badge: 'Syndicate Network',
    badgeColor: 'text-purple-400 border-purple-800/40 bg-purple-950/40',
    description: 'Multi-accounting syndicate sharing hardware fingerprints & payment VPAs.',
    payload: {
      transaction_id: `txn_sybil_${Math.floor(1000 + Math.random() * 9000)}`,
      merchant_id: 'rzp_mid_blr_demo',
      order_id: `ord_${Math.floor(10000 + Math.random() * 90000)}`,
      customer: {
        customer_id: `cust_sybil_member_${Math.floor(10 + Math.random() * 90)}`,
        name: 'Vikas Patel',
        email: 'vikas.sybil.ring@yopmail.com',
        phone: '+91 97123 45678',
        historical_orders_count: 1,
        successful_orders_count: 0,
        rto_count: 1,
        dispute_count: 1
      },
      shipping_address: {
        line1: 'Plot #18, Ring Colony Road 4',
        line2: 'Near Bus Terminal',
        city: 'Ahmedabad',
        state: 'Gujarat',
        pincode: '380015',
        country: 'IN'
      },
      payment: {
        payment_method: 'card',
        amount: 8499.00,
        currency: 'INR',
        card_bin: '524128',
        card_last4: '4491'
      },
      telemetry: {
        ip_address: '103.45.12.89',
        user_agent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        device_fingerprint: 'dev_sybil_ring_shared_hw',
        session_duration_sec: 14.0,
        checkout_time_sec: 2.8,
        is_vpn_or_proxy: true,
        geo_city: 'Ahmedabad',
        geo_state: 'Gujarat'
      },
      items_count: 3,
      items_categories: ['High Value Electronics']
    }
  }
];

export default function LiveThreatRadar({ transactions, setTransactions, onSelectTxn, selectedTxn }) {
  const [loadingScenario, setLoadingScenario] = useState(null);

  const handleRunScenario = async (scenario) => {
    setLoadingScenario(scenario.id);
    try {
      const result = await evaluateTransaction(scenario.payload);
      setTransactions((prev) => [result, ...prev]);
      onSelectTxn(result);
    } catch (err) {
      console.error('Failed to run scenario:', err);
    } finally {
      setLoadingScenario(null);
    }
  };

  const getActionBadge = (action) => {
    switch (action) {
      case 'ALLOW':
        return <span className="px-2.5 py-1 rounded-md text-xs font-mono font-bold badge-allow">✓ ALLOW</span>;
      case 'CHALLENGE_STEP_UP_AUTH':
        return <span className="px-2.5 py-1 rounded-md text-xs font-mono font-bold badge-challenge">⚡ STEP-UP AUTH</span>;
      case 'COD_RESTRICTED':
        return <span className="px-2.5 py-1 rounded-md text-xs font-mono font-bold badge-cod">⛔ COD RESTRICTED</span>;
      case 'BLOCK':
        return <span className="px-2.5 py-1 rounded-md text-xs font-mono font-bold badge-block">✕ BLOCK</span>;
      default:
        return <span className="px-2.5 py-1 rounded-md text-xs font-mono">{action}</span>;
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Attack Scenario Injectors Bar */}
      <div className="glass-card p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <Zap className="w-4 h-4 text-blue-400" />
            <h2 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
              Real-Time Attack Vector Simulator
            </h2>
          </div>
          <span className="text-xs text-slate-400">Click any scenario to inject live transaction stream</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          {SAMPLE_SCENARIOS.map((sc) => (
            <button
              key={sc.id}
              onClick={() => handleRunScenario(sc)}
              disabled={loadingScenario === sc.id}
              className="text-left p-3 rounded-lg bg-slate-900/90 hover:bg-slate-850 border border-slate-800 hover:border-slate-700 transition flex flex-col justify-between group"
            >
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="font-semibold text-xs text-white group-hover:text-blue-400 transition">{sc.title}</span>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded font-mono border ${sc.badgeColor}`}>
                    {sc.badge}
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed">
                  {sc.description}
                </p>
              </div>
              <div className="mt-3 flex items-center justify-between text-[11px] text-blue-400 font-mono pt-2 border-t border-slate-800/80">
                <span>Inject Webhook</span>
                <Play className={`w-3 h-3 ${loadingScenario === sc.id ? 'animate-spin' : ''}`} />
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Main Grid: Live Feed & Deep-Dive Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column: Live Transaction Stream (5 cols) */}
        <div className="lg:col-span-5 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-slate-300 uppercase font-mono tracking-wider flex items-center space-x-2">
              <span className="w-2 h-2 rounded-full bg-blue-500 animate-ping"></span>
              <span>Live Ingested Transactions ({transactions.length})</span>
            </h3>
            <span className="text-[11px] text-slate-400 font-mono">Click card to inspect</span>
          </div>

          <div className="space-y-2 max-h-[640px] overflow-y-auto pr-1">
            {transactions.length === 0 ? (
              <div className="glass-card p-8 text-center text-slate-400 text-xs">
                No transactions ingested yet. Click a scenario button above to simulate!
              </div>
            ) : (
              transactions.map((txn) => {
                const isSelected = selectedTxn?.evaluation_id === txn.evaluation_id;
                return (
                  <div
                    key={txn.evaluation_id}
                    onClick={() => onSelectTxn(txn)}
                    className={`glass-card p-3.5 glass-card-interactive border ${
                      isSelected ? 'border-blue-500 bg-blue-950/20' : 'border-slate-800'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-mono text-xs font-bold text-white">{txn.transaction_id}</span>
                      {getActionBadge(txn.recommendation.action)}
                    </div>

                    <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
                      <div className="flex items-center space-x-3">
                        <span>Risk Score:</span>
                        <span className={`font-mono font-bold ${
                          txn.overall_risk_score >= 70 ? 'text-red-400' :
                          txn.overall_risk_score >= 35 ? 'text-amber-400' : 'text-emerald-400'
                        }`}>
                          {txn.overall_risk_score} / 100
                        </span>
                      </div>
                      <span className="font-mono text-[11px] text-slate-400">⚡ {txn.latency_ms}ms</span>
                    </div>

                    <div className="text-[11px] text-slate-400 line-clamp-1">
                      {txn.recommendation.reason}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Right Column: Deep-Dive Forensic Inspector (7 cols) */}
        <div className="lg:col-span-7">
          {selectedTxn ? (
            <div className="glass-card p-6 space-y-6">
              
              {/* Header Details */}
              <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800">
                <div>
                  <div className="flex items-center space-x-3 mb-1">
                    <h3 className="font-mono font-bold text-lg text-white">
                      {selectedTxn.transaction_id}
                    </h3>
                    {getActionBadge(selectedTxn.recommendation.action)}
                  </div>
                  <p className="text-xs text-slate-400 font-mono">
                    Evaluation ID: {selectedTxn.evaluation_id} • Latency: {selectedTxn.latency_ms}ms
                  </p>
                </div>

                <div className="text-right">
                  <div className="text-xs text-slate-400">Composite Risk Score</div>
                  <div className={`font-mono text-3xl font-extrabold ${
                    selectedTxn.overall_risk_score >= 70 ? 'text-red-400' :
                    selectedTxn.overall_risk_score >= 35 ? 'text-amber-400' : 'text-emerald-400'
                  }`}>
                    {selectedTxn.overall_risk_score}
                    <span className="text-xs text-slate-400 font-normal"> / 100</span>
                  </div>
                </div>
              </div>

              {/* Sub-Score Breakdown Matrix */}
              <div className="grid grid-cols-3 gap-3">
                <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-center">
                  <div className="text-[11px] text-slate-400 uppercase font-mono">RTO / Postal Risk</div>
                  <div className="font-mono text-lg font-bold text-slate-200 mt-1">
                    {selectedTxn.rto_risk_score} <span className="text-xs text-slate-400">/ 100</span>
                  </div>
                </div>
                <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-center">
                  <div className="text-[11px] text-slate-400 uppercase font-mono">Payment Fraud</div>
                  <div className="font-mono text-lg font-bold text-slate-200 mt-1">
                    {selectedTxn.payment_fraud_score} <span className="text-xs text-slate-400">/ 100</span>
                  </div>
                </div>
                <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-center">
                  <div className="text-[11px] text-slate-400 uppercase font-mono">Sybil Ring Risk</div>
                  <div className="font-mono text-lg font-bold text-slate-200 mt-1">
                    {selectedTxn.sybil_ring_score} <span className="text-xs text-slate-400">/ 100</span>
                  </div>
                </div>
              </div>

              {/* Merchant Advisory Banner */}
              <div className="p-4 rounded-lg bg-blue-950/30 border border-blue-800/40 space-y-1.5">
                <div className="flex items-center space-x-2 text-xs font-bold text-blue-400 font-mono uppercase">
                  <ShieldCheck className="w-4 h-4" />
                  <span>RazorShield Merchant Advisory</span>
                </div>
                <p className="text-xs text-slate-200 leading-relaxed font-medium">
                  {selectedTxn.recommendation.merchant_advisory}
                </p>
              </div>

              {/* SHAP-Style Factor Attribution Breakdown */}
              <div>
                <h4 className="text-xs font-bold text-slate-300 uppercase font-mono tracking-wider mb-3 flex items-center space-x-2">
                  <Fingerprint className="w-4 h-4 text-blue-400" />
                  <span>Explainable Factor Attribution (SHAP-Style)</span>
                </h4>

                <div className="space-y-2.5">
                  {selectedTxn.risk_factors.map((factor, idx) => {
                    const isPositive = factor.impact_score > 0;
                    return (
                      <div key={idx} className="p-3 rounded-lg bg-slate-900/60 border border-slate-800 space-y-1.5">
                        <div className="flex items-center justify-between text-xs">
                          <div className="flex items-center space-x-2 font-medium text-slate-200">
                            <span className={`w-2 h-2 rounded-full ${
                              factor.severity === 'critical' ? 'bg-red-400' :
                              factor.severity === 'high' ? 'bg-amber-400' :
                              factor.severity === 'medium' ? 'bg-yellow-400' : 'bg-emerald-400'
                            }`}></span>
                            <span>{factor.name}</span>
                          </div>
                          <span className={`font-mono font-bold ${isPositive ? 'text-red-400' : 'text-emerald-400'}`}>
                            {isPositive ? `+${factor.impact_score}` : factor.impact_score} pts
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-400 leading-normal">{factor.description}</p>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Cryptographic Proof Footer */}
              <div className="pt-4 border-t border-slate-800 flex items-center justify-between text-[11px] font-mono text-slate-400">
                <div className="flex items-center space-x-2">
                  <Lock className="w-3.5 h-3.5 text-blue-400" />
                  <span>Audit Chain Block Hash:</span>
                  <span className="text-slate-300">{selectedTxn.tamper_proof_hash.substring(0, 18)}...</span>
                </div>
                <span className="text-emerald-400">✓ Cryptographically Verified</span>
              </div>

            </div>
          ) : (
            <div className="glass-card p-12 text-center text-slate-400 text-xs">
              Select a transaction on the left to inspect forensic attribution details.
            </div>
          )}
        </div>

      </div>

    </div>
  );
}
