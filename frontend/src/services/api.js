const API_BASE = "http://localhost:8000/api/v1";

export async function evaluateTransaction(transactionPayload) {
  const res = await fetch(`${API_BASE}/transactions/evaluate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(transactionPayload)
  });
  if (!res.ok) throw new Error(`API error: ${res.statusText}`);
  return await res.json();
}

export async function getRecentTransactions(limit = 20) {
  try {
    const res = await fetch(`${API_BASE}/transactions/recent?limit=${limit}`);
    if (!res.ok) return [];
    return await res.json();
  } catch (err) {
    console.error("Failed to fetch recent transactions:", err);
    return [];
  }
}

export async function getAllDisputes() {
  try {
    const res = await fetch(`${API_BASE}/disputes/all`);
    if (!res.ok) return [];
    return await res.json();
  } catch (err) {
    console.error("Failed to fetch disputes:", err);
    return [];
  }
}

export async function triggerDisputeDefense(disputePayload) {
  const res = await fetch(`${API_BASE}/disputes/webhook`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(disputePayload)
  });
  if (!res.ok) throw new Error(`Dispute defense error: ${res.statusText}`);
  return await res.json();
}

export async function getLatestBenchmark() {
  try {
    const res = await fetch(`${API_BASE}/benchmarks/latest`);
    if (!res.ok) throw new Error("Failed to get benchmark");
    return await res.json();
  } catch (err) {
    console.error("Benchmark fetch error:", err);
    return null;
  }
}

export async function runBenchmarkAtThreshold(threshold = 65.0) {
  const res = await fetch(`${API_BASE}/benchmarks/run?block_threshold=${threshold}`, {
    method: "POST"
  });
  if (!res.ok) throw new Error("Failed to run benchmark");
  return await res.json();
}

export async function getAuditLedger(limit = 50) {
  try {
    const res = await fetch(`${API_BASE}/audit/ledger?limit=${limit}`);
    if (!res.ok) return [];
    return await res.json();
  } catch (err) {
    console.error("Failed to fetch audit ledger:", err);
    return [];
  }
}

export async function verifyLedgerIntegrity() {
  const res = await fetch(`${API_BASE}/audit/verify`);
  if (!res.ok) throw new Error("Verification error");
  return await res.json();
}
