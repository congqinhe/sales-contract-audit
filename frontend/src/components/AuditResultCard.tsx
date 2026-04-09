import React, { useCallback } from "react";
import type { AuditRecord } from "../types";
import "./AuditResultCard.css";

interface Props {
  record: AuditRecord;
  onRefClick: (start: number, end: number) => void;
}

const REVIEW_TYPE_LABELS: Record<string, string> = {
  identify: "识别",
  judge: "判定",
  verify: "核对",
};

const RISK_LEVEL_LABELS: Record<string, string> = {
  risk: "有风险",
  no_risk: "无风险",
  needs_manual_review: "需人工核验",
  not_applicable: "不适用",
};

function renderTextWithRefs(
  text: string,
  onRefClick: (start: number, end: number) => void
): (string | React.ReactElement)[] {
  const parts: (string | React.ReactElement)[] = [];
  const re = /\{\{?id:(\d+)(?:-(\d+))?\}\}?/g;
  let lastIndex = 0;
  let m: RegExpExecArray | null;
  while ((m = re.exec(text)) !== null) {
    parts.push(text.slice(lastIndex, m.index));
    const start = parseInt(m[1], 10);
    const end = m[2] ? parseInt(m[2], 10) : start;
    parts.push(
      <button
        key={m.index}
        type="button"
        className="ref-link"
        onClick={() => onRefClick(start, end)}
      >
        {m[0]}
      </button>
    );
    lastIndex = m.index + m[0].length;
  }
  parts.push(text.slice(lastIndex));
  return parts;
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

  return (
    <div className={`audit-result-card card-${riskLevelClass(record.risk_level)}`}>
      <div className="card-top-row">
        <span className={`risk-badge ${riskLevelClass(record.risk_level)}`}>
          {RISK_LEVEL_LABELS[record.risk_level] || record.risk_level}
        </span>
        <span className={`type-badge type-${record.review_type}`}>
          {REVIEW_TYPE_LABELS[record.review_type] || record.review_type}
        </span>
        {record.rule_id && (
          <span className="rule-id-badge">{record.rule_id}</span>
        )}
      </div>

      <div className="review-point">{record.review_point}</div>

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
            {record.contract_quote || "未找到相关条款"}
          </span>
        </div>
      </div>

      {extractedEntries.length > 0 && (
        <div className="extracted-section">
          <div className="section-label">提取信息</div>
          <div className="extracted-grid">
            {extractedEntries.map(([key, val]) => (
              <div key={key} className="extracted-item">
                <span className="extracted-key">{key}:</span>
                <span className="extracted-val">{String(val)}</span>
              </div>
            ))}
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
          <div className="suggestion-content">{record.suggestion}</div>
        </div>
      )}
    </div>
  );
}
