import { useRef, useEffect, useState, useMemo } from "react";
import type { Paragraph } from "../types";
import "./OriginalTextPanel.css";

interface Props {
  paragraphs: Paragraph[];
  highlightRange: { start: number; end: number } | null;
}

function escapeRegex(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function highlightText(text: string, keyword: string): React.ReactNode {
  if (!keyword.trim()) return text;
  const escaped = escapeRegex(keyword);
  const re = new RegExp(`(${escaped})`, "gi");
  const parts = text.split(re);
  return parts.map((part, i) =>
    i % 2 === 1 ? <mark key={i}>{part}</mark> : part
  );
}

export function OriginalTextPanel({ paragraphs, highlightRange }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [searchKeyword, setSearchKeyword] = useState("");
  const [currentMatchIndex, setCurrentMatchIndex] = useState(0);

  const matchedParagraphs = useMemo(() => {
    if (!searchKeyword.trim()) return [];
    const kw = searchKeyword.trim();
    return paragraphs
      .map((p) => ({ para: p, text: p.text }))
      .filter(({ text }) => text.toLowerCase().includes(kw.toLowerCase()));
  }, [paragraphs, searchKeyword]);

  const totalMatches = matchedParagraphs.length;

  useEffect(() => {
    if (!highlightRange || !containerRef.current) return;
    const el = containerRef.current.querySelector(
      `[data-para-id="${highlightRange.start}"]`
    ) as HTMLElement;
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }, [highlightRange]);

  useEffect(() => {
    if (totalMatches === 0 || !containerRef.current) return;
    const idx = Math.min(currentMatchIndex, totalMatches - 1);
    const paraId = matchedParagraphs[idx]?.para.id;
    const el = containerRef.current.querySelector(
      `[data-para-id="${paraId}"]`
    ) as HTMLElement;
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }, [currentMatchIndex, totalMatches, matchedParagraphs]);

  const handlePrev = () => {
    setCurrentMatchIndex((i) => (i <= 0 ? totalMatches - 1 : i - 1));
  };
  const handleNext = () => {
    setCurrentMatchIndex((i) => (i >= totalMatches - 1 ? 0 : i + 1));
  };

  return (
    <div className="original-text-panel" ref={containerRef}>
      <div className="panel-header">合同原文</div>
      <div className="search-bar">
        <input
          type="text"
          placeholder="搜索关键词..."
          value={searchKeyword}
          onChange={(e) => {
            setSearchKeyword(e.target.value);
            setCurrentMatchIndex(0);
          }}
          className="search-input"
        />
        {totalMatches > 0 && (
          <span className="search-count">
            {currentMatchIndex + 1} / {totalMatches}
          </span>
        )}
        {totalMatches > 0 && (
          <div className="search-nav">
            <button type="button" onClick={handlePrev} className="search-nav-btn">
              ↑
            </button>
            <button type="button" onClick={handleNext} className="search-nav-btn">
              ↓
            </button>
          </div>
        )}
      </div>
      <div className="paragraphs">
        {paragraphs.map((p) => {
          const inRange =
            highlightRange &&
            p.id >= highlightRange.start &&
            p.id <= highlightRange.end;
          return (
            <div
              key={p.id}
              data-para-id={p.id}
              className={`para ${inRange ? "para-highlight" : ""}`}
            >
              <span className="para-id">{p.id}</span>
              <span className="para-text">
                {highlightText(p.text, searchKeyword)}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
