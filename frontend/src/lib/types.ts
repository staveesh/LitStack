export type WorkflowStatus = "inbox" | "triaged" | "skim" | "deep_read" | "read" | "citation_only" | "archived";
export type RQStatus = "active" | "partially_answered" | "answered" | "abandoned";
export type ClaimStatus = "hypothesis" | "weak_evidence" | "supported" | "contested" | "rejected";
export type EvidenceType = "supports" | "contradicts" | "qualifies" | "background" | "methodological";
export type OQStatus = "open" | "investigating" | "answered" | "converted_to_experiment" | "abandoned";

export interface Paper {
  id: number;
  title: string;
  authors: string[];
  year: number | null;
  venue: string | null;
  doi: string | null;
  url: string | null;
  abstract: string | null;
  citation_key: string | null;
  workflow_status: WorkflowStatus;
  relevance_score: number | null;
  priority: number | null;
  reading_reason: string | null;
  pdf_path: string | null;
  zotero_key: string | null;
  date_added: string | null;
  created_at: string;
  updated_at: string;
  project_ids?: number[];
  research_question_ids?: number[];
}

export interface Project {
  id: number;
  name: string;
  description: string | null;
  active: boolean;
  created_at: string;
}

export interface ResearchQuestion {
  id: number;
  project_id: number;
  question: string;
  motivation: string | null;
  status: RQStatus;
  notes: string | null;
  created_at: string;
}

export interface ReadingIntent {
  id: number;
  paper_id: number;
  research_question_id: number | null;
  intent: string;
  created_at: string;
  resolved_at: string | null;
  resolution_notes: string | null;
}

export interface PaperExtraction {
  id: number;
  paper_id: number;
  problem: string | null;
  key_idea: string | null;
  approach: string | null;
  architecture: string | null;
  threat_model: string | null;
  assumptions: string[];
  dataset: string | null;
  evaluation_methodology: string | null;
  baselines: string[];
  metrics: string[];
  main_results: string | null;
  limitations: string[];
  future_work: string[];
  relevant_sections: string[];
  important_figures: string[];
  claims_made: string[];
  model_name: string | null;
  prompt_version: string | null;
  confidence: number | null;
  generated_at: string | null;
}

export interface HumanNote {
  id: number;
  paper_id: number;
  why_i_care: string | null;
  what_surprised_me: string | null;
  what_i_dont_believe: string | null;
  relation_to_my_work: string | null;
  what_i_might_cite_this_for: string | null;
  methodological_ideas: string | null;
  unanswered_questions: string | null;
  freeform_notes: string | null;
  updated_at: string;
}

export interface Claim {
  id: number;
  project_id: number;
  claim: string;
  status: ClaimStatus;
  confidence: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface Evidence {
  id: number;
  claim_id: number;
  paper_id: number;
  evidence_type: EvidenceType;
  evidence_text: string;
  source_location: string | null;
  strength: number | null;
  notes: string | null;
}

export interface OpenQuestion {
  id: number;
  project_id: number;
  question: string;
  origin: string | null;
  status: OQStatus;
  importance: number | null;
  notes: string | null;
  created_at: string;
}

export interface TriageResult {
  paper_id: number;
  relevance_score: number;
  recommended_action: "deep_read" | "skim" | "citation_only" | "ignore";
  reason: string;
  related_question_ids: number[];
  suggested_reading_intent: string;
  sections_to_inspect: string[];
  confidence: number;
}
