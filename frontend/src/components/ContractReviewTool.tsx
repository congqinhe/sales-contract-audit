import { useState, useCallback, useEffect, useMemo } from "react";
import {
  parseContract,
  auditByModule,
  auditFull,
  listModules,
  listRulesByModule,
  inspectContract,
} from "../api/client";
import type { Paragraph, Rule, AuditRecord } from "../types";
import { OriginalTextPanel } from "./OriginalTextPanel";
import { AuditResultPanel } from "./AuditResultPanel";
import "./ContractReviewTool.css";

const COMPANIES = ["通用", "低压", "诺雅克", "输配电"];

export function ContractReviewTool() {
  const [paragraphs, setParagraphs] = useState<Paragraph[]>([]);
  const [fullText, setFullText] = useState("");

  const [modules, setModules] = useState<string[]>([]);
  const [selectedModule, setSelectedModule] = useState<string>("");
  const [company, setCompany] = useState("通用");
  const [moduleRules, setModuleRules] = useState<Record<string, Rule[]>>({});

  const [records, setRecords] = useState<AuditRecord[]>([]);
  const [highlightRange, setHighlightRange] = useState<{
    start: number;
    end: number;
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const [auditProgress, setAuditProgress] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [inputText, setInputText] = useState("");
  const [inputSource, setInputSource] = useState<"paste" | "file">("paste");

  useEffect(() => {
    listModules()
      .then(({ modules: mods }) => {
        setModules(mods);
        if (mods.length > 0) setSelectedModule(mods[0]);
      })
      .catch((e) => setError(String(e)));
  }, []);

  useEffect(() => {
    listRulesByModule(company !== "通用" ? company : undefined)
      .then(({ modules: grouped }) => setModuleRules(grouped))
      .catch(() => {});
  }, [company]);

  const handleParsePaste = useCallback(async () => {
    if (!inputText.trim()) {
      setError("请粘贴合同文本");
      return;
    }
    setError(null);
    setLoading(true);
    try {
      const res = await parseContract(inputText.trim());
      setParagraphs(res.paragraphs || []);
      setFullText(res.full_text || "");
      setRecords([]);
    } catch (err) {
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
        setParagraphs(res.paragraphs || []);
        setFullText(res.full_text || "");
        setRecords([]);
      } catch (err) {
        setError(String(err));
      } finally {
        setLoading(false);
      }
      e.target.value = "";
    },
    []
  );

  const handleAuditModule = useCallback(async () => {
    if (!fullText || !selectedModule) {
      setError("请先录入合同文本并选择模块");
      return;
    }
    setError(null);
    setLoading(true);
    setAuditProgress(`正在审核【${selectedModule}】…`);
    try {
      const res = await auditByModule(
        fullText,
        selectedModule,
        company !== "通用" ? company : undefined
      );
      setRecords(res.records);
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
      setAuditProgress("");
    }
  }, [fullText, selectedModule, company]);

  const handleAuditFull = useCallback(async () => {
    if (!fullText) {
      setError("请先录入合同文本");
      return;
    }
    setError(null);
    setLoading(true);
    setAuditProgress("正在全量审核（所有模块并行）…");
    try {
      const res = await auditFull(
        fullText,
        company !== "通用" ? company : undefined
      );
      const allRecords: AuditRecord[] = [];
      for (const moduleName of modules) {
        const moduleRecs = res.modules[moduleName];
        if (moduleRecs) allRecords.push(...moduleRecs);
      }
      setRecords(allRecords);
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
      setAuditProgress("");
    }
  }, [fullText, company, modules]);

  const handleRefClick = useCallback((start: number, end: number) => {
    setHighlightRange({ start, end });
    setTimeout(() => setHighlightRange(null), 3000);
  }, []);

  const coveredParaIds = useMemo(() => {
    const ids = new Set<number>();
    for (const r of records) {
      const s = typeof r.paragraph_start === "number" ? r.paragraph_start : NaN;
      const e = typeof r.paragraph_end === "number" ? r.paragraph_end : NaN;
      if (!isNaN(s) && !isNaN(e)) {
        for (let i = s; i <= e; i++) ids.add(i);
      }
      for (const ref of r.refs) {
        for (let i = ref.start; i <= ref.end; i++) ids.add(i);
      }
    }
    return ids;
  }, [records]);

  const inputCollapsed = paragraphs.length > 0;
  const currentModuleRules = moduleRules[selectedModule] || [];

  return (
    <div className="contract-review-tool">
      <header className="tool-header">
        <h1>合同智能评审</h1>
        <div className="tool-actions">
          <select
            className="company-select"
            value={company}
            onChange={(e) => setCompany(e.target.value)}
          >
            {COMPANIES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
          <select
            className="module-select"
            value={selectedModule}
            onChange={(e) => setSelectedModule(e.target.value)}
          >
            <option value="">选择评审模块</option>
            {modules.map((m) => (
              <option key={m} value={m}>
                {m}（{(moduleRules[m] || []).length}条）
              </option>
            ))}
          </select>
          <button
            className="btn btn-primary"
            onClick={handleAuditModule}
            disabled={loading || !fullText || !selectedModule}
          >
            {loading ? "审核中…" : "模块审核"}
          </button>
          <button
            className="btn btn-full-audit"
            onClick={handleAuditFull}
            disabled={loading || !fullText}
          >
            {loading ? "审核中…" : "全量审核"}
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
                placeholder={
                  "请粘贴合同文本，格式示例：\n\n<!-- 1 --> 产品采购合同（一体机）\n<!-- 2 --> 合同编号：xxx\n<!-- 3 --> 采购方（以下简称需方）：..."
                }
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
                选择 TXT 文件
                <input
                  id="file-input"
                  type="file"
                  accept=".txt"
                  onChange={handleParseFile}
                  disabled={loading}
                  hidden
                />
              </label>
              <span className="file-hint">
                支持 .txt 文件（需含 {"<!-- N -->"} 段落编号格式）
              </span>
            </div>
          )}
        </div>
      ) : (
        <div className="loaded-info">
          已加载 {paragraphs.length} 个段落
          {selectedModule && currentModuleRules.length > 0 && (
            <span className="module-rule-count">
              | 当前模块：{selectedModule}（{currentModuleRules.length}条规则）
            </span>
          )}
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
      {auditProgress && <div className="progress-banner">{auditProgress}</div>}

      <div className="dual-panel">
        <OriginalTextPanel
          paragraphs={paragraphs}
          highlightRange={highlightRange}
          coveredParaIds={coveredParaIds}
        />
        <AuditResultPanel records={records} onRefClick={handleRefClick} />
      </div>
    </div>
  );
}
