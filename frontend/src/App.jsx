import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import LiveThreatRadar from './components/LiveThreatRadar';
import DisputeStudio from './components/DisputeStudio';
import BenchmarkSuite from './components/BenchmarkSuite';
import AuditLedger from './components/AuditLedger';
import { getRecentTransactions } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('radar');
  const [transactions, setTransactions] = useState([]);
  const [selectedTxn, setSelectedTxn] = useState(null);
  const [latencyMs, setLatencyMs] = useState('0.25');

  useEffect(() => {
    // Initial fetch of recent evaluations if any
    async function loadData() {
      const recent = await getRecentTransactions(20);
      if (recent.length > 0) {
        setTransactions(recent);
        setSelectedTxn(recent[0]);
        setLatencyMs(recent[0].latency_ms.toString());
      }
    }
    loadData();
  }, []);

  return (
    <div className="min-h-screen bg-[#07090e] text-slate-100 flex flex-col font-sans selection:bg-blue-600 selection:text-white">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        ledgerValid={true}
        latencyMs={latencyMs}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'radar' && (
          <LiveThreatRadar
            transactions={transactions}
            setTransactions={setTransactions}
            selectedTxn={selectedTxn}
            onSelectTxn={(txn) => {
              setSelectedTxn(txn);
              setLatencyMs(txn.latency_ms.toString());
            }}
          />
        )}

        {activeTab === 'disputes' && <DisputeStudio />}

        {activeTab === 'benchmarks' && <BenchmarkSuite />}

        {activeTab === 'audit' && <AuditLedger />}
      </main>

      <footer className="border-t border-slate-900 bg-slate-950/60 py-6 text-center text-xs text-slate-400 font-mono">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <div>
            RazorShield AI • Razorpay AI Buildathon 2026 (Track 02: AI Risk Manager)
          </div>
          <div className="flex items-center space-x-3 text-slate-400">
            <span>FastAPI Backend (Port 8000)</span>
            <span>•</span>
            <span>Vite React SOC (Port 5173)</span>
            <span>•</span>
            <span className="text-blue-400">SHA-256 Merkle Ledger</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
