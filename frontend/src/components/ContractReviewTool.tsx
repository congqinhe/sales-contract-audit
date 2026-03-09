import { useState, useCallback, useEffect } from "react";
import { parseContract, auditContract, listRules, inspectContract } from "../api/client";
import type { Paragraph, Rule, AuditRecord } from "../types";
import { OriginalTextPanel } from "./OriginalTextPanel";
import { AuditResultPanel } from "./AuditResultPanel";
import "./ContractReviewTool.css";

export function ContractReviewTool() {
  const [paragraphs, setParagraphs] = useState<Paragraph[]>([]);
  const [fullText, setFullText] = useState("");
  const [rules, setRules] = useState<Rule[]>([]);
  const [selectedRule, setSelectedRule] = useState<Rule | null>(null);
  const [records, setRecords] = useState<AuditRecord[]>([]);
  const [highlightRange, setHighlightRange] = useState<{
    start: number;
    end: number;
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [inputText, setInputText] = useState("");
  const [inputSource, setInputSource] = useState<"paste" | "file">("paste");

  useEffect(() => {
    listRules()
      .then(({ items }) => {
        // #region agent log
        fetch('http://127.0.0.1:7390/ingest/f7289e82-292a-4746-8ff8-522eda614c1c',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'be0578'},body:JSON.stringify({sessionId:'be0578',location:'ContractReviewTool.tsx:listRules',message:'listRules success',data:{itemCount:items?.length},hypothesisId:'H1',timestamp:Date.now()})}).catch(()=>{});
        // #endregion
        setRules(items);
        if (items.length > 0) setSelectedRule((prev) => prev ?? items[0]);
      })
      .catch((e) => {
        // #region agent log
        fetch('http://127.0.0.1:7390/ingest/f7289e82-292a-4746-8ff8-522eda614c1c',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'be0578'},body:JSON.stringify({sessionId:'be0578',location:'ContractReviewTool.tsx:listRules-catch',message:'listRules failed',data:{err:String(e)},hypothesisId:'H1',timestamp:Date.now()})}).catch(()=>{});
        // #endregion
        setError(String(e));
      });
  }, []);

  const handleParsePaste = useCallback(async () => {
    if (!inputText.trim()) {
      setError("请粘贴合同文本");
      return;
    }
    setError(null);
    setLoading(true);
    try {
      const res = await parseContract(inputText.trim());
      // #region agent log
      fetch('http://127.0.0.1:7390/ingest/f7289e82-292a-4746-8ff8-522eda614c1c',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'be0578'},body:JSON.stringify({sessionId:'be0578',location:'ContractReviewTool.tsx:parsePaste',message:'parse success',data:{paragraphCount:res?.paragraphs?.length,hasFullText:!!res?.full_text},hypothesisId:'H2',timestamp:Date.now()})}).catch(()=>{});
      // #endregion
      setParagraphs(res.paragraphs || []);
      setFullText(res.full_text || "");
      setRecords([]);
    } catch (err) {
      // #region agent log
      fetch('http://127.0.0.1:7390/ingest/f7289e82-292a-4746-8ff8-522eda614c1c',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'be0578'},body:JSON.stringify({sessionId:'be0578',location:'ContractReviewTool.tsx:parsePaste-catch',message:'parse failed',data:{err:String(err)},hypothesisId:'H2',timestamp:Date.now()})}).catch(()=>{});
      // #endregion
      setError(String(err));
    } finally {
      setLoading(false);
    }
  }, [inputText]);

  const handleParseFile = useCallback(
    async (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;
      setError(null);
      setLoading(true);
    try {
      const res = await parseContract(undefined, file);
      // #region agent log
      fetch('http://127.0.0.1:7390/ingest/f7289e82-292a-4746-8ff8-522eda614c1c',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'be0578'},body:JSON.stringify({sessionId:'be0578',location:'ContractReviewTool.tsx:parseFile',message:'parse file success',data:{paragraphCount:res?.paragraphs?.length},hypothesisId:'H2',timestamp:Date.now()})}).catch(()=>{});
      // #endregion
        setParagraphs(res.paragraphs || []);
        setFullText(res.full_text || "");
        setRecords([]);
      } catch (err) {
        // #region agent log
        fetch('http://127.0.0.1:7390/ingest/f7289e82-292a-4746-8ff8-522eda614c1c',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'be0578'},body:JSON.stringify({sessionId:'be0578',location:'ContractReviewTool.tsx:parseFile-catch',message:'parse file failed',data:{err:String(err)},hypothesisId:'H2',timestamp:Date.now()})}).catch(()=>{});
        // #endregion
        setError(String(err));
      } finally {
        setLoading(false);
      }
      e.target.value = "";
    },
    []
  );

  const handleAudit = useCallback(async () => {
    if (!fullText || !selectedRule) {
      setError("请先录入合同文本并选择风险规则");
      return;
    }
    setError(null);
    setLoading(true);
    try {
      const res = await auditContract(
        fullText,
        selectedRule.risk_element,
        selectedRule.explanation,
        selectedRule.risk_exclusion || ""
      );
      // #region agent log
      fetch('http://127.0.0.1:7390/ingest/f7289e82-292a-4746-8ff8-522eda614c1c',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'be0578'},body:JSON.stringify({sessionId:'be0578',location:'ContractReviewTool.tsx:audit',message:'audit success',data:{recordCount:res?.records?.length},hypothesisId:'H3',timestamp:Date.now()})}).catch(()=>{});
      // #endregion
      setRecords(res.records);
    } catch (err) {
      // #region agent log
      fetch('http://127.0.0.1:7390/ingest/f7289e82-292a-4746-8ff8-522eda614c1c',{method:'POST',headers:{'Content-Type':'application/json','X-Debug-Session-Id':'be0578'},body:JSON.stringify({sessionId:'be0578',location:'ContractReviewTool.tsx:audit-catch',message:'audit failed',data:{err:String(err)},hypothesisId:'H3',timestamp:Date.now()})}).catch(()=>{});
      // #endregion
      setError(String(err));
    } finally {
      setLoading(false);
    }
  }, [fullText, selectedRule]);

  const handleRefClick = useCallback((start: number, end: number) => {
    setHighlightRange({ start, end });
    setTimeout(() => setHighlightRange(null), 3000);
  }, []);

  const inputCollapsed = paragraphs.length > 0;

  return (
    <div className="contract-review-tool">
      <header className="tool-header">
        <h1>合同风险审核</h1>
        <div className="tool-actions">
          <select
            className="rule-select"
            value={selectedRule?.id ?? ""}
            onChange={(e) => {
              const r = rules.find((x) => x.id === e.target.value);
              setSelectedRule(r ?? null);
            }}
          >
            <option value="">选择风险规则</option>
            {rules.map((r) => (
              <option key={r.id} value={r.id}>
                {r.risk_element}
              </option>
            ))}
          </select>
          <button
            className="btn btn-primary"
            onClick={handleAudit}
            disabled={loading || !fullText || !selectedRule}
          >
            {loading ? "审核中…" : "执行审核"}
          </button>
        </div>
      </header>

      {!inputCollapsed ? (
        <div className="input-section">
          <div className="input-tabs">
            <button
              type="button"
              className={`input-tab ${inputSource === "paste" ? "active" : ""}`}
              onClick={() => setInputSource("paste")}
            >
              粘贴文本
            </button>
            <button
              type="button"
              className={`input-tab ${inputSource === "file" ? "active" : ""}`}
              onClick={() => setInputSource("file")}
            >
              上传文件
            </button>
          </div>
          {inputSource === "paste" ? (
            <div className="paste-area">
              <textarea
                className="contract-textarea"
                placeholder="请粘贴合同文本，格式示例：&#10;&#10;<!-- 1 --> 产品采购合同（一体机）&#10;<!-- 2 --> 合同编号：xxx&#10;<!-- 3 --> 采购方（以下简称需方）：..."
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                rows={4}
              />
              <button
                type="button"
                className="btn btn-parse"
                onClick={handleParsePaste}
                disabled={loading || !inputText.trim()}
              >
                {loading ? "解析中…" : "解析并加载"}
              </button>
            </div>
          ) : (
            <div className="file-area">
              <label className="btn btn-upload">
                选择 TXT 或 PDF 文件
                <input
                  id="file-input"
                  type="file"
                  accept=".txt,.pdf"
                  onChange={handleParseFile}
                  disabled={loading}
                  hidden
                />
              </label>
              <span className="file-hint">支持 .txt（需含 {'<!-- N -->'} 格式）或 .pdf（自动解析）</span>
            </div>
          )}
        </div>
      ) : (
        <div className="loaded-info">
          已加载 {paragraphs.length} 个段落
          <button
            type="button"
            className="btn-inspect"
            onClick={async () => {
              if (!fullText) return;
              try {
                const r = await inspectContract(fullText);
                alert(
                  `【验证】合同全文统计\n\n` +
                    `字符数：${r.char_count}\n` +
                    `行数：${r.line_count}\n` +
                    `段落数（约）：${r.para_count_approx}\n\n` +
                    `末 300 字预览：\n${r.last_300_chars || "（无）"}`
                );
              } catch (e) {
                alert("验证失败：" + String(e));
              }
            }}
          >
            验证发送内容
          </button>
          <button
            type="button"
            className="btn btn-reload"
            onClick={() => {
              setParagraphs([]);
              setFullText("");
              setInputText("");
              setRecords([]);
              setError(null);
            }}
          >
            重新录入
          </button>
        </div>
      )}

      {error && <div className="error-banner">{error}</div>}

      <div className="dual-panel">
        <OriginalTextPanel
          paragraphs={paragraphs}
          highlightRange={highlightRange}
        />
        <AuditResultPanel records={records} onRefClick={handleRefClick} />
      </div>
    </div>
  );
}
