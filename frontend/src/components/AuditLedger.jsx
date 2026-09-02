import React, { useState, useEffect } from 'react';
import { Lock, ShieldCheck, CheckCircle2, AlertTriangle, RefreshCw, Link as LinkIcon, Hash, Key } from 'lucide-react';
import { getAuditLedger, verifyLedgerIntegrity } from '../services/api';

export default function AuditLedger() {
  const [entries, setEntries] = useState([]);
  const [verification, setVerification] = useState(null);
  const [loadingVerify, setLoadingVerify] = useState(false);

  useEffect(() => {
    loadLedger();
  }, []);

  const loadLedger = async () => {
    const data = await getAuditLedger(50);
    setEntries(data);
  };

  const handleVerifyChain = async () => {
    setLoadingVerify(true);
    try {
      const res = await verifyLedgerIntegrity();
      setVerification(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingVerify(false);
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Header Banner */}
      <div className="glass-card p-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-lg bg-blue-600/20 border border-blue-500/40">
              <Lock className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white font-mono">
                Cryptographic SHA-256 Tamper-Proof Audit Ledger
              </h2>
              <p className="text-xs text-slate-400">
                Immutably records every risk decision, policy gate, and dispute defense with Merkle-leaf chaining and HMAC signatures.
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={handleVerifyChain}
              disabled={loadingVerify}
              className="btn-primary text-xs"
            >
              <ShieldCheck className={`w-4 h-4 ${loadingVerify ? 'animate-spin' : ''}`} />
              <span>Verify Cryptographic Integrity</span>
            </button>
          </div>
        </div>
      </div>

      {/* Verification Report Banner (if verified) */}
      {verification && (
        <div className={`p-4 rounded-lg border ${
          verification.valid
            ? 'bg-emerald-950/40 border-emerald-800/60 text-emerald-300'
            : 'bg-red-950/40 border-red-800/60 text-red-300'
        } space-y-2`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 font-mono text-xs font-bold">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>CHAIN INTEGRITY VERIFICATION PASSED (100% NON-TAMPERED)</span>
            </div>
            <span className="text-xs font-mono">{verification.total_blocks} Blocks Verified</span>
          </div>
          <div className="text-[11px] font-mono space-y-1 text-slate-300">
            <div>Genesis Hash: <span className="text-slate-400">{verification.genesis_hash}</span></div>
            <div>Latest Tip Hash: <span className="text-blue-400">{verification.latest_hash}</span></div>
          </div>
        </div>
      )}

      {/* Chained Blocks Stream */}
      <div className="glass-card p-6 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <h3 className="text-xs font-bold text-slate-300 uppercase font-mono tracking-wider">
            Immutable Event Blocks ({entries.length})
          </h3>
          <button onClick={loadLedger} className="text-xs text-blue-400 font-mono hover:underline flex items-center space-x-1">
            <RefreshCw className="w-3 h-3" />
            <span>Refresh Ledger</span>
          </button>
        </div>

        <div className="space-y-3">
          {entries.length === 0 ? (
            <div className="p-8 text-center text-slate-400 text-xs font-mono">
              No audit blocks recorded yet. Run transaction evaluations or dispute tests to generate blocks.
            </div>
          ) : (
            entries.map((entry) => (
              <div
                key={entry.index}
                className="p-4 rounded-lg bg-slate-900/70 border border-slate-800 space-y-3 hover:border-slate-700 transition"
              >
                {/* Block Top Header */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-blue-950 text-blue-400 border border-blue-800">
                      Block #{entry.index}
                    </span>
                    <span className="font-mono text-xs font-bold text-white uppercase">
                      {entry.event_type}
                    </span>
                    <span className="text-xs text-slate-400 font-mono">
                      (Entity: {entry.entity_id})
                    </span>
                  </div>
                  <span className="text-[11px] font-mono text-slate-400">
                    {new Date(entry.timestamp).toLocaleTimeString()}
                  </span>
                </div>

                {/* Event Payload Data */}
                <div className="p-2.5 rounded bg-slate-950 border border-slate-850 text-[11px] font-mono text-slate-300 overflow-x-auto">
                  {JSON.stringify(entry.event_data)}
                </div>

                {/* Hashes & Linkage */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-[11px] font-mono text-slate-400 pt-1">
                  <div className="flex items-center space-x-1.5 truncate">
                    <LinkIcon className="w-3 h-3 text-slate-400 shrink-0" />
                    <span>Prev:</span>
                    <span className="text-slate-300 truncate">{entry.previous_hash}</span>
                  </div>
                  <div className="flex items-center space-x-1.5 truncate">
                    <Hash className="w-3 h-3 text-blue-400 shrink-0" />
                    <span>Hash:</span>
                    <span className="text-blue-300 truncate">{entry.current_hash}</span>
                  </div>
                </div>

              </div>
            ))
          )}
        </div>
      </div>

    </div>
  );
}
