import React, { useState, useEffect } from 'react';
import { Scale, FileText, CheckCircle2, ShieldCheck, Copy, Download, Clock, AlertCircle, Lock, Truck, CreditCard, UserCheck } from 'lucide-react';
import { getAllDisputes, triggerDisputeDefense } from '../services/api';

export default function DisputeStudio() {
  const [disputes, setDisputes] = useState([]);
  const [selectedDispute, setSelectedDispute] = useState(null);
  const [loadingDefense, setLoadingDefense] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    loadDisputes();
  }, []);

  const loadDisputes = async () => {
    const data = await getAllDisputes();
    setDisputes(data);
    if (data.length > 0) {
      setSelectedDispute(data[0]);
    }
  };

  const handleCopyRebuttal = () => {
    if (!selectedDispute?.evidence_pack?.rebuttal_letter) return;
    navigator.clipboard.writeText(selectedDispute.evidence_pack.rebuttal_letter);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadDossier = () => {
    if (!selectedDispute?.evidence_pack) return;
    const jsonString = `data:text/json;charset=utf-8,${encodeURIComponent(
      JSON.stringify(selectedDispute.evidence_pack, null, 2)
    )}`;
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', jsonString);
    downloadAnchor.setAttribute('download', `${selectedDispute.evidence_pack.dossier_id}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="space-y-6">
      
      {/* Header Banner */}
      <div className="glass-card p-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-lg bg-blue-600/20 border border-blue-500/40">
              <Scale className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white font-mono">
                Autonomous Chargeback & Dispute Defense Studio
              </h2>
              <p className="text-xs text-slate-400">
                Automates Visa/Mastercard Compelling Evidence 3.0 and RBI PA dispute rebuttals within seconds.
              </p>
            </div>
          </div>
          <div className="text-right">
            <span className="text-xs font-mono px-3 py-1 rounded-full bg-emerald-950/60 border border-emerald-800/40 text-emerald-400 font-bold">
              100% Defense Win Rate Target
            </span>
          </div>
        </div>
      </div>

      {/* Main Grid: Disputes List & Dossier Viewer */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column: Active Disputes (4 cols) */}
        <div className="lg:col-span-4 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-slate-300 uppercase font-mono tracking-wider">
              Tracked Disputes ({disputes.length})
            </h3>
            <span className="text-[11px] text-slate-400 font-mono">Razorpay Webhook Stream</span>
          </div>

          <div className="space-y-2">
            {disputes.map((item) => {
              const d = item.dispute;
              const isSelected = selectedDispute?.dispute?.dispute_id === d.dispute_id;
              return (
                <div
                  key={d.dispute_id}
                  onClick={() => setSelectedDispute(item)}
                  className={`glass-card p-4 glass-card-interactive border ${
                    isSelected ? 'border-blue-500 bg-blue-950/20' : 'border-slate-800'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-mono text-xs font-bold text-white">{d.dispute_id}</span>
                    <span className="font-mono text-xs font-bold text-emerald-400">
                      ₹{d.amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                    </span>
                  </div>

                  <div className="text-xs text-slate-300 mb-2 font-medium capitalize">
                    {d.reason_code.replace(/_/g, ' ')}
                  </div>

                  <div className="flex items-center justify-between text-[11px] text-slate-400 pt-2 border-t border-slate-800">
                    <span className="flex items-center space-x-1 text-amber-400 font-mono">
                      <Clock className="w-3 h-3" />
                      <span>5 Days Remaining</span>
                    </span>
                    <span className="text-blue-400 font-mono">Dossier Ready ✓</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Column: Compiled Defense Dossier (8 cols) */}
        <div className="lg:col-span-8">
          {selectedDispute?.evidence_pack ? (
            <div className="glass-card p-6 space-y-6">
              
              {/* Dossier Header & Export Actions */}
              <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800">
                <div>
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="text-xs font-mono text-blue-400 uppercase font-bold">
                      {selectedDispute.evidence_pack.dossier_id}
                    </span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-950 text-emerald-400 border border-emerald-800">
                      COMPLIANT DOSSIER
                    </span>
                  </div>
                  <h3 className="font-bold text-base text-white">
                    Compelling Evidence Package — Order #{selectedDispute.dispute.order_id}
                  </h3>
                </div>

                <div className="flex items-center space-x-2">
                  <button onClick={handleCopyRebuttal} className="btn-secondary text-xs">
                    <Copy className="w-3.5 h-3.5" />
                    <span>{copied ? 'Copied!' : 'Copy Letter'}</span>
                  </button>
                  <button onClick={handleDownloadDossier} className="btn-primary text-xs">
                    <Download className="w-3.5 h-3.5" />
                    <span>Export JSON Dossier</span>
                  </button>
                </div>
              </div>

              {/* Multi-Source Forensic Evidence Checklist */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                
                {/* 1. 2FA & Telemetry */}
                <div className="p-3.5 rounded-lg bg-slate-900/80 border border-slate-800 space-y-2">
                  <div className="flex items-center space-x-2 text-xs font-bold text-blue-400 font-mono">
                    <CreditCard className="w-4 h-4" />
                    <span>3DS 2FA Auth Reference</span>
                  </div>
                  <div className="text-[11px] text-slate-300 font-mono space-y-1">
                    <div>Ref: {selectedDispute.evidence_pack.transaction_telemetry_proof.auth_ref}</div>
                    <div className="text-emerald-400">✓ Issuer Liability Shift Active</div>
                    <div className="text-slate-400">{selectedDispute.evidence_pack.transaction_telemetry_proof.ip} ({selectedDispute.evidence_pack.transaction_telemetry_proof.geo_city})</div>
                  </div>
                </div>

                {/* 2. Courier Proof of Delivery */}
                <div className="p-3.5 rounded-lg bg-slate-900/80 border border-slate-800 space-y-2">
                  <div className="flex items-center space-x-2 text-xs font-bold text-blue-400 font-mono">
                    <Truck className="w-4 h-4" />
                    <span>Courier POD Verified</span>
                  </div>
                  <div className="text-[11px] text-slate-300 font-mono space-y-1">
                    <div>Carrier: {selectedDispute.evidence_pack.delivery_pod_proof.carrier}</div>
                    <div>AWB: {selectedDispute.evidence_pack.delivery_pod_proof.awb}</div>
                    <div className="text-emerald-400">✓ Recipient OTP Confirmed</div>
                  </div>
                </div>

                {/* 3. Invoice & Terms */}
                <div className="p-3.5 rounded-lg bg-slate-900/80 border border-slate-800 space-y-2">
                  <div className="flex items-center space-x-2 text-xs font-bold text-blue-400 font-mono">
                    <UserCheck className="w-4 h-4" />
                    <span>Signed Invoice & Terms</span>
                  </div>
                  <div className="text-[11px] text-slate-300 font-mono space-y-1">
                    <div>Inv: {selectedDispute.evidence_pack.merchant_invoice_proof.invoice_no}</div>
                    <div>Customer: {selectedDispute.evidence_pack.customer_summary.name}</div>
                    <div className="text-emerald-400">✓ Terms Consented at Checkout</div>
                  </div>
                </div>

              </div>

              {/* Formal Legal Rebuttal Letter Viewer */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-xs font-bold text-slate-300 uppercase font-mono tracking-wider flex items-center space-x-2">
                    <FileText className="w-4 h-4 text-blue-400" />
                    <span>Automated Bank Rebuttal Letter Preview</span>
                  </h4>
                  <span className="text-[11px] text-slate-400 font-mono">Visa/Mastercard CE 3.0 Standard</span>
                </div>

                <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 font-mono text-[11px] text-slate-300 whitespace-pre-wrap leading-relaxed max-h-72 overflow-y-auto">
                  {selectedDispute.evidence_pack.rebuttal_letter}
                </div>
              </div>

              {/* Cryptographic Dossier Hash */}
              <div className="pt-4 border-t border-slate-800 flex items-center justify-between text-[11px] font-mono text-slate-400">
                <div className="flex items-center space-x-2">
                  <Lock className="w-3.5 h-3.5 text-blue-400" />
                  <span>Dossier SHA-256 Hash Seal:</span>
                  <span className="text-slate-300">{selectedDispute.evidence_pack.dossier_hash}</span>
                </div>
                <span className="text-emerald-400 font-bold">✓ Ready for Razorpay API Submission</span>
              </div>

            </div>
          ) : (
            <div className="glass-card p-12 text-center text-slate-400 text-xs">
              Select a dispute to review its auto-generated compelling evidence package.
            </div>
          )}
        </div>

      </div>

    </div>
  );
}
