import { useMemo } from "react";
import type { AuditRecord } from "../types";
import { AuditResultCard } from "./AuditResultCard";
import "./AuditResultPanel.css";

interface Props {
  records: AuditRecord[];
  onRefClick: (start: number, end: number) => void;
}

export function AuditResultPanel({ records, onRefClick }: Props) {
  const grouped = useMemo(() => {
    const map: Record<string, AuditRecord[]> = {};
    for (const r of records) {
      const mod = r.module || "未分类";
      if (!map[mod]) map[mod] = [];
      map[mod].push(r);
    }
    return map;
  }, [records]);

  const moduleNames = Object.keys(grouped);

  const summary = useMemo(() => {
    let risk = 0;
    let noRisk = 0;
    let needsReview = 0;
    for (const r of records) {
      if (r.risk_level === "risk") risk++;
      else if (r.risk_level === "no_risk") noRisk++;
      else if (r.risk_level === "needs_manual_review") needsReview++;
    }
    return { risk, noRisk, needsReview, total: records.length };
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
          </span>
        )}
      </div>
      <div className="records">
        {records.length === 0 ? (
          <div className="empty-state">
            请上传合同并选择评审模块执行审核
          </div>
        ) : moduleNames.length === 1 ? (
          records.map((r, i) => (
            <AuditResultCard key={i} record={r} onRefClick={onRefClick} />
          ))
        ) : (
          moduleNames.map((mod) => (
            <div key={mod} className="module-group">
              <div className="module-group-header">{mod}</div>
              {grouped[mod].map((r, i) => (
                <AuditResultCard key={i} record={r} onRefClick={onRefClick} />
              ))}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
