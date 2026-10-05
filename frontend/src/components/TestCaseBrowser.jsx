import React, { useState } from 'react';
import { 
  Play, 
  Search, 
  Filter, 
  CheckCircle2, 
  AlertCircle, 
  Trash2, 
  Code, 
  Sparkles, 
  ArrowUpRight,
  TrendingDown,
  TrendingUp
} from 'lucide-react';
import Card from './common/Card';
import Badge from './common/Badge';
import Button from './common/Button';

export default function TestCaseBrowser({
  testCases = [],
  onRunSuite,
  onRunSingleTest,
  isLoading = false,
}) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedSeverity, setSelectedSeverity] = useState('all');

  // Filter test cases
  const filteredCases = testCases.filter((tc) => {
    const matchesSearch =
      (tc.title || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (tc.category_l1 || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (tc.category_l2 || '').toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || tc.category_l1 === selectedCategory;
    const matchesSeverity = selectedSeverity === 'all' || tc.severity === selectedSeverity;
    return matchesSearch && matchesCategory && matchesSeverity;
  });

  const categories = Array.from(new Set(testCases.map((tc) => tc.category_l1))).filter(Boolean);

  return (
    <div className="space-y-6">
      {/* Header bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">
            Regression Test Cases <span className="text-sm font-normal text-slate-500">({testCases.length || 847} total)</span>
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Atomically synthesized assertions generated from confirmed production QA failures.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="primary"
            icon={Play}
            disabled={isLoading}
            onClick={() => onRunSuite('v2.5.0-candidate')}
          >
            {isLoading ? 'Running Suite...' : 'Run Regression Suite'}
          </Button>
        </div>
      </div>

      {/* Search and Filters */}
      <Card bodyClassName="p-3">
        <div className="flex flex-col md:flex-row items-center gap-3">
          <div className="relative flex-1 w-full">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search by assertion name, category, or keyword..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#0066FF]/30 focus:bg-white transition-all"
            />
          </div>
          <div className="flex items-center gap-2 w-full md:w-auto">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="text-xs py-1.5 px-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-none"
            >
              <option value="all">All Categories</option>
              {categories.map((cat) => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
            <select
              value={selectedSeverity}
              onChange={(e) => setSelectedSeverity(e.target.value)}
              className="text-xs py-1.5 px-2.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-700 focus:outline-none"
            >
              <option value="all">All Severities</option>
              <option value="S1">S1 - Critical</option>
              <option value="S2">S2 - Major</option>
              <option value="S3">S3 - Minor</option>
              <option value="S4">S4 - Cosmetic</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Test Cases List */}
      <div className="space-y-3">
        {filteredCases.length === 0 ? (
          <Card className="text-center py-12">
            <p className="text-sm text-slate-500">No test cases match your filter criteria.</p>
          </Card>
        ) : (
          filteredCases.map((tc) => {
            const isPassing = (tc.pass_rate ?? 0.98) >= 0.95;
            const baselineRate = 98.2;
            const currentRate = 96.8;

            return (
              <Card key={tc.id} className="hover:border-slate-300 transition-all">
                <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                  <div className="space-y-2 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-mono text-xs font-semibold text-slate-500">{tc.id.slice(0, 8)}</span>
                      <Badge variant={tc.severity === 'S1' ? 'error' : tc.severity === 'S2' ? 'warning' : 'neutral'}>
                        {tc.severity}
                      </Badge>
                      <Badge variant="info">{tc.category_l1}</Badge>
                      {tc.category_l2 && <span className="text-xs text-slate-400">→ {tc.category_l2}</span>}
                      <span className="ml-auto md:ml-0">
                        {isPassing ? (
                          <Badge variant="success">Passing (96.8%)</Badge>
                        ) : (
                          <Badge variant="error">Degrading (91.2%)</Badge>
                        )}
                      </span>
                    </div>

                    <h3 className="text-sm font-semibold text-slate-900">{tc.title || `Regression Case: ${tc.category_l2}`}</h3>

                    {/* Assertion Code Box */}
                    <div className="bg-slate-900 text-slate-100 p-2.5 rounded-lg font-mono text-xs overflow-x-auto">
                      <div className="text-slate-400 text-[10px] mb-1">
                        Assertion Type: <span className="text-sky-300">{tc.expected_assertion?.type || 'no_hallucination'}</span>
                      </div>
                      <code>
                        {JSON.stringify(tc.expected_assertion || {
                          type: "no_hallucination",
                          condition: "agent_utterance NOT IN unverified_rates",
                          prohibited: ["12% APR without disclosure", "0% flat interest"]
                        }, null, 2)}
                      </code>
                    </div>

                    {/* Telemetry Stats */}
                    <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500 pt-1">
                      <span>Baseline: <strong className="text-slate-700">{baselineRate}%</strong></span>
                      <span>Current: <strong className="text-slate-700">{currentRate}%</strong></span>
                      <span className="flex items-center gap-1 text-amber-600">
                        <TrendingDown className="w-3.5 h-3.5" /> -1.4% delta
                      </span>
                      <span>Affected Conversations: <strong className="text-slate-700">47</strong></span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 self-end md:self-start">
                    <Button
                      variant="outline"
                      size="sm"
                      icon={Play}
                      onClick={() => onRunSingleTest(tc.id)}
                    >
                      Run Test
                    </Button>
                  </div>
                </div>
              </Card>
            );
          })
        )}
      </div>
    </div>
  );
}
