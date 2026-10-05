/**
 * AgentAssure API Client for REST Backend Communication.
 */

const BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

async function request(endpoint, options = {}) {
  const url = endpoint.startsWith('http') ? endpoint : `${BASE_URL}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  const response = await fetch(url, { ...options, headers });
  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(errorBody.detail || `HTTP Error ${response.status}`);
  }
  return response.json();
}

export const api = {
  // Health
  getHealth: () => request('/health', { baseURL: '' }),
  getMetrics: () => request('/metrics', { baseURL: '' }),

  // Smart Sampling & Review Queue
  getQueue: (page = 1, pageSize = 50, reviewStatus = 'pending', language = '') => {
    let q = `/sampling/queue?page=${page}&page_size=${pageSize}`;
    if (reviewStatus) q += `&review_status=${reviewStatus}`;
    if (language) q += `&language=${language}`;
    return request(q);
  },
  sampleBatch: (targetBatchSize = 50, latestVersion = 'v2.5.0') =>
    request(`/sampling/sample?target_batch_size=${targetBatchSize}&latest_version=${latestVersion}`, {
      method: 'POST',
    }),
  ingestConversation: (payload) =>
    request('/sampling/ingest', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  // Review Workbench
  startReviewSession: (conversationId) =>
    request(`/review/session/start/${conversationId}`, { method: 'POST' }),
  getConversation: (conversationId) => request(`/review/conversation/${conversationId}`),
  submitAnnotation: (payload) =>
    request('/review/annotation', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  getDisagreements: () => request('/review/disagreements'),
  adjudicateDisagreement: (payload) =>
    request('/review/adjudicate', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  getReviewerMetrics: (reviewerId) => request(`/review/metrics/${reviewerId}`),

  // Failure-to-Test Pipeline
  convertFailureToTest: (annotationId, title = '') => {
    let url = `/failures/convert/${annotationId}`;
    if (title) url += `?title=${encodeURIComponent(title)}`;
    return request(url, { method: 'POST' });
  },
  listTestCases: (categoryL1 = '', severity = '') => {
    let q = '/failures/tests';
    const params = [];
    if (categoryL1) params.push(`category_l1=${encodeURIComponent(categoryL1)}`);
    if (severity) params.push(`severity=${encodeURIComponent(severity)}`);
    if (params.length) q += `?${params.join('&')}`;
    return request(q);
  },
  runRegressionSuite: (agentVersion = 'v2.5.0-candidate', commitHash = 'head-sha') =>
    request(`/failures/tests/run?agent_version=${encodeURIComponent(agentVersion)}&commit_hash=${encodeURIComponent(commitHash)}`, {
      method: 'POST',
    }),

  // Persona Simulator
  listPersonas: () => request('/simulator/personas'),
  runSimulation: (payload) =>
    request('/simulator/run', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  listSimulationRuns: (limit = 50) => request(`/simulator/runs?limit=${limit}`),

  // Release Gating
  evaluateReleaseGate: (payload) =>
    request('/release-gate/evaluate', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  // Closed-Loop Ticketing
  mineClusters: () => request('/tickets/cluster', { method: 'POST' }),
  listClusters: () => request('/tickets/clusters'),
  createTicket: (payload) =>
    request('/tickets/create', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  listTickets: () => request('/tickets'),
  postWebhook: (payload) =>
    request('/tickets/webhook', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  // Quality Reporting & Governance
  getQualitySummary: () => request('/reports/summary'),
  listRubricVersions: () => request('/reports/rubrics'),
  activateRubricVersion: (versionTag) =>
    request(`/reports/rubrics/activate/${versionTag}`, { method: 'POST' }),
  getAuditLogs: (limit = 50) => request(`/reports/audit-logs?limit=${limit}`),
};
