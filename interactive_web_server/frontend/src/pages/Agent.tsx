import { useEffect, useState } from 'react';
import {
  apiErrorMessage,
  executePlan,
  fetchExamples,
  fetchPrerun,
  fetchProviders,
  generatePlan,
} from '../api/client';
import type {
  AgentConfiguration,
  AgentExample,
  AgentExecution,
  AgentPlan,
  PrerunResult,
  ProvidersResponse,
} from '../api/types';

function buildMarkdown(query: string, plan: AgentPlan, results: AgentExecution): string {
  const lines = [
    '# LinkD Agent Analysis Report',
    '',
    '## Query',
    query,
    '',
    '## Analysis Plan',
  ];
  plan.steps.forEach(step => {
    lines.push(
      `${step.step_number}. ${step.description} (${step.data_sources.join(', ')})`,
    );
  });
  lines.push('', '## Step Results');
  results.steps.forEach(step => {
    lines.push(
      `### ${step.status === 'completed' ? 'Completed' : 'Not completed'} — Step ${step.step_number}: ${step.description}`,
    );
    if (step.result_summary) lines.push(step.result_summary);
    if (step.error) lines.push(`Error: ${step.error}`);
    lines.push('');
  });
  if (results.summary) lines.push('## Analysis Summary', results.summary, '');
  lines.push(
    '---',
    'Research use only. Results are observational and LLM-generated summaries may contain errors.',
  );
  return `${lines.join('\n')}\n`;
}

function downloadFile(content: string, filename: string, mime: string): void {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

const PRERUN_EXAMPLES = [
  { label: 'Vemurafenib-BRAF Analysis', name: 'vemurafenib_braf' },
  { label: 'EGFR Target Landscape', name: 'egfr_landscape' },
];

const QUERY_TYPES = [
  { type: 'Drug-target evidence', example: 'How strong is the evidence that vemurafenib binds to BRAF?', icon: '🔬' },
  { type: 'Drug repurposing', example: 'Could erlotinib be repurposed beyond its current indications?', icon: '💊' },
  { type: 'Target analysis', example: 'Which drugs most potently target EGFR?', icon: '🎯' },
  { type: 'Disease exploration', example: 'Which BRAF-targeted options are linked to melanoma?', icon: '🏥' },
];

export default function Agent() {
  const [mode, setMode] = useState<'free' | 'custom'>('free');
  const [provider, setProvider] = useState('Google Gemini');
  const [model, setModel] = useState('gemini-2.5-flash');
  const [apiKey, setApiKey] = useState('');
  const [message, setMessage] = useState('');
  const [query, setQuery] = useState('');
  const [plan, setPlan] = useState<AgentPlan | null>(null);
  const [results, setResults] = useState<AgentExecution | null>(null);
  const [prerunResult, setPrerunResult] = useState<PrerunResult | null>(null);
  const [loading, setLoading] = useState('');
  const [providers, setProviders] = useState<ProvidersResponse>({});
  const [examples, setExamples] = useState<AgentExample[]>([]);

  useEffect(() => {
    void Promise.all([fetchProviders(), fetchExamples()])
      .then(([providerData, exampleData]) => {
        setProviders(providerData);
        setExamples(exampleData.agent || []);
      })
      .catch(error => setMessage(apiErrorMessage(error)));
  }, []);

  const configuration = (): AgentConfiguration => mode === 'free'
    ? { provider: 'Google Gemini', model: 'gemini-2.5-flash' }
    : { provider, model, api_key: apiKey };

  const doPlan = async () => {
    setLoading('plan');
    setMessage('');
    setResults(null);
    setPrerunResult(null);
    try {
      setPlan(await generatePlan(configuration(), query));
    } catch (error) {
      setPlan(null);
      setMessage(apiErrorMessage(error));
    } finally {
      setLoading('');
    }
  };

  const doExecute = async () => {
    if (!plan) return;
    setLoading('execute');
    setMessage('');
    try {
      setResults(await executePlan(configuration(), plan));
    } catch (error) {
      setMessage(apiErrorMessage(error));
    } finally {
      setLoading('');
    }
  };

  const loadPrerun = async (name: string) => {
    setLoading('prerun');
    setMessage('');
    try {
      setPrerunResult(await fetchPrerun(name));
      setPlan(null);
      setResults(null);
    } catch (error) {
      setMessage(apiErrorMessage(error));
    } finally {
      setLoading('');
    }
  };

  const providerInfo = providers[provider];
  const downloadReport = () => {
    if (plan && results) {
      downloadFile(buildMarkdown(query, plan, results), 'linkd_analysis.md', 'text/markdown');
    }
  };

  return (
    <div>
      <h2 className="text-xl font-bold text-gray-800 mb-2">LinkD-Agent: AI Analysis Agent</h2>
      <div className="bg-amber-50 rounded-lg border border-amber-200 p-4 mb-4 text-xs text-amber-900">
        <strong>Research use only.</strong> LinkD reports observational evidence, not causal or
        clinical conclusions. LLM plans and summaries can be incomplete or incorrect; verify all
        outputs against the cited source records.
      </div>

      <div className="bg-blue-50 rounded-lg border border-blue-200 p-5 mb-6">
        <h3 className="text-sm font-bold text-[#2171B5] mb-2">What can LinkD-Agent do?</h3>
        <p className="text-xs text-gray-600 mb-3">
          It creates a bounded plan across LinkD binding, EHR, drug-response, and clinical-trial
          tables, then executes that plan against the read-only database.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {QUERY_TYPES.map(item => (
            <div key={item.type} className="bg-white rounded-lg p-3 border border-blue-100">
              <div className="text-lg mb-1">{item.icon}</div>
              <div className="text-xs font-semibold text-gray-700 mb-1">{item.type}</div>
              <div className="text-xs text-gray-400 italic">“{item.example}”</div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4 shadow-sm">
        <h3 className="text-sm font-semibold text-gray-700 mb-1">Pre-run examples</h3>
        <p className="text-xs text-gray-400 mb-3">Fixed, repository-supplied examples; no API key required.</p>
        <div className="flex flex-wrap gap-2">
          {PRERUN_EXAMPLES.map(example => (
            <button
              key={example.name}
              onClick={() => void loadPrerun(example.name)}
              disabled={loading === 'prerun'}
              className="px-4 py-2 bg-gray-50 border border-gray-300 rounded-lg text-sm hover:bg-[#2171B5] hover:text-white transition-colors"
            >
              {example.label} &rarr;
            </button>
          ))}
        </div>
      </div>

      {prerunResult && !prerunResult.error && (
        <div className="bg-white rounded-lg border border-gray-200 p-5 mb-4 shadow-sm">
          <div className="text-xs text-gray-400 mb-2">Pre-run example result</div>
          <h3 className="text-sm font-semibold text-gray-700">Query: {prerunResult.query}</h3>
          {prerunResult.plan_html && (
            <div className="mt-3" dangerouslySetInnerHTML={{ __html: prerunResult.plan_html }} />
          )}
          <div className="text-xs text-gray-500 my-2">{prerunResult.execution_status}</div>
          {prerunResult.results_html && (
            <div className="mt-3" dangerouslySetInnerHTML={{ __html: prerunResult.results_html }} />
          )}
        </div>
      )}

      <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4 shadow-sm">
        <h3 className="text-sm font-semibold text-gray-700 mb-3">Run your own query</h3>
        <div className="flex gap-2 mb-3">
          <button
            onClick={() => {
              setMode('free');
              setProvider('Google Gemini');
              setModel('gemini-2.5-flash');
            }}
            className={`px-4 py-1.5 text-xs rounded-full border ${mode === 'free' ? 'bg-[#238B45] text-white' : 'bg-white text-gray-600'}`}
          >
            Server-configured Gemini
          </button>
          <button
            onClick={() => setMode('custom')}
            className={`px-4 py-1.5 text-xs rounded-full border ${mode === 'custom' ? 'bg-[#2171B5] text-white' : 'bg-white text-gray-600'}`}
          >
            Your API key
          </button>
        </div>

        {mode === 'free' ? (
          <p className="text-xs text-gray-500 mb-3">
            Uses the server-configured Gemini key when available.
          </p>
        ) : (
          <div className="flex flex-wrap gap-3 items-end mb-3">
            <label className="text-xs text-gray-600">
              Provider
              <select
                value={provider}
                onChange={event => {
                  const selected = event.target.value;
                  setProvider(selected);
                  if (providers[selected]) setModel(providers[selected].default);
                }}
                className="block mt-1 px-3 py-2 border rounded-md text-sm w-44 bg-white"
              >
                {Object.keys(providers).map(name => <option key={name}>{name}</option>)}
              </select>
            </label>
            <label className="text-xs text-gray-600">
              Model
              <select
                value={model}
                onChange={event => setModel(event.target.value)}
                className="block mt-1 px-3 py-2 border rounded-md text-sm w-56 bg-white"
              >
                {(providerInfo?.models || []).map(name => <option key={name}>{name}</option>)}
              </select>
            </label>
            <label className="text-xs text-gray-600">
              API key
              <input
                type="password"
                autoComplete="off"
                value={apiKey}
                onChange={event => setApiKey(event.target.value)}
                placeholder="Held in this page only"
                className="block mt-1 px-3 py-2 border rounded-md text-sm w-56"
              />
            </label>
          </div>
        )}
        <p className="text-xs text-gray-400 mb-3">
          API keys remain in this browser page and the individual HTTPS request. LinkD does not
          retain them in server state.
        </p>

        <div className="flex flex-wrap gap-2 mb-3">
          <span className="text-xs font-semibold text-gray-500 self-center">Try:</span>
          {examples.map(example => (
            <button
              key={example.label}
              onClick={() => setQuery(example.query)}
              className="px-3 py-1 text-xs bg-gray-50 border rounded-full hover:bg-[#2171B5] hover:text-white"
            >
              {example.label}
            </button>
          ))}
        </div>
        <textarea
          value={query}
          maxLength={2_000}
          onChange={event => setQuery(event.target.value)}
          rows={3}
          placeholder="e.g., How strong is the evidence that vemurafenib binds to BRAF?"
          className="w-full px-3 py-2 border rounded-md text-sm resize-y mb-1"
        />
        <div className="text-right text-xs text-gray-400 mb-2">{query.length}/2,000</div>
        <div className="flex gap-2">
          <button
            onClick={() => void doPlan()}
            disabled={Boolean(loading) || !query.trim()}
            className="px-5 py-2 bg-[#2171B5] text-white rounded-md text-sm disabled:opacity-50"
          >
            {loading === 'plan' ? 'Generating…' : 'Generate plan'}
          </button>
          <button
            onClick={() => void doExecute()}
            disabled={Boolean(loading) || !plan}
            className="px-5 py-2 bg-gray-600 text-white rounded-md text-sm disabled:opacity-50"
          >
            {loading === 'execute' ? 'Executing…' : 'Execute plan'}
          </button>
        </div>
        {message && <p role="alert" className="text-xs text-red-600 mt-3">{message}</p>}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {plan && (
          <div className="bg-white rounded-lg border p-4 shadow-sm">
            <h3 className="text-sm font-semibold text-gray-700 mb-2">Plan steps</h3>
            <ol className="space-y-2">
              {plan.steps.map(step => (
                <li key={step.step_number} className="text-sm">
                  <div className="font-medium text-gray-700">
                    {step.step_number}. {step.description}
                  </div>
                  <div className="text-xs text-gray-400">{step.data_sources.join(', ')}</div>
                </li>
              ))}
            </ol>
          </div>
        )}

        {results && (
          <div className="lg:col-span-2 bg-white rounded-lg border p-4 shadow-sm">
            <h3 className="text-sm font-semibold text-gray-700 mb-2">Results</h3>
            <div className="mb-3 text-xs text-gray-500">
              {results.steps.filter(step => step.status === 'completed').length}/{results.steps.length} steps completed
            </div>
            {results.steps.map(step => (
              <div key={step.step_number} className="mb-3 p-3 bg-gray-50 rounded border">
                <div className="text-sm font-medium">{step.description}</div>
                {step.result_summary && <p className="text-xs text-gray-600 mt-1 whitespace-pre-wrap">{step.result_summary}</p>}
                {step.error && <p className="text-xs text-red-500 mt-1">{step.error}</p>}
              </div>
            ))}
            {results.summary && (
              <div className="mt-4 p-4 bg-blue-50 rounded border border-blue-200">
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Analysis summary</h4>
                <p className="text-sm text-gray-700 whitespace-pre-wrap">{results.summary}</p>
              </div>
            )}
            <button
              onClick={downloadReport}
              className="mt-3 px-3 py-1 text-xs bg-gray-100 rounded border"
            >
              Download report
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
