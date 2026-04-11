import React, { useCallback } from "react";
import type { AuditRecord, EvidenceSpan } from "../types";
import "./AuditResultCard.css";

interface Props {
  record: AuditRecord;
  onRefClick: (start: number, end: number) => void;
}

const RISK_LEVEL_LABELS: Record<string, string> = {
  risk: "有风险",
  no_risk: "无风险",
  needs_manual_review: "需人工核验",
  not_applicable: "仅识别",
};

/**
 * 兼容各种段落引用变体：
 * {id:72}  {{id:72}}  {{ id: 72 }}
 * {{id:72-74}}  {{id:72–74}}         （范围）
 * {{id:128, 134}}  {{id:128,134}}    （逗号分隔）
 */
const REF_TOKEN_RE =
  /\{?\{\s*id\s*:\s*(\d+)(?:\s*[-–,，]\s*(\d+))?\s*\}\}?/g;

/**
 * 是否展示「段落编号 + 合同原文」整块引用区。
 * 当前与「证据覆盖」信息重复且主引用常为证据子集，故默认关闭。
 * 若需恢复左侧大段原文引用，改为 true 即可。
 */
const SHOW_LEGACY_CONTRACT_QUOTE_META = false;

function isObjectArray(val: unknown): val is Record<string, unknown>[] {
  return (
    Array.isArray(val) &&
    val.length > 0 &&
    val.every((item) => typeof item === "object" && item !== null && !Array.isArray(item))
  );
}

function ExtractedValue({
  val,
  onRefClick,
}: {
  val: unknown;
  onRefClick: (start: number, end: number) => void;
}): React.ReactElement {
  if (val === null || val === undefined) return <span className="extracted-val ev-empty">—</span>;

  if (typeof val === "boolean")
    return (
      <span className={`extracted-val ev-bool ${val ? "ev-bool-yes" : "ev-bool-no"}`}>
        {val ? "是" : "否"}
      </span>
    );

  if (typeof val === "number")
    return <span className="extracted-val">{val}</span>;

  if (typeof val === "string")
    return (
      <span className="extracted-val">
        {val ? renderTextWithRefs(val, onRefClick) : "—"}
      </span>
    );

  if (isObjectArray(val)) {
    const cols = Array.from(new Set(val.flatMap((row) => Object.keys(row))));
    return (
      <table className="ev-table">
        <thead>
          <tr>
            {cols.map((c) => (
              <th key={c}>{c}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {val.map((row, ri) => (
            <tr key={ri}>
              {cols.map((c) => (
                <td key={c}>{row[c] != null ? String(row[c]) : "—"}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    );
  }

  if (Array.isArray(val))
    return (
      <span className="extracted-val">
        {val.map((item) => (typeof item === "object" ? JSON.stringify(item) : String(item))).join("、")}
      </span>
    );

  if (typeof val === "object") {
    const entries = Object.entries(val as Record<string, unknown>);
    return (
      <div className="ev-kv-group">
        {entries.map(([k, v]) => (
          <div key={k} className="ev-kv-row">
            <span className="ev-kv-key">{k}:</span>
            <span className="ev-kv-val">{v != null ? String(v) : "—"}</span>
          </div>
        ))}
      </div>
    );
  }

  return <span className="extracted-val">{String(val)}</span>;
}

function renderTextWithRefs(
  text: string,
  onRefClick: (start: number, end: number) => void
): (string | React.ReactElement)[] {
  const parts: (string | React.ReactElement)[] = [];
  const re = new RegExp(REF_TOKEN_RE.source, "g");
  let lastIndex = 0;
  let m: RegExpExecArray | null;
  while ((m = re.exec(text)) !== null) {
    parts.push(text.slice(lastIndex, m.index));
    const start = parseInt(m[1], 10);
    const end = m[2] ? parseInt(m[2], 10) : start;
    const label =
      end !== start ? `段落 ${start}–${end}` : `段落 ${start}`;
    parts.push(
      <button
        key={m.index}
        type="button"
        className="ref-link"
        title={m[0]}
        onClick={() => onRefClick(start, end)}
      >
        {label}
      </button>
    );
    lastIndex = m.index + m[0].length;
  }
  parts.push(text.slice(lastIndex));
  return parts;
}

function normalizeEvidenceSpans(record: AuditRecord): EvidenceSpan[] {
  const raw = record.evidence_spans;
  if (!Array.isArray(raw) || raw.length === 0) return [];
  const out: EvidenceSpan[] = [];
  for (const el of raw) {
    if (!el || typeof el !== "object") continue;
    const o = el as Record<string, unknown>;
    const ps = o.paragraph_start ?? o.start;
    const pe = o.paragraph_end ?? o.end;
    const ns = typeof ps === "number" ? ps : parseInt(String(ps), 10);
    const ne = typeof pe === "number" ? pe : parseInt(String(pe), 10);
    if (!Number.isFinite(ns) || !Number.isFinite(ne)) continue;
    let a = ns;
    let b = ne;
    if (b < a) [a, b] = [b, a];
    const brief = o.brief != null && String(o.brief).trim() ? String(o.brief).trim() : undefined;
    out.push(
      brief !== undefined
        ? { paragraph_start: a, paragraph_end: b, brief }
        : { paragraph_start: a, paragraph_end: b }
    );
  }
  return out;
}

/** 无 evidence_spans 时，用主段落字段合成一条，避免旧数据无跳转入口 */
function fallbackEvidenceSpan(record: AuditRecord, isNotFound: boolean): EvidenceSpan[] {
  if (isNotFound) return [];
  const ps = Number(record.paragraph_start);
  const pe = Number(record.paragraph_end);
  if (!Number.isFinite(ps) || !Number.isFinite(pe)) return [];
  let a = ps;
  let b = pe;
  if (b < a) [a, b] = [b, a];
  return [{ paragraph_start: a, paragraph_end: b }];
}

function riskLevelClass(level: string): string {
  switch (level) {
    case "risk":
      return "risk-danger";
    case "no_risk":
      return "risk-safe";
    case "needs_manual_review":
      return "risk-review";
    case "not_applicable":
      return "risk-na";
    default:
      return "risk-review";
  }
}

export function AuditResultCard({ record, onRefClick }: Props) {
  const handleRefClick = useCallback(
    (start: number, end: number) => onRefClick(start, end),
    [onRefClick]
  );

  const isNotFound =
    record.paragraph_start === "未找到" ||
    record.contract_quote === "未找到相关条款";

  const extractedEntries = Object.entries(record.extracted_info || {});
  const evidenceSpans = normalizeEvidenceSpans(record);
  const displayEvidenceSpans =
    evidenceSpans.length > 0 ? evidenceSpans : fallbackEvidenceSpan(record, isNotFound);
  const showEvidenceBlock = displayEvidenceSpans.length > 0;

  return (
    <div className={`audit-result-card card-${riskLevelClass(record.risk_level)}`}>
      <div className="card-top-row">
        <span className={`risk-badge ${riskLevelClass(record.risk_level)}`}>
          {RISK_LEVEL_LABELS[record.risk_level] || record.risk_level}
        </span>
        {record.rule_id && (
          <span className="rule-id-badge">{record.rule_id}</span>
        )}
      </div>

      <div className="review-point">{record.review_point}</div>

      {SHOW_LEGACY_CONTRACT_QUOTE_META ? (
        <div className="meta-section">
          <div className="meta-row">
            <span className="meta-label">段落编号:</span>
            <span className="meta-value">
              {isNotFound ? (
                "未找到"
              ) : (
                <button
                  type="button"
                  className="ref-link meta-ref"
                  onClick={() =>
                    onRefClick(
                      Number(record.paragraph_start),
                      Number(record.paragraph_end)
                    )
                  }
                >
                  {record.paragraph_start} - {record.paragraph_end}
                </button>
              )}
            </span>
          </div>
          <div className="meta-row">
            <span className="meta-label">合同原文:</span>
            <span className="meta-value">
              {record.contract_quote
                ? renderTextWithRefs(record.contract_quote, handleRefClick)
                : "未找到相关条款"}
            </span>
          </div>
        </div>
      ) : null}

      {isNotFound && !showEvidenceBlock ? (
        <div className="evidence-not-found">未找到相关条款</div>
      ) : null}

      {showEvidenceBlock ? (
        <details className="evidence-spans-details" open={displayEvidenceSpans.length <= 2}>
          <summary className="evidence-spans-summary">
            <span className="evidence-summary-chevron" aria-hidden="true">
              <svg width="10" height="10" viewBox="0 0 10 10" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path
                  d="M2.5 3.75L5 6.25L7.5 3.75"
                  stroke="currentColor"
                  strokeWidth="1.25"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </span>
            <span className="evidence-summary-text">
              <span className="evidence-summary-title">证据覆盖</span>
              <span className="evidence-summary-count">{displayEvidenceSpans.length} 处段落</span>
            </span>
          </summary>
          <ul className="evidence-spans-list">
            {displayEvidenceSpans.map((sp, idx) => (
              <li key={`${sp.paragraph_start}-${sp.paragraph_end}-${idx}`} className="evidence-spans-item">
                <button
                  type="button"
                  className="ref-link evidence-span-ref"
                  onClick={() => onRefClick(sp.paragraph_start, sp.paragraph_end)}
                >
                  {sp.paragraph_start === sp.paragraph_end
                    ? `段落 ${sp.paragraph_start}`
                    : `段落 ${sp.paragraph_start}–${sp.paragraph_end}`}
                </button>
                {sp.brief ? <span className="evidence-span-brief">{sp.brief}</span> : null}
              </li>
            ))}
          </ul>
        </details>
      ) : null}

      {extractedEntries.length > 0 && (
        <div className="extracted-section">
          <div className="section-label">提取信息</div>
          <div className="extracted-grid">
            {extractedEntries.map(([key, val]) => {
              const isComplex =
                isObjectArray(val) || (typeof val === "object" && val !== null && !Array.isArray(val));
              return (
                <div key={key} className={`extracted-item${isComplex ? " extracted-item-block" : ""}`}>
                  <span className="extracted-key">{key}:</span>
                  <ExtractedValue val={val} onRefClick={handleRefClick} />
                </div>
              );
            })}
          </div>
        </div>
      )}

      {record.risk_description && (
        <div className="conclusion-section">
          <div className="section-label">评审意见</div>
          <div className="conclusion-content">
            {renderTextWithRefs(record.risk_description, handleRefClick)}
          </div>
        </div>
      )}

      {record.suggestion && (
        <div className="suggestion-section">
          <div className="section-label">建议</div>
          <div className="suggestion-content">
            {renderTextWithRefs(record.suggestion, handleRefClick)}
          </div>
        </div>
      )}
    </div>
  );
}
