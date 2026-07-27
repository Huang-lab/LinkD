export type JsonRecord = Record<string, unknown>;

export interface StatCardData {
  label: string;
  value: number;
  color: string;
}

export interface OverviewResponse {
  cards: StatCardData[];
  charts: {
    sources: { source: string; count: number }[];
    phases: { phase: string; count: number }[];
    top_genes: { gene: string; count: number }[];
    roles: { role: string; count: number }[];
  };
  sources_table: { dataset: string; rows: number; columns: number }[];
  data_version: string;
  data_loaded_at: string;
  source_versions: Record<string, string>;
}

export interface BindingGene {
  gene: string;
  drug_count: number;
  avg_pkd: number | null;
  max_pkd: number | null;
  n_hit: number | null;
  tpi: number | null;
}

export interface BindingPreloadResponse {
  genes: BindingGene[];
  total: number;
  page: number;
  page_size: number;
  filters?: { phases: number[] };
}

export interface BindingSearchResponse {
  error?: string;
  stats: {
    avg_pkd: number | null;
    max_pkd: number | null;
    drug_hits: number | null;
    tpi: number | null;
  } | null;
  landscape: { drug: string; affinity: number; selectivity: number }[];
  radar: {
    categories: string[];
    values: number[];
    overall_strength: string;
  } | null;
  table: JsonRecord[];
  table_columns: string[];
}

export interface SelectivityTrace {
  type: string;
  color: string;
  x: number[];
  y: number[];
  drugs: string[];
}

export interface SelectivityPreloadResponse {
  umap: { traces: SelectivityTrace[]; highlight: null } | null;
  type_distribution: Record<string, number>;
  drugs: JsonRecord[];
  drug_columns: string[];
  total: number;
  page: number;
  page_size: number;
}

export interface SelectivitySearchResponse {
  error?: string;
  info: {
    drug: string;
    selectivity_score: number | null;
    drug_type: string | null;
    n_targets: number | null;
  } | null;
  bars: { target: string; affinity: number }[];
  umap: {
    traces: SelectivityTrace[];
    highlight: { x: number; y: number; drug: string } | null;
  } | null;
  table: JsonRecord[];
  table_columns: string[];
}

export interface EHRPoint {
  or_value: number;
  neg_log_p: number;
  drug_name: string;
  disease: string;
  icd10: string;
  source: string;
}

export interface EHRPreloadResponse {
  associations: JsonRecord[];
  columns: string[];
  total: number;
  total_raw: number;
  page: number;
  page_size: number;
  forest: EHRPoint[];
  disease_categories: { prefix: string; label: string; count: number }[];
  drug_categories: { category: string; count: number }[];
}

export interface AgentExample {
  label: string;
  query: string;
}

export interface ExamplesResponse {
  agent: AgentExample[];
}

export interface ProviderInfo {
  key: string;
  models: string[];
  default: string;
}

export type ProvidersResponse = Record<string, ProviderInfo>;

export interface AgentConfiguration {
  provider: string;
  model: string;
  api_key?: string;
}

export interface AgentPlanStep {
  step_number: number;
  description: string;
  data_sources: string[];
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  error?: string | null;
  result_summary?: string;
}

export interface AgentPlan {
  status: 'ok';
  query: string;
  steps: AgentPlanStep[];
}

export interface AgentExecution {
  status: 'ok';
  query: string;
  steps: AgentPlanStep[];
  summary: string;
  overall_status: string;
}

export interface PrerunResult {
  query?: string;
  plan_html?: string;
  execution_status?: string;
  results_html?: string;
  error?: string;
}
