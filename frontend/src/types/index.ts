export interface Paragraph {
  id: number;
  text: string;
  page?: number;
}

export interface Rule {
  id: string;
  risk_element: string;
  explanation: string;
  risk_exclusion?: string;
}

export interface AuditRecord {
  risk_element: string;
  paragraph_start: string | number;
  paragraph_end: string | number;
  original_text: string;
  conclusion_and_reason: string;
  risk_level?: string;
  refs: { start: number; end: number }[];
}

export interface AuditResponse {
  records: AuditRecord[];
  raw_output?: string;
}

export interface ParseResult {
  paragraphs: Paragraph[];
  full_text: string;
  file_id: string;
}
