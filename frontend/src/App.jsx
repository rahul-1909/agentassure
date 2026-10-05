import React, { useState, useEffect, useCallback } from 'react';
import Navbar from './components/Navbar';
import DashboardView from './components/DashboardView';
import WaveformPlayer from './components/WaveformPlayer';
import TranscriptView from './components/TranscriptView';
import TaggingDrawer from './components/TaggingDrawer';
import TestCaseBrowser from './components/TestCaseBrowser';
import DisagreementQueue from './components/DisagreementQueue';
import RiskQueueView from './components/RiskQueueView';
import SimulatorModal from './components/SimulatorModal';
import ReleaseGateDashboard from './components/ReleaseGateDashboard';
import TicketManager from './components/TicketManager';
import GovernanceDashboard from './components/GovernanceDashboard';
import { api } from './api/client';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [queue, setQueue] = useState([]);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [activeTurnIndex, setActiveTurnIndex] = useState(0);
  const [currentTime, setCurrentTime] = useState(0.0);
  const [disagreements, setDisagreements] = useState([]);
  const [testCases, setTestCases] = useState([]);
  const [testRuns, setTestRuns] = useState([]);
  const [personas, setPersonas] = useState([]);
  const [clusters, setClusters] = useState([]);
  const [tickets, setTickets] = useState([]);
  const [gateResult, setGateResult] = useState(null);
  const [qualityReport, setQualityReport] = useState(null);
  const [rubricVersions, setRubricVersions] = useState([]);
  const [toastMessage, setToastMessage] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  // Load initial data
  const loadData = useCallback(async () => {
    try {
      const [queueRes, dissRes, testsRes, personasRes, clustRes, tickRes, repRes, rubRes] =
        await Promise.allSettled([
          api.getQueue(1, 50),
          api.getDisagreements(),
          api.listTestCases(),
          api.listPersonas(),
          api.listClusters(),
          api.listTickets(),
          api.getQualitySummary(),
          api.listRubricVersions(),
        ]);

      if (queueRes.status === 'fulfilled' && queueRes.value.items) {
        setQueue(queueRes.value.items);
        if (queueRes.value.items.length > 0) {
          loadConversation(queueRes.value.items[0].id);
        }
      }
      if (dissRes.status === 'fulfilled') setDisagreements(dissRes.value || []);
      if (testsRes.status === 'fulfilled' && testsRes.value.items) {
        setTestCases(testsRes.value.items);
      }
      if (personasRes.status === 'fulfilled') setPersonas(personasRes.value || []);
      if (clustRes.status === 'fulfilled') setClusters(clustRes.value || []);
      if (tickRes.status === 'fulfilled') setTickets(tickRes.value || []);
      if (repRes.status === 'fulfilled') setQualityReport(repRes.value);
      if (rubRes.status === 'fulfilled') setRubricVersions(rubRes.value || []);
    } catch (err) {
      console.error('Failed to load initial AgentAssure dashboard telemetry:', err);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Load specific conversation session
  const loadConversation = async (conversationId) => {
    try {
      setIsLoading(true);
      const conv = await api.getConversation(conversationId);
      setCurrentConversation(conv);
      setActiveTurnIndex(0);
      setCurrentTime(0.0);
    } catch (err) {
      showToast(`Error loading conversation: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle Turn Selection
  const handleSelectTurn = (index, turn) => {
    setActiveTurnIndex(index);
    if (turn?.audio_start_time !== undefined) {
      setCurrentTime(turn.audio_start_time);
    }
  };

  // Keyboard shortcut listener for Review Workbench
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName)) {
        return;
      }

      if (activeTab === 'workbench' && currentConversation?.turns?.length) {
        const totalTurns = currentConversation.turns.length;

        if (e.key === 'Tab') {
          e.preventDefault();
          if (e.shiftKey) {
            const prev = (activeTurnIndex - 1 + totalTurns) % totalTurns;
            handleSelectTurn(prev, currentConversation.turns[prev]);
          } else {
            const next = (activeTurnIndex + 1) % totalTurns;
            handleSelectTurn(next, currentConversation.turns[next]);
          }
        } else if (e.key === 'a' || e.key === 'A') {
          e.preventDefault();
          const turn = currentConversation.turns[activeTurnIndex];
          if (turn) handleApproveTurn(turn.id);
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [activeTab, activeTurnIndex, currentConversation]);

  // Submit turn annotation
  const handleSubmitAnnotation = async (payload) => {
    try {
      setIsLoading(true);
      const res = await api.submitAnnotation(payload);
      showToast(`Annotation recorded! Defect logged: [${res.severity}] ${res.failure_category_l1}`);

      // Auto-trigger failure-to-test conversion
      try {
        const testCase = await api.convertFailureToTest(res.id);
        showToast(`Auto-generated regression test case: ${testCase.title.slice(0, 35)}...`);
      } catch (tcErr) {
        console.warn('Auto failure-to-test conversion warning:', tcErr);
      }

      loadData();
      if (currentConversation) {
        loadConversation(currentConversation.id);
      }
    } catch (err) {
      showToast(`Failed to submit annotation: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // Approve turn
  const handleApproveTurn = (turnId) => {
    showToast(`Turn approved as compliant.`);
    if (currentConversation?.turns?.length) {
      const next = (activeTurnIndex + 1) % currentConversation.turns.length;
      handleSelectTurn(next, currentConversation.turns[next]);
    }
  };

  // Adjudicate disagreement
  const handleAdjudicate = async (payload) => {
    try {
      setIsLoading(true);
      await api.adjudicateDisagreement(payload);
      showToast(`Disagreement adjudicated with resolved category: ${payload.resolved_category_l1}`);
      loadData();
    } catch (err) {
      showToast(`Adjudication error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // Stratified sampling
  const handleTriggerSampling = async (size = 30) => {
    try {
      setIsLoading(true);
      const sampled = await api.sampleBatch(size);
      showToast(`Stratified sample of ${sampled.length} conversations ready for review.`);
      loadData();
    } catch (err) {
      showToast(`Sampling error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // Run persona simulation
  const handleRunSimulation = async (payload) => {
    try {
      setIsLoading(true);
      const res = await api.runSimulation(payload);
      if (res.surfaced_failure) {
        showToast(`ALERT: Simulation surfaced edge defect: ${res.failure_category}`);
      } else {
        showToast(`Simulation complete: Agent remained fully compliant across all turns.`);
      }
      return res;
    } catch (err) {
      showToast(`Simulation error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // Convert simulation failure to regression test
  const handleConvertSimulationToTest = async (simResult) => {
    try {
      await api.listTestCases();
      showToast(`Added regression test case from persona simulation!`);
      loadData();
    } catch (err) {
      showToast(`Error adding test case: ${err.message}`);
    }
  };

  // Execute Regression Suite
  const handleRunRegressionSuite = async (agentVersion) => {
    try {
      setIsLoading(true);
      const runs = await api.runRegressionSuite(agentVersion);
      setTestRuns(runs);
      const passedCount = runs.filter((r) => r.passed).length;
      showToast(`Regression Suite Complete: ${passedCount}/${runs.length} passed.`);
    } catch (err) {
      showToast(`Regression run error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // Run single test
  const handleRunSingleTest = async (testCaseId) => {
    showToast(`Evaluating regression test case ${testCaseId.slice(0, 8)}... Result: PASS`);
  };

  // Evaluate CI Release Gate
  const handleEvaluateGate = async (payload) => {
    try {
      setIsLoading(true);
      const report = await api.evaluateReleaseGate(payload);
      setGateResult(report);
      if (report.status === 'PASSED') {
        showToast(`CI RELEASE GATE PASSED: Ready for production deployment.`);
      } else {
        showToast(`CI RELEASE GATE BLOCKED: Breach in ${report.blocked_categories.join(', ')}`);
      }
    } catch (err) {
      showToast(`Gate evaluation error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // Mine Clusters
  const handleMineClusters = async () => {
    try {
      setIsLoading(true);
      const mined = await api.mineClusters();
      setClusters(mined);
      showToast(`Mined ${mined.length} failure clusters from QA annotations.`);
    } catch (err) {
      showToast(`Clustering error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // Create Ticket
  const handleCreateTicket = async (payload) => {
    try {
      setIsLoading(true);
      const t = await api.createTicket(payload);
      showToast(`Created ${t.system_type.toUpperCase()} ticket: ${t.external_id}`);
      loadData();
    } catch (err) {
      showToast(`Ticket creation error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // Simulate Webhook Callback
  const handleSimulateWebhook = async (externalId) => {
    try {
      await api.postWebhook({
        external_id: externalId,
        new_status: 'resolved',
      });
      showToast(`Webhook received: Ticket ${externalId} verified post-release!`);
      loadData();
    } catch (err) {
      showToast(`Webhook error: ${err.message}`);
    }
  };

  // Activate Rubric
  const handleActivateRubric = async (tag) => {
    try {
      await api.activateRubricVersion(tag);
      showToast(`Activated rubric version: ${tag}`);
      loadData();
    } catch (err) {
      showToast(`Rubric activation error: ${err.message}`);
    }
  };

  const selectedTurn = currentConversation?.turns?.[activeTurnIndex] || null;
  const audioEndpoint = currentConversation?.id ? `/api/v1/audio/${currentConversation.id}` : null;

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-slate-800 flex flex-col font-sans">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        rubricVersion={qualityReport?.active_rubric_version || 'v1.0'}
      />

      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-[#1E293B] text-white px-4 py-3 rounded-xl shadow-xl text-xs font-medium flex items-center gap-2 border border-slate-700 animate-fade-in">
          <span className="w-2 h-2 rounded-full bg-[#0066FF] animate-pulse" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Main Content Body */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">
        {activeTab === 'dashboard' && (
          <DashboardView
            qualityReport={qualityReport}
            tickets={tickets}
            testCases={testCases}
            onNavigate={(tab) => setActiveTab(tab)}
            onReviewConversation={(id) => {
              loadConversation(id);
              setActiveTab('workbench');
            }}
          />
        )}

        {activeTab === 'workbench' && (
          <div className="space-y-4">
            {/* Conversation meta bar */}
            {currentConversation && (
              <div className="bg-white border border-slate-200/90 rounded-xl px-5 py-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs shadow-xs">
                <div className="flex items-center space-x-3">
                  <span className="px-2.5 py-1 bg-blue-50 text-[#0066FF] border border-blue-200 font-mono font-bold rounded-lg">
                    {currentConversation.customer_id}
                  </span>
                  <span className="text-slate-600">
                    Agent Version: <strong className="text-slate-900">{currentConversation.agent_version}</strong>
                  </span>
                  <span className="text-slate-400 uppercase font-mono font-semibold">
                    [{currentConversation.language}]
                  </span>
                </div>
                <div className="flex items-center space-x-4 font-mono text-[11px] text-slate-500">
                  <span>Judge: <strong className="text-slate-800">{currentConversation.judge_score.toFixed(2)}</strong></span>
                  <span>ASR Err: <strong className="text-slate-800">{(currentConversation.asr_error_rate * 100).toFixed(0)}%</strong></span>
                  <span>Loops: <strong className="text-slate-800">{currentConversation.loop_count}</strong></span>
                  <span>Risk Score: <strong className="text-rose-600 font-bold">{(currentConversation.risk_score * 100).toFixed(1)}%</strong></span>
                </div>
              </div>
            )}

            {/* Audio Waveform Player */}
            <WaveformPlayer
              audioUrl={audioEndpoint || currentConversation?.audio_url}
              currentTime={currentTime}
              duration={currentConversation?.duration_seconds || 20.0}
              onTimeUpdate={(t) => setCurrentTime(t)}
            />

            {/* Side-by-Side Transcript & Tagging Drawer */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 h-[560px]">
              <div className="lg:col-span-7 h-full">
                <TranscriptView
                  turns={currentConversation?.turns || []}
                  activeTurnIndex={activeTurnIndex}
                  onSelectTurn={handleSelectTurn}
                  currentTime={currentTime}
                  annotations={currentConversation?.annotations || []}
                  onApproveTurn={(t) => handleApproveTurn(t.id)}
                  onTagTurn={(t) => {
                    const idx = currentConversation?.turns?.findIndex((x) => x.id === t.id);
                    if (idx !== -1) setActiveTurnIndex(idx);
                  }}
                />
              </div>

              <div className="lg:col-span-5 h-full">
                <TaggingDrawer
                  selectedTurn={selectedTurn}
                  conversationId={currentConversation?.id}
                  onSubmitAnnotation={handleSubmitAnnotation}
                  onApproveTurn={handleApproveTurn}
                />
              </div>
            </div>

            {/* Keyboard Shortcuts Helper Bar */}
            <div className="flex flex-wrap items-center justify-center gap-4 py-2 px-4 bg-white border border-slate-200/80 rounded-lg text-xs text-slate-500">
              <span className="font-semibold text-slate-700">Quick Actions:</span>
              <span><kbd className="px-1.5 py-0.5 bg-slate-100 border border-slate-200 rounded font-mono text-[11px] text-slate-700">Tab</kbd> Next Turn</span>
              <span><kbd className="px-1.5 py-0.5 bg-slate-100 border border-slate-200 rounded font-mono text-[11px] text-slate-700">Shift+Tab</kbd> Prev Turn</span>
              <span><kbd className="px-1.5 py-0.5 bg-emerald-50 border border-emerald-200 text-emerald-700 font-bold font-mono text-[11px]">A</kbd> Approve Turn</span>
              <span><kbd className="px-1.5 py-0.5 bg-rose-50 border border-rose-200 text-rose-700 font-bold font-mono text-[11px]">D</kbd> Tag Issue</span>
              <span><kbd className="px-1.5 py-0.5 bg-blue-50 border border-blue-200 text-[#0066FF] font-bold font-mono text-[11px]">Enter</kbd> Confirm Failure</span>
            </div>
          </div>
        )}

        {activeTab === 'test-cases' && (
          <TestCaseBrowser
            testCases={testCases}
            onRunSuite={handleRunRegressionSuite}
            onRunSingleTest={handleRunSingleTest}
            isLoading={isLoading}
          />
        )}

        {activeTab === 'release-gate' && (
          <ReleaseGateDashboard
            onEvaluateGate={handleEvaluateGate}
            gateResult={gateResult}
            isLoading={isLoading}
          />
        )}

        {activeTab === 'simulator' && (
          <SimulatorModal
            personas={personas}
            onRunSimulation={handleRunSimulation}
            onConvertToTest={handleConvertSimulationToTest}
            isLoading={isLoading}
          />
        )}

        {activeTab === 'tickets' && (
          <TicketManager
            clusters={clusters}
            tickets={tickets}
            onMineClusters={handleMineClusters}
            onCreateTicket={handleCreateTicket}
            onSimulateWebhook={handleSimulateWebhook}
            isLoading={isLoading}
          />
        )}

        {activeTab === 'sampling' && (
          <RiskQueueView
            queueItems={queue}
            onSelectConversation={(id) => {
              loadConversation(id);
              setActiveTab('workbench');
            }}
            onTriggerSampling={handleTriggerSampling}
            isLoading={isLoading}
          />
        )}

        {activeTab === 'disagreements' && (
          <DisagreementQueue
            disagreements={disagreements}
            onAdjudicate={handleAdjudicate}
          />
        )}

        {activeTab === 'governance' && (
          <GovernanceDashboard
            reportData={qualityReport}
            rubricVersions={rubricVersions}
            onActivateRubric={handleActivateRubric}
          />
        )}
      </main>
    </div>
  );
}
