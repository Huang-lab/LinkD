import axios from 'axios';
import type {
  AgentConfiguration,
  AgentExecution,
  AgentPlan,
  BindingPreloadResponse,
  BindingSearchResponse,
  EHRPreloadResponse,
  ExamplesResponse,
  JsonRecord,
  OverviewResponse,
  PrerunResult,
  ProvidersResponse,
  SelectivityPreloadResponse,
  SelectivitySearchResponse,
} from './types';

const api = axios.create({ baseURL: '/api', timeout: 120_000 });

export const fetchOverview = () =>
  api.get<OverviewResponse>('/overview').then(response => response.data);

export const fetchExamples = () =>
  api.get<ExamplesResponse>('/examples').then(response => response.data);

export const preloadBinding = (params?: {
  page?: number;
  page_size?: number;
  gene_filter?: string;
}) => api.get<BindingPreloadResponse>('/binding/preload', { params }).then(response => response.data);

export const preloadSelectivity = (params?: {
  page?: number;
  page_size?: number;
  type_filter?: string;
  drug_filter?: string;
}) => api.get<SelectivityPreloadResponse>('/selectivity/preload', { params }).then(response => response.data);

export const preloadEHR = (params?: {
  page?: number;
  page_size?: number;
  source?: string;
  drug_filter?: string;
  disease_filter?: string;
  icd_prefix?: string;
  atc_category?: string;
}) => api.get<EHRPreloadResponse>('/ehr/preload', { params }).then(response => response.data);

export const searchBinding = (params: {
  gene: string;
  drug_id: string;
  min_affinity?: number;
}) => api.post<BindingSearchResponse>('/binding/search', params).then(response => response.data);

export const searchSelectivity = (params: {
  drug_id: string;
  selectivity_type: string;
}) => api.post<SelectivitySearchResponse>('/selectivity/search', params).then(response => response.data);

export const generatePlan = (configuration: AgentConfiguration, query: string) =>
  api.post<AgentPlan>('/agent/plan', { ...configuration, query }).then(response => response.data);

export const executePlan = (configuration: AgentConfiguration, plan: AgentPlan) =>
  api.post<AgentExecution>('/agent/execute', {
    ...configuration,
    plan: { query: plan.query, steps: plan.steps },
  }).then(response => response.data);

export const fetchProviders = () =>
  api.get<ProvidersResponse>('/agent/providers').then(response => response.data);

export const fetchPrerun = (name: string) =>
  api.get<PrerunResult>(`/agent/prerun/${encodeURIComponent(name)}`).then(response => response.data);

function csvCell(value: unknown): string {
  const text = value == null
    ? ''
    : typeof value === 'object'
      ? JSON.stringify(value)
      : String(value);
  return `"${text.replaceAll('"', '""')}"`;
}

export function downloadRecordsCSV(
  records: JsonRecord[],
  columns: string[],
  filename: string,
): void {
  if (!records.length || !columns.length) return;
  const rows = [
    columns.map(csvCell).join(','),
    ...records.map(record => columns.map(column => csvCell(record[column])).join(',')),
  ];
  const blob = new Blob([`\uFEFF${rows.join('\n')}\n`], { type: 'text/csv;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

export function apiErrorMessage(error: unknown): string {
  if (axios.isAxiosError<{ detail?: string }>(error)) {
    return error.response?.data?.detail || 'The request could not be completed.';
  }
  return 'The request could not be completed.';
}

export default api;
