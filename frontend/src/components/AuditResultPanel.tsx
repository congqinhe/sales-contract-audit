import { useMemo } from "react";
import type { AuditRecord } from "../types";
import { AuditResultCard } from "./AuditResultCard";
import "./AuditResultPanel.css";

interface Props {
  records: AuditRecord[];
  onRefClick: (start: number, end: number) => void;
}

function paragraphSortKey(r: AuditRecord): number {
  const s = r.paragraph_start;
  if (s === "未找到" || s === undefined || s === null) {
    return Number.MAX_SAFE_INTEGER;
  }
  const n = typeof s === "number" ? s : parseInt(String(s), 10);
  return Number.isFinite(n) ? n : Number.MAX_SAFE_INTEGER;
}

function paragraphEndSortKey(r: AuditRecord): number {
  const s = r.paragraph_end;
  if (s === "未找到" || s === undefined || s === null) {
    return Number.MAX_SAFE_INTEGER;
  }
  const n = typeof s === "number" ? s : parseInt(String(s), 10);
  return Number.isFinite(n) ? n : Number.MAX_SAFE_INTEGER;
}

function recordRowKey(r: AuditRecord, index: number): string {
  return `${r.module}|${r.rule_id}|${String(r.paragraph_start)}-${String(r.paragraph_end)}|${index}`;
}

export function AuditResultPanel({ records, onRefClick }: Props) {
  const sortedRecords = useMemo(() => {
    const arr = [...records];
    arr.sort((a, b) => {
      const idCmp = String(a.rule_id || "").localeCompare(String(b.rule_id || ""), "zh");
      if (idCmp !== 0) return idCmp;
      const pa = paragraphSortKey(a);
      const pb = paragraphSortKey(b);
      if (pa !== pb) return pa - pb;
      return paragraphEndSortKey(a) - paragraphEndSortKey(b);
    });
    return arr;
  }, [records]);

  const grouped = useMemo(() => {
    const map: Record<string, AuditRecord[]> = {};
    for (const r of sortedRecords) {
      const mod = r.module || "未分类";
      if (!map[mod]) map[mod] = [];
      map[mod].push(r);
    }
    return map;
  }, [sortedRecords]);

  const moduleNames = Object.keys(grouped);

  const summary = useMemo(() => {
    let risk = 0;
    let noRisk = 0;
    let needsReview = 0;
    let identifyOnly = 0;
    for (const r of records) {
      if (r.risk_level === "risk") risk++;
      else if (r.risk_level === "no_risk") noRisk++;
      else if (r.risk_level === "needs_manual_review") needsReview++;
      else if (r.risk_level === "not_applicable") identifyOnly++;
    }
    return { risk, noRisk, needsReview, identifyOnly, total: records.length };
  }, [records]);

  return (
    <div className="audit-result-panel">
      <div className="panel-header">
        合同评审结果
        {records.length > 0 && (
          <span className="summary-badges">
            <span className="badge badge-risk">{summary.risk} 风险</span>
            <span className="badge badge-review">{summary.needsReview} 待核</span>
            <span className="badge badge-ok">{summary.noRisk} 通过</span>
            <span className="badge badge-identify-only">
              {summary.identifyOnly} 仅识别
            </span>
          </span>
        )}
      </div>
      <div className="records">
        {records.length === 0 ? (
          <div className="empty-state">
            请上传合同并选择评审模块执行审核
          </div>
        ) : moduleNames.length === 1 ? (
          sortedRecords.map((r, i) => (
            <AuditResultCard key={recordRowKey(r, i)} record={r} onRefClick={onRefClick} />
          ))
        ) : (
          moduleNames.map((mod) => (
            <div key={mod} className="module-group">
              <div className="module-group-header">{mod}</div>
              {grouped[mod].map((r, i) => (
                <AuditResultCard key={recordRowKey(r, i)} record={r} onRefClick={onRefClick} />
              ))}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
