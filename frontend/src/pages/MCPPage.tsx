import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/shared/ui/card';
import { Button } from '../components/shared/ui/button';
import { Badge } from '../components/shared/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/shared/ui/tabs';
import { Search, Shield, BookOpen, Database, Play, CheckCircle2, AlertTriangle, Layers, Award, Info, Scale, ArrowRight } from 'lucide-react';

export const MCPPage: React.FC = () => {
  // Tool testing states
  const [activeSubTab, setActiveSubTab] = useState<'validator' | 'tools' | 'knowledge' | 'presentation'>('validator');

  // Tool 1: search_clause_library
  const [clauseQuery, setClauseQuery] = useState('Payment is due within sixty (60) days of invoice receipt.');
  const [clauseType, setClauseType] = useState('Payment Terms');
  const [clauseSearchResult, setClauseSearchResult] = useState<string | null>(null);
  const [searchingClause, setSearchingClause] = useState(false);

  // Tool 2: get_playbook_rule
  const [selectedRule, setSelectedRule] = useState('confidentiality_survival_minimum');
  const [ruleClauseType, setRuleClauseType] = useState('Survival');
  const [playbookResult, setPlaybookResult] = useState<string | null>(null);
  const [fetchingRule, setFetchingRule] = useState(false);

  // Tool 3: search_prior_approved_clauses
  const [precedentQuery, setPrecedentQuery] = useState('liability limited to fees paid in preceding 12 months');
  const [precedentContractType, setPrecedentContractType] = useState('MSA');
  const [precedentResult, setPrecedentResult] = useState<string | null>(null);
  const [searchingPrecedent, setSearchingPrecedent] = useState(false);

  // Tool 4: fetch_metadata
  const [metaContractType, setMetaContractType] = useState('NDA');
  const [metaClauseType, setMetaClauseType] = useState('Confidentiality');
  const [metaJurisdiction, setMetaJurisdiction] = useState('California');
  const [metaResult, setMetaResult] = useState<string | null>(null);
  const [fetchingMeta, setFetchingMeta] = useState(false);

  // Playground Validator
  const [candClauseType, setCandClauseType] = useState('Survival');
  const [candJurisdiction, setCandJurisdiction] = useState('California');
  const [candContractType, setCandContractType] = useState('NDA');
  const [candContent, setCandContent] = useState(
    'The confidentiality obligations herein shall expire two (2) years following the execution date of this Agreement.'
  );
  const [validating, setValidating] = useState(false);
  const [validationOutput, setValidationOutput] = useState<any>(null);

  // Knowledge base state
  const [knowledgeData, setKnowledgeData] = useState<any>(null);

  useEffect(() => {
    fetch('/api/mcp/knowledge-base')
      .then(res => res.json())
      .then(data => setKnowledgeData(data))
      .catch(() => {});
  }, []);

  // Handlers
  const handleSearchClause = async () => {
    setSearchingClause(true);
    try {
      const res = await fetch('/api/mcp/tools/search_clause_library', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: clauseQuery, clause_type: clauseType, limit: 3 })
      });
      const data = await res.json();
      setClauseSearchResult(data.formatted_text);
    } catch (e: any) {
      setClauseSearchResult(`Error: ${e.message}`);
    } finally {
      setSearchingClause(false);
    }
  };

  const handleFetchRule = async () => {
    setFetchingRule(true);
    try {
      const res = await fetch('/api/mcp/tools/get_playbook_rule', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rule_name: selectedRule, clause_type: ruleClauseType })
      });
      const data = await res.json();
      setPlaybookResult(data.formatted_text);
    } catch (e: any) {
      setPlaybookResult(`Error: ${e.message}`);
    } finally {
      setFetchingRule(false);
    }
  };

  const handleSearchPrecedent = async () => {
    setSearchingPrecedent(true);
    try {
      const res = await fetch('/api/mcp/tools/search_prior_approved_clauses', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ clause_text: precedentQuery, contract_type: precedentContractType, limit: 3 })
      });
      const data = await res.json();
      setPrecedentResult(data.formatted_text);
    } catch (e: any) {
      setPrecedentResult(`Error: ${e.message}`);
    } finally {
      setSearchingPrecedent(false);
    }
  };

  const handleFetchMeta = async () => {
    setFetchingMeta(true);
    try {
      const res = await fetch('/api/mcp/tools/fetch_metadata', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ contract_type: metaContractType, clause_type: metaClauseType, jurisdiction: metaJurisdiction })
      });
      const data = await res.json();
      setMetaResult(data.formatted_text);
    } catch (e: any) {
      setMetaResult(`Error: ${e.message}`);
    } finally {
      setFetchingMeta(false);
    }
  };

  const handleRunValidation = async () => {
    setValidating(true);
    try {
      const res = await fetch('/api/mcp/validate-clause', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          clause_type: candClauseType,
          clause_content: candContent,
          contract_type: candContractType,
          jurisdiction: candJurisdiction
        })
      });
      const data = await res.json();
      setValidationOutput(data);
    } catch (e: any) {
      setValidationOutput({ error: e.message });
    } finally {
      setValidating(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-blue-900 via-indigo-900 to-slate-900 text-white rounded-xl p-8 shadow-md relative overflow-hidden">
        <div className="relative z-10">
          <div className="flex flex-wrap items-center justify-between gap-4 mb-3">
            <div className="flex items-center gap-3">
              <span className="p-2 bg-blue-600/30 border border-blue-400/30 rounded-lg text-blue-300">
                <Layers className="h-6 w-6" />
              </span>
              <h1 className="text-3xl font-bold tracking-tight">Knowledge + MCP Layer</h1>
            </div>
            <div className="flex items-center gap-2">
              <Badge className="bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 px-3 py-1 text-xs">
                Phase 2 Deliverable
              </Badge>
              <Badge className="bg-blue-500/20 text-blue-200 border border-blue-400/30 px-3 py-1 text-xs">
                Owner: Brittany Gunn
              </Badge>
              <Badge className="bg-purple-500/20 text-purple-200 border border-purple-400/30 px-3 py-1 text-xs">
                4 MCP Tools Active
              </Badge>
            </div>
          </div>
          <p className="text-slate-300 text-base max-w-3xl leading-relaxed">
            The authoritative memory and governance interface for the contract intelligence platform. Exposes legal playbooks, benchmark clause libraries, precedent archives, and jurisdictional metadata via standardized Model Context Protocol tools.
          </p>
        </div>
      </div>

      {/* Main Tabs */}
      <Tabs value={activeSubTab} onValueChange={(v: any) => setActiveSubTab(v)} className="w-full">
        <TabsList className="grid w-full grid-cols-4 bg-slate-200/70 p-1">
          <TabsTrigger value="validator" className="flex items-center gap-2">
            <Play className="h-4 w-4" /> Live MCP Pipeline Playground
          </TabsTrigger>
          <TabsTrigger value="tools" className="flex items-center gap-2">
            <Shield className="h-4 w-4" /> Interactive MCP Tools (4)
          </TabsTrigger>
          <TabsTrigger value="knowledge" className="flex items-center gap-2">
            <Database className="h-4 w-4" /> Knowledge Store Collections
          </TabsTrigger>
          <TabsTrigger value="presentation" className="flex items-center gap-2">
            <Award className="h-4 w-4" /> Presentation Talking Points
          </TabsTrigger>
        </TabsList>

        {/* TAB 1: Live Validation Playground */}
        <TabsContent value="validator" className="space-y-6 mt-6">
          <Card className="border-slate-200 shadow-sm">
            <CardHeader className="bg-slate-50/50 border-b border-slate-100">
              <CardTitle className="text-xl text-slate-800 flex items-center gap-2">
                <Play className="h-5 w-5 text-indigo-600" />
                End-to-End Clause Validation Pipeline
              </CardTitle>
              <CardDescription>
                Simulates an Agent Orchestrator querying the 4 MCP tools in sequence to evaluate a clause dynamically against legal policy.
              </CardDescription>
            </CardHeader>
            <CardContent className="p-6 space-y-6">
              {/* Quick clause presets */}
              <div>
                <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-2">
                  Quick Scenario Presets:
                </label>
                <div className="flex flex-wrap gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    className="text-xs bg-red-50 hover:bg-red-100 text-red-700 border-red-200"
                    onClick={() => {
                      setCandClauseType('Survival');
                      setCandContractType('NDA');
                      setCandJurisdiction('California');
                      setCandContent('The confidentiality obligations herein shall expire two (2) years following the execution date of this Agreement.');
                    }}
                  >
                    ⚠️ High Risk: 2-Year Survival Clause (Policy Breach)
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    className="text-xs bg-amber-50 hover:bg-amber-100 text-amber-700 border-amber-200"
                    onClick={() => {
                      setCandClauseType('Limitation of Liability');
                      setCandContractType('NDA');
                      setCandJurisdiction('Delaware');
                      setCandContent('In no event shall either party be liable for any indirect, incidental, special, or consequential damages arising under this Agreement.');
                    }}
                  >
                    ⚠️ Consequential Damages Exclusion (Review Required)
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    className="text-xs bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border-emerald-200"
                    onClick={() => {
                      setCandClauseType('Survival');
                      setCandContractType('NDA');
                      setCandJurisdiction('Delaware');
                      setCandContent('The obligations of confidentiality shall survive termination of this Agreement for a period of five (5) years.');
                    }}
                  >
                    ✅ Compliant: Standard 5-Year Survival
                  </Button>
                </div>
              </div>

              {/* Input grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Clause Category</label>
                  <select
                    value={candClauseType}
                    onChange={e => setCandClauseType(e.target.value)}
                    className="w-full rounded-md border border-slate-300 p-2 text-sm focus:border-indigo-500 focus:outline-none"
                  >
                    <option value="Survival">Survival</option>
                    <option value="Confidentiality">Confidentiality</option>
                    <option value="Limitation of Liability">Limitation of Liability</option>
                    <option value="Termination">Termination</option>
                    <option value="Indemnification">Indemnification</option>
                    <option value="Payment Terms">Payment Terms</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Contract Type</label>
                  <select
                    value={candContractType}
                    onChange={e => setCandContractType(e.target.value)}
                    className="w-full rounded-md border border-slate-300 p-2 text-sm focus:border-indigo-500 focus:outline-none"
                  >
                    <option value="NDA">NDA (Non-Disclosure Agreement)</option>
                    <option value="MSA">MSA (Master Services Agreement)</option>
                    <option value="SOW">SOW (Statement of Work)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Jurisdiction</label>
                  <select
                    value={candJurisdiction}
                    onChange={e => setCandJurisdiction(e.target.value)}
                    className="w-full rounded-md border border-slate-300 p-2 text-sm focus:border-indigo-500 focus:outline-none"
                  >
                    <option value="California">California</option>
                    <option value="Delaware">Delaware</option>
                    <option value="New York">New York</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Candidate Clause Text to Review</label>
                <textarea
                  rows={3}
                  value={candContent}
                  onChange={e => setCandContent(e.target.value)}
                  className="w-full rounded-md border border-slate-300 p-3 text-sm font-mono focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <Button
                onClick={handleRunValidation}
                disabled={validating}
                className="bg-indigo-600 hover:bg-indigo-700 text-white w-full py-3 text-base flex items-center justify-center gap-2"
              >
                {validating ? 'Running MCP Pipeline...' : 'Execute 4-Step MCP Validation Pipeline'}
                <ArrowRight className="h-4 w-4" />
              </Button>

              {/* Output Display */}
              {validationOutput && (
                <div className="space-y-4 pt-4 border-t border-slate-200">
                  <div className="flex items-center justify-between bg-slate-100 p-4 rounded-lg">
                    <div>
                      <span className="text-xs uppercase font-bold text-slate-500 tracking-wider">Evaluation Verdict</span>
                      <h3 className="text-xl font-bold flex items-center gap-2 mt-1">
                        {validationOutput?.evaluation?.flagged ? (
                          <span className="text-red-600 flex items-center gap-1.5">
                            <AlertTriangle className="h-6 w-6 text-red-500" />
                            {validationOutput?.evaluation?.recommendation || 'Flagged for Escalation'}
                          </span>
                        ) : (
                          <span className="text-emerald-600 flex items-center gap-1.5">
                            <CheckCircle2 className="h-6 w-6 text-emerald-500" />
                            {validationOutput?.evaluation?.recommendation || 'Compliant with Playbook'}
                          </span>
                        )}
                      </h3>
                    </div>
                    <Badge className={validationOutput?.evaluation?.flagged ? 'bg-red-100 text-red-800 border-red-200 text-sm' : 'bg-emerald-100 text-emerald-800 border-emerald-200 text-sm'}>
                      {validationOutput?.evaluation?.flagged ? 'High Risk Violation' : 'Standard Approved'}
                    </Badge>
                  </div>

                  {validationOutput?.evaluation?.reasons?.length > 0 && (
                    <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                      <h4 className="font-semibold text-red-800 text-sm mb-1">Policy Violation Details:</h4>
                      <ul className="list-disc list-inside text-sm text-red-700 space-y-1">
                        {validationOutput.evaluation.reasons.map((r: string, i: number) => (
                          <li key={i}>{r}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* 4 Pipeline Step Inspection */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Card className="border-slate-200 bg-white shadow-xs">
                      <CardHeader className="py-3 px-4 bg-slate-50 border-b border-slate-100">
                        <CardTitle className="text-xs font-bold text-slate-700 uppercase flex items-center gap-1.5">
                          <Scale className="h-3.5 w-3.5 text-blue-600" /> Step 1: Context Metadata (`fetch_metadata`)
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="p-3 text-xs font-mono whitespace-pre-wrap text-slate-700">
                        {validationOutput.metadata_context}
                      </CardContent>
                    </Card>

                    <Card className="border-slate-200 bg-white shadow-xs">
                      <CardHeader className="py-3 px-4 bg-slate-50 border-b border-slate-100">
                        <CardTitle className="text-xs font-bold text-slate-700 uppercase flex items-center gap-1.5">
                          <Shield className="h-3.5 w-3.5 text-indigo-600" /> Step 2: Governing Rule (`get_playbook_rule`)
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="p-3 text-xs font-mono whitespace-pre-wrap text-slate-700">
                        {validationOutput.playbook_rule}
                      </CardContent>
                    </Card>

                    <Card className="border-slate-200 bg-white shadow-xs">
                      <CardHeader className="py-3 px-4 bg-slate-50 border-b border-slate-100">
                        <CardTitle className="text-xs font-bold text-slate-700 uppercase flex items-center gap-1.5">
                          <Search className="h-3.5 w-3.5 text-teal-600" /> Step 3: Clause Benchmark (`search_clause_library`)
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="p-3 text-xs font-mono whitespace-pre-wrap text-slate-700">
                        {validationOutput.benchmark_clauses}
                      </CardContent>
                    </Card>

                    <Card className="border-slate-200 bg-white shadow-xs">
                      <CardHeader className="py-3 px-4 bg-slate-50 border-b border-slate-100">
                        <CardTitle className="text-xs font-bold text-slate-700 uppercase flex items-center gap-1.5">
                          <Database className="h-3.5 w-3.5 text-purple-600" /> Step 4: Historical Precedent (`search_prior_approved_clauses`)
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="p-3 text-xs font-mono whitespace-pre-wrap text-slate-700">
                        {validationOutput.precedent_approved}
                      </CardContent>
                    </Card>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* TAB 2: Interactive Tools Testing */}
        <TabsContent value="tools" className="space-y-6 mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Tool 1 */}
            <Card className="border-slate-200 shadow-sm">
              <CardHeader className="bg-slate-50 border-b border-slate-100">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base font-bold text-slate-800 flex items-center gap-2">
                    <Search className="h-4 w-4 text-blue-600" /> search_clause_library
                  </CardTitle>
                  <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200 text-xs">
                    Semantic Search
                  </Badge>
                </div>
                <CardDescription className="text-xs">
                  Compares clause language against standard templates to identify deviations.
                </CardDescription>
              </CardHeader>
              <CardContent className="p-4 space-y-3">
                <div>
                  <label className="text-xs font-medium text-slate-600">Clause Text Query</label>
                  <input
                    type="text"
                    value={clauseQuery}
                    onChange={e => setClauseQuery(e.target.value)}
                    className="w-full border rounded p-2 text-xs mt-1"
                  />
                </div>
                <div className="flex gap-2">
                  <div className="flex-1">
                    <label className="text-xs font-medium text-slate-600">Clause Type</label>
                    <input
                      type="text"
                      value={clauseType}
                      onChange={e => setClauseType(e.target.value)}
                      className="w-full border rounded p-2 text-xs mt-1"
                    />
                  </div>
                  <div className="flex items-end">
                    <Button size="sm" onClick={handleSearchClause} disabled={searchingClause} className="bg-blue-600 hover:bg-blue-700 text-white">
                      {searchingClause ? 'Searching...' : 'Search'}
                    </Button>
                  </div>
                </div>
                {clauseSearchResult && (
                  <div className="mt-2 bg-slate-900 text-slate-100 p-3 rounded text-xs font-mono max-h-48 overflow-y-auto whitespace-pre-wrap">
                    {clauseSearchResult}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Tool 2 */}
            <Card className="border-slate-200 shadow-sm">
              <CardHeader className="bg-slate-50 border-b border-slate-100">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base font-bold text-slate-800 flex items-center gap-2">
                    <Shield className="h-4 w-4 text-indigo-600" /> get_playbook_rule
                  </CardTitle>
                  <Badge variant="outline" className="bg-indigo-50 text-indigo-700 border-indigo-200 text-xs">
                    Exact Governance
                  </Badge>
                </div>
                <CardDescription className="text-xs">
                  Pulls authoritative policy constraints (survival thresholds, liability limits).
                </CardDescription>
              </CardHeader>
              <CardContent className="p-4 space-y-3">
                <div>
                  <label className="text-xs font-medium text-slate-600">Select Rule Name</label>
                  <select
                    value={selectedRule}
                    onChange={e => setSelectedRule(e.target.value)}
                    className="w-full border rounded p-2 text-xs mt-1"
                  >
                    <option value="confidentiality_survival_minimum">confidentiality_survival_minimum</option>
                    <option value="liability_cap_review">liability_cap_review</option>
                    <option value="termination_notice_minimum">termination_notice_minimum</option>
                    <option value="mutual_indemnification_mandate">mutual_indemnification_mandate</option>
                    <option value="payment_terms_approval">payment_terms_approval</option>
                  </select>
                </div>
                <div className="flex gap-2">
                  <div className="flex-1">
                    <label className="text-xs font-medium text-slate-600">Applies To</label>
                    <input
                      type="text"
                      value={ruleClauseType}
                      onChange={e => setRuleClauseType(e.target.value)}
                      className="w-full border rounded p-2 text-xs mt-1"
                    />
                  </div>
                  <div className="flex items-end">
                    <Button size="sm" onClick={handleFetchRule} disabled={fetchingRule} className="bg-indigo-600 hover:bg-indigo-700 text-white">
                      {fetchingRule ? 'Fetching...' : 'Fetch Rule'}
                    </Button>
                  </div>
                </div>
                {playbookResult && (
                  <div className="mt-2 bg-slate-900 text-slate-100 p-3 rounded text-xs font-mono max-h-48 overflow-y-auto whitespace-pre-wrap">
                    {playbookResult}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Tool 3 */}
            <Card className="border-slate-200 shadow-sm">
              <CardHeader className="bg-slate-50 border-b border-slate-100">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base font-bold text-slate-800 flex items-center gap-2">
                    <BookOpen className="h-4 w-4 text-purple-600" /> search_prior_approved_clauses
                  </CardTitle>
                  <Badge variant="outline" className="bg-purple-50 text-purple-700 border-purple-200 text-xs">
                    Precedent Match
                  </Badge>
                </div>
                <CardDescription className="text-xs">
                  Finds historically approved clauses to prevent re-negotiation and adjust risk.
                </CardDescription>
              </CardHeader>
              <CardContent className="p-4 space-y-3">
                <div>
                  <label className="text-xs font-medium text-slate-600">Precedent Text Query</label>
                  <input
                    type="text"
                    value={precedentQuery}
                    onChange={e => setPrecedentQuery(e.target.value)}
                    className="w-full border rounded p-2 text-xs mt-1"
                  />
                </div>
                <div className="flex gap-2">
                  <div className="flex-1">
                    <label className="text-xs font-medium text-slate-600">Contract Type</label>
                    <input
                      type="text"
                      value={precedentContractType}
                      onChange={e => setPrecedentContractType(e.target.value)}
                      className="w-full border rounded p-2 text-xs mt-1"
                    />
                  </div>
                  <div className="flex items-end">
                    <Button size="sm" onClick={handleSearchPrecedent} disabled={searchingPrecedent} className="bg-purple-600 hover:bg-purple-700 text-white">
                      {searchingPrecedent ? 'Searching...' : 'Find Precedents'}
                    </Button>
                  </div>
                </div>
                {precedentResult && (
                  <div className="mt-2 bg-slate-900 text-slate-100 p-3 rounded text-xs font-mono max-h-48 overflow-y-auto whitespace-pre-wrap">
                    {precedentResult}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Tool 4 */}
            <Card className="border-slate-200 shadow-sm">
              <CardHeader className="bg-slate-50 border-b border-slate-100">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base font-bold text-slate-800 flex items-center gap-2">
                    <Scale className="h-4 w-4 text-teal-600" /> fetch_metadata
                  </CardTitle>
                  <Badge variant="outline" className="bg-teal-50 text-teal-700 border-teal-200 text-xs">
                    Context Filter
                  </Badge>
                </div>
                <CardDescription className="text-xs">
                  Jurisdiction rules and risk thresholds applied before vector similarity ranking.
                </CardDescription>
              </CardHeader>
              <CardContent className="p-4 space-y-3">
                <div className="grid grid-cols-3 gap-2">
                  <div>
                    <label className="text-xs font-medium text-slate-600">Contract</label>
                    <input
                      type="text"
                      value={metaContractType}
                      onChange={e => setMetaContractType(e.target.value)}
                      className="w-full border rounded p-2 text-xs mt-1"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-medium text-slate-600">Clause</label>
                    <input
                      type="text"
                      value={metaClauseType}
                      onChange={e => setMetaClauseType(e.target.value)}
                      className="w-full border rounded p-2 text-xs mt-1"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-medium text-slate-600">Jurisdiction</label>
                    <input
                      type="text"
                      value={metaJurisdiction}
                      onChange={e => setMetaJurisdiction(e.target.value)}
                      className="w-full border rounded p-2 text-xs mt-1"
                    />
                  </div>
                </div>
                <Button size="sm" onClick={handleFetchMeta} disabled={fetchingMeta} className="bg-teal-600 hover:bg-teal-700 text-white w-full">
                  {fetchingMeta ? 'Fetching...' : 'Fetch Context Metadata'}
                </Button>
                {metaResult && (
                  <div className="mt-2 bg-slate-900 text-slate-100 p-3 rounded text-xs font-mono max-h-48 overflow-y-auto whitespace-pre-wrap">
                    {metaResult}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* TAB 3: Knowledge Store Collections */}
        <TabsContent value="knowledge" className="space-y-6 mt-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="border-slate-200 shadow-sm">
              <CardHeader className="bg-slate-50 border-b border-slate-100 py-3">
                <CardTitle className="text-sm font-bold text-slate-800 flex items-center gap-2">
                  <Search className="h-4 w-4 text-blue-600" /> Clause Library ({knowledgeData?.clauses?.length || 8})
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4 space-y-3 max-h-96 overflow-y-auto">
                {knowledgeData?.clauses?.map((c: any) => (
                  <div key={c.id} className="p-2.5 bg-slate-50 rounded border border-slate-200 text-xs">
                    <div className="flex justify-between items-center mb-1">
                      <Badge variant="outline" className="text-[10px] bg-blue-50 text-blue-700">{c.metadata.clause_type}</Badge>
                      <span className="text-[10px] text-slate-500">{c.metadata.contract_type}</span>
                    </div>
                    <p className="text-slate-700 leading-snug">{c.text}</p>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card className="border-slate-200 shadow-sm">
              <CardHeader className="bg-slate-50 border-b border-slate-100 py-3">
                <CardTitle className="text-sm font-bold text-slate-800 flex items-center gap-2">
                  <Shield className="h-4 w-4 text-indigo-600" /> Legal Playbook ({knowledgeData?.playbook_rules?.length || 6})
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4 space-y-3 max-h-96 overflow-y-auto">
                {knowledgeData?.playbook_rules?.map((p: any) => (
                  <div key={p.id} className="p-2.5 bg-slate-50 rounded border border-slate-200 text-xs">
                    <div className="flex justify-between items-center mb-1">
                      <Badge variant="outline" className="text-[10px] bg-indigo-50 text-indigo-700">{p.metadata.rule_name}</Badge>
                      <span className="text-[10px] text-red-600 font-bold">{p.metadata.severity}</span>
                    </div>
                    <p className="text-slate-700 leading-snug">{p.text}</p>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card className="border-slate-200 shadow-sm">
              <CardHeader className="bg-slate-50 border-b border-slate-100 py-3">
                <CardTitle className="text-sm font-bold text-slate-800 flex items-center gap-2">
                  <Database className="h-4 w-4 text-purple-600" /> Approved Precedents ({knowledgeData?.approved_precedents?.length || 4})
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4 space-y-3 max-h-96 overflow-y-auto">
                {knowledgeData?.approved_precedents?.map((a: any) => (
                  <div key={a.id} className="p-2.5 bg-slate-50 rounded border border-slate-200 text-xs">
                    <div className="flex justify-between items-center mb-1">
                      <Badge variant="outline" className="text-[10px] bg-purple-50 text-purple-700">{a.metadata.clause_type}</Badge>
                      <span className="text-[10px] text-slate-500">{a.metadata.approved_date}</span>
                    </div>
                    <p className="text-slate-700 leading-snug">{a.text}</p>
                    <p className="text-[10px] text-slate-500 mt-1">Approved by: {a.metadata.approved_by}</p>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* TAB 4: Presentation Talking Points */}
        <TabsContent value="presentation" className="space-y-6 mt-6">
          <div className="space-y-4">
            <Card className="border-l-4 border-l-blue-600 shadow-sm">
              <CardHeader className="py-3 px-4 bg-slate-50/50">
                <CardTitle className="text-sm font-bold text-slate-800">
                  1. What problem does your layer solve?
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4 text-sm text-slate-700 leading-relaxed">
                "The agents need to analyze contract clauses against legal policy — but that knowledge cannot simply be baked into the model weights without constant retraining, and putting everything in prompts blows up context limits and creates hallucinations. My layer gives the agents an authoritative memory. Instead of hallucinating what an acceptable clause looks like, the agents retrieve it dynamically from a curated, policy-grounded knowledge base."
              </CardContent>
            </Card>

            <Card className="border-l-4 border-l-indigo-600 shadow-sm">
              <CardHeader className="py-3 px-4 bg-slate-50/50">
                <CardTitle className="text-sm font-bold text-slate-800">
                  2. What is the Knowledge Layer?
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4 text-sm text-slate-700 leading-relaxed">
                "I built a RAG system storing three distinct legal knowledge collections: benchmark standard clauses, authoritative playbook rules, and historically approved precedents. When an agent receives a clause to analyze, it queries the knowledge store semantically and receives exact policy rules, benchmark language, and precedent approval history to ground its decision."
              </CardContent>
            </Card>

            <Card className="border-l-4 border-l-purple-600 shadow-sm">
              <CardHeader className="py-3 px-4 bg-slate-50/50">
                <CardTitle className="text-sm font-bold text-slate-800">
                  3. What are the 4 MCP tools and why did you design them that way?
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4 text-sm text-slate-700 leading-relaxed space-y-2">
                <p>• <strong>search_clause_library</strong> — compares candidate clauses against benchmark language using semantic vector search with clause-type filtering.</p>
                <p>• <strong>get_playbook_rule</strong> — fetches exact policy rules. It is targeted retrieval, not fuzzy, because compliance checking requires strict adherence to corporate policy.</p>
                <p>• <strong>search_prior_approved_clauses</strong> — retrieves historical precedents. High similarity to previously approved language lowers risk, preventing re-negotiation of approved patterns.</p>
                <p>• <strong>fetch_metadata</strong> — retrieves contract and jurisdictional metadata. This ensures legal nuances (like California vs. Delaware law) constrain the analysis before similarity ranking happens.</p>
              </CardContent>
            </Card>

            <Card className="border-l-4 border-l-teal-600 shadow-sm">
              <CardHeader className="py-3 px-4 bg-slate-50/50">
                <CardTitle className="text-sm font-bold text-slate-800">
                  4. Why MCP instead of calling the vector store directly from each agent?
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4 text-sm text-slate-700 leading-relaxed">
                "Separation of concerns. The agents should not know HOW knowledge is stored or indexed — only that they have a standard interface to request it. By using the Model Context Protocol, any agent can query our legal knowledge. If we swap the underlying storage from Neo4j to Qdrant or an internal vector store tomorrow, zero agent code changes. That is what enables enterprise scale."
              </CardContent>
            </Card>

            <Card className="border-l-4 border-l-amber-600 shadow-sm">
              <CardHeader className="py-3 px-4 bg-slate-50/50">
                <CardTitle className="text-sm font-bold text-slate-800">
                  5. What would you improve with more time?
                </CardTitle>
              </CardHeader>
              <CardContent className="p-4 text-sm text-slate-700 leading-relaxed">
                "Two areas: First, ingesting full-scale training corpora: the complete CUAD 510 commercial contracts dataset, LEDGAR (60,000+ labeled provisions), and ContractNLI. Second, adding a cross-encoder re-ranking step: retrieving the top 15 candidate clauses and running a re-ranker before passing the top 3 to the agent orchestrator."
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};
