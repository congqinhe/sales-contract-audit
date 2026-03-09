import type { AuditRecord } from "../types";
import { AuditResultCard } from "./AuditResultCard";
import "./AuditResultPanel.css";

interface Props {
  records: AuditRecord[];
  onRefClick: (start: number, end: number) => void;
}

export function AuditResultPanel({ records, onRefClick }: Props) {
  return (
    <div className="audit-result-panel">
      <div className="panel-header">合同风险审查结果</div>
      <div className="records">
        {records.length === 0 ? (
          <div className="empty-state">
            请上传合同并选择风险规则执行审核
          </div>
        ) : (
          records.map((r, i) => (
            <AuditResultCard key={i} record={r} onRefClick={onRefClick} />
          ))
        )}
      </div>
    </div>
  );
}
