export interface Paragraph {
  id: number;
  text: string;
  page?: number;
}

export interface Rule {
  rule_id: string;
  module: string;
  review_point: string;
  review_type: "identify" | "judge" | "verify";
  applies_to?: string | null;
  extraction_instruction: string;
  risk_criteria?: string | null;
  risk_exclusion?: string;
  notes?: string;
}

export interface AuditRecord {
  rule_id: string;
  module: string;
  review_point: string;
  review_type: string;
  paragraph_start: string | number;
  paragraph_end: string | number;
  contract_quote: string;
  extracted_info: Record<string, unknown>;
  risk_level: string;
  risk_description: string;
  suggestion: string;
  refs: { start: number; end: number }[];
}

export interface AuditResponse {
  records: AuditRecord[];
  raw_output?: string;
}

export interface FullAuditResponse {
  modules: Record<string, AuditRecord[]>;
  summary: {
    total_rules: number;
    risk_count: number;
    needs_review_count: number;
    no_risk_count: number;
  };
  raw_output?: string;
}

export interface ParseResult {
  paragraphs: Paragraph[];
  full_text: string;
}
