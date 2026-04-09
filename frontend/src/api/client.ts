import type { AuditRecord, AuditResponse, FullAuditResponse, Rule } from "../types";

const API_BASE = import.meta.env.VITE_API_BASE || "";

async function handleError(res: Response): Promise<never> {
  const text = await res.text();
  let msg = text;
  try {
    const json = JSON.parse(text);
    if (json.detail)
      msg = typeof json.detail === "string" ? json.detail : String(json.detail);
  } catch {
    /* keep raw text */
  }
  throw new Error(msg);
}

export async function inspectContract(contractText: string) {
  const form = new FormData();
  form.append("contract_text", contractText);
  const res = await fetch(`${API_BASE}/api/contract/inspect`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) return handleError(res);
  return res.json() as Promise<{
    char_count: number;
    line_count: number;
    para_count_approx: number;
    first_300_chars: string;
    last_300_chars: string;
  }>;
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
  if (!res.ok) return handleError(res);
  return res.json();
}

// -----------------------------------------------------------------------
// 方案B：模块级审核
// -----------------------------------------------------------------------

export async function auditByModule(
  contractText: string,
  module: string,
  company?: string
): Promise<AuditResponse> {
  const form = new FormData();
  form.append("contract_text", contractText);
  form.append("module", module);
  if (company) form.append("company", company);
  const res = await fetch(`${API_BASE}/api/contract/audit/module`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) return handleError(res);
  return res.json();
}

export async function auditFull(
  contractText: string,
  company?: string
): Promise<FullAuditResponse> {
  const form = new FormData();
  form.append("contract_text", contractText);
  if (company) form.append("company", company);
  const res = await fetch(`${API_BASE}/api/contract/audit/full`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) return handleError(res);
  return res.json();
}

export async function listRules(): Promise<{ items: Rule[] }> {
  const res = await fetch(`${API_BASE}/api/rules`);
  if (!res.ok) return handleError(res);
  return res.json();
}

export async function listModules(): Promise<{ modules: string[] }> {
  const res = await fetch(`${API_BASE}/api/rules/modules`);
  if (!res.ok) return handleError(res);
  return res.json();
}

export async function listRulesByModule(
  company?: string
): Promise<{ modules: Record<string, Rule[]> }> {
  const params = company ? `?company=${encodeURIComponent(company)}` : "";
  const res = await fetch(`${API_BASE}/api/rules/by-module${params}`);
  if (!res.ok) return handleError(res);
  return res.json();
}
