import React from 'react';
import { Shield, Activity, Lock, Cpu, BarChart2, Scale, Terminal } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, ledgerValid, latencyMs }) {
  const tabs = [
    { id: 'radar', label: 'Threat Radar & Live Stream', icon: Activity },
    { id: 'disputes', label: 'Chargeback Defense Studio', icon: Scale },
    { id: 'benchmarks', label: 'Benchmark & Threshold Tuner', icon: BarChart2 },
    { id: 'audit', label: 'Cryptographic Audit Chain', icon: Lock },
  ];

  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo & System Brand */}
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-600/20 border border-blue-500/40 rounded-lg flex items-center justify-center">
              <Shield className="w-6 h-6 text-blue-400" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg tracking-tight text-white font-mono">
                  Razor<span className="text-blue-400">Shield</span> AI
                </span>
                <span className="text-xs px-2 py-0.5 rounded-full bg-blue-900/50 text-blue-300 border border-blue-700/50 font-medium">
                  Autonomous Risk Engine v1.0
                </span>
              </div>
              <p className="text-xs text-slate-400">FinTech Risk & Threat Defense Sentinel</p>
            </div>
          </div>

          {/* Nav Tabs */}
          <nav className="flex space-x-1">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg text-xs font-semibold transition-all ${
                    isActive
                      ? 'bg-blue-600/20 text-blue-400 border border-blue-500/40 shadow-sm shadow-blue-500/20'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60 border border-transparent'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Engine Status Indicators */}
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-emerald-950/60 border border-emerald-800/40 text-emerald-400 text-xs font-mono">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>OPERATIONAL</span>
            </div>
            <div className="text-xs font-mono text-slate-400 px-2.5 py-1 bg-slate-900 rounded-md border border-slate-800">
              ⚡ {latencyMs ? `${latencyMs}ms` : '0.25ms'} avg
            </div>
          </div>

        </div>
      </div>
    </header>
  );
}
