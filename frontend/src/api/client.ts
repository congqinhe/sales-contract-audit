const API_BASE = import.meta.env.VITE_API_BASE || "";

export async function inspectContract(contractText: string): Promise<{
  char_count: number;
  line_count: number;
  para_count_approx: number;
  first_300_chars: string;
  last_300_chars: string;
}> {
  const form = new FormData();
  form.append("contract_text", contractText);
  const res = await fetch(`${API_BASE}/api/contract/inspect`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function parseContract(
  content?: string,
  file?: File
): Promise<{
  paragraphs: { id: number; text: string; page?: number }[];
  full_text: string;
}> {
  const form = new FormData();
  if (content) form.append("content", content);
  if (file) form.append("file", file);
  const res = await fetch(`${API_BASE}/api/contract/parse`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const text = await res.text();
    let msg = text;
    try {
      const json = JSON.parse(text);
      if (json.detail) msg = typeof json.detail === "string" ? json.detail : String(json.detail);
    } catch (_) {}
    throw new Error(msg);
  }
  return res.json();
}

export async function auditContract(
  contractText: string,
  riskElement: string,
  explanation: string,
  riskExclusion?: string
): Promise<{ records: import("../types").AuditRecord[]; raw_output?: string }> {
  const form = new FormData();
  form.append("contract_text", contractText);
  form.append("risk_element", riskElement);
  form.append("explanation", explanation);
  if (riskExclusion) form.append("risk_exclusion", riskExclusion);
  const res = await fetch(`${API_BASE}/api/contract/audit`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const text = await res.text();
    let msg = text;
    try {
      const json = JSON.parse(text);
      if (json.detail) msg = typeof json.detail === "string" ? json.detail : String(json.detail);
    } catch (_) {}
    throw new Error(msg);
  }
  return res.json();
}

export async function listRules(): Promise<{ items: import("../types").Rule[] }> {
  const res = await fetch(`${API_BASE}/api/rules`);
  if (!res.ok) {
    const text = await res.text();
    let msg = text;
    try {
      const json = JSON.parse(text);
      if (json.detail) msg = typeof json.detail === "string" ? json.detail : String(json.detail);
    } catch (_) {}
    throw new Error(msg);
  }
  return res.json();
}
