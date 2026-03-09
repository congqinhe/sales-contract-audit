import React, { useCallback } from "react";
import type { AuditRecord } from "../types";
import "./AuditResultCard.css";

interface Props {
  record: AuditRecord;
  onRefClick: (start: number, end: number) => void;
}

/** 将 {{id:X-Y}}、{id:X} 等段落引用替换为可点击链接，点击后左侧锚中对应段落 */
function renderConclusionWithRefs(
  text: string,
  onRefClick: (start: number, end: number) => void
): (string | React.ReactElement)[] {
  const parts: (string | React.ReactElement)[] = [];
  // 支持 {{id:X}}、{{id:X-Y}}、{id:X}、{id:X-Y}
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

function riskLevelClass(level?: string): string {
  if (!level) return "risk-mid";
  if (level.includes("低")) return "risk-low";
  if (level.includes("高")) return "risk-high";
  return "risk-mid";
}

export function AuditResultCard({ record, onRefClick }: Props) {
  const handleRefClick = useCallback(
    (start: number, end: number) => onRefClick(start, end),
    [onRefClick]
  );

  const isNotFound =
    record.paragraph_start === "未找到" || record.original_text === "未找到相关条款";

  return (
    <div className="audit-result-card">
      <div className={`risk-badge ${riskLevelClass(record.risk_level)}`}>
        {record.risk_level || "中风险"}
      </div>
      <div className="risk-element">{record.risk_element}</div>

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
          <span className="meta-label">原文文本:</span>
          <span className="meta-value">
            {record.original_text || "未找到相关条款"}
          </span>
        </div>
      </div>

      <div className="conclusion-section">
        {record.conclusion_and_reason.includes("原因分析") ? (
          <>
            <div className="conclusion-label">风险判断结论:</div>
            <div className="conclusion-content highlight-red">
              {record.conclusion_and_reason
                .split("原因分析")[0]
                ?.replace(/风险判断结论[:：]\s*/g, "")
                .trim() || "-"}
            </div>
            <div className="conclusion-label">原因分析:</div>
            <div className="conclusion-content reason">
              {renderConclusionWithRefs(
                record.conclusion_and_reason
                  .split("原因分析")[1]
                  ?.replace(/^[:：]\s*/, "")
                  .trim() || "",
                handleRefClick
              )}
            </div>
          </>
        ) : (
          <>
            <div className="conclusion-label">风险判断结论及原因:</div>
            <div className="conclusion-content reason">
              {renderConclusionWithRefs(record.conclusion_and_reason, handleRefClick)}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
