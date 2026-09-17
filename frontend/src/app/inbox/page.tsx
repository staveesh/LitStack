"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { Paper, Project, TriageResult, WorkflowStatus } from "@/lib/types";
import { WorkflowBadge } from "@/components/WorkflowBadge";
import { AIBadge } from "@/components/AIBadge";

const WORKFLOW_OPTIONS: WorkflowStatus[] = [
  "inbox", "triaged", "skim", "deep_read", "read", "citation_only", "archived",
];

export default function InboxPage() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [filterStatus, setFilterStatus] = useState<WorkflowStatus | "">("");
  const [projectFilter, setProjectFilter] = useState<number | "">("");
  const [triageResults, setTriageResults] = useState<TriageResult[]>([]);
  const [triageProject, setTriageProject] = useState<number | "">("");
  const [loading, setLoading] = useState(false);
  const [triaging, setTriaging] = useState(false);
  const [applying, setApplying] = useState<number | null>(null);
  const [zoteroStatus, setZoteroStatus] = useState<Record<string, unknown>>({});
  const [syncing, setSyncing] = useState(false);

  async function load() {
    setLoading(true);
    const params: Record<string, string> = {};
    if (filterStatus) params.status = filterStatus;
    if (projectFilter) params.project_id = String(projectFilter);
    const [ps, projs] = await Promise.all([
      api.papers.list(params),
      api.projects.list(),
    ]);
    setPapers(ps);
    setProjects(projs);
    setLoading(false);
  }

  async function loadZoteroStatus() {
    const s = await api.zotero.status().catch(() => ({}));
    setZoteroStatus(s);
  }

  useEffect(() => { load(); loadZoteroStatus(); }, [filterStatus, projectFilter]);

  function toggleSelect(id: number) {
    setSelectedIds(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  }

  function selectAll() {
    setSelectedIds(new Set(papers.map(p => p.id)));
  }

  async function syncZotero() {
    setSyncing(true);
    try {
      await api.zotero.sync();
      await load();
      await loadZoteroStatus();
    } finally {
      setSyncing(false);
    }
  }

  async function runTriage() {
    if (selectedIds.size === 0) return;
    setTriaging(true);
    try {
      const results = await api.ai.triage(
        Array.from(selectedIds),
        triageProject ? Number(triageProject) : undefined,
      );
      setTriageResults(results);
    } catch (e) {
      alert(`Triage failed: ${e instanceof Error ? e.message : e}`);
    } finally {
      setTriaging(false);
    }
  }

  async function applyTriageResult(r: TriageResult) {
    setApplying(r.paper_id);
    try {
      await api.ai.applyTriage({
        paper_id: r.paper_id,
        workflow_status: r.recommended_action === "ignore" ? "archived" : r.recommended_action,
        relevance_score: r.relevance_score,
        reading_intent: r.suggested_reading_intent,
        research_question_ids: r.related_question_ids,
      });
      setTriageResults(prev => prev.filter(t => t.paper_id !== r.paper_id));
      setSelectedIds(prev => { const n = new Set(prev); n.delete(r.paper_id); return n; });
      await load();
    } finally {
      setApplying(null);
    }
  }

  const triageMap = new Map(triageResults.map(r => [r.paper_id, r]));

  return (
    <div className="p-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Inbox</h1>
        <div className="flex gap-2">
          <button
            onClick={syncZotero}
            disabled={syncing}
            className="px-3 py-1.5 text-sm border rounded hover:bg-gray-50 disabled:opacity-50"
          >
            {syncing ? "Syncing…" : "Sync Zotero"}
          </button>
          {zoteroStatus.last_sync && (
            <span className="text-xs text-gray-400 self-center">
              Last sync: {new Date(zoteroStatus.last_sync as string).toLocaleString()}
            </span>
          )}
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-3 mb-4">
        <select
          value={filterStatus}
          onChange={e => setFilterStatus(e.target.value as WorkflowStatus | "")}
          className="text-sm border rounded px-2 py-1.5"
        >
          <option value="">All statuses</option>
          {WORKFLOW_OPTIONS.map(s => (
            <option key={s} value={s}>{s.replace("_", " ")}</option>
          ))}
        </select>
        <select
          value={projectFilter}
          onChange={e => setProjectFilter(e.target.value ? Number(e.target.value) : "")}
          className="text-sm border rounded px-2 py-1.5"
        >
          <option value="">All projects</option>
          {projects.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
        </select>
      </div>

      {/* Bulk triage toolbar */}
      {selectedIds.size > 0 && (
        <div className="flex items-center gap-3 mb-4 p-3 bg-blue-50 border border-blue-200 rounded">
          <span className="text-sm text-blue-800">{selectedIds.size} selected</span>
          <select
            value={triageProject}
            onChange={e => setTriageProject(e.target.value ? Number(e.target.value) : "")}
            className="text-sm border rounded px-2 py-1"
          >
            <option value="">No project context</option>
            {projects.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
          <button
            onClick={runTriage}
            disabled={triaging}
            className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {triaging ? "Running AI triage…" : "AI Triage"}
          </button>
          {triaging && (
            <span className="text-xs text-amber-700 flex items-center gap-1">
              <AIBadge /> Sending abstracts to AI — content will leave this machine
            </span>
          )}
          <button onClick={() => setSelectedIds(new Set())} className="text-xs text-gray-500 ml-auto">
            Clear
          </button>
        </div>
      )}

      {/* Paper list */}
      <div className="space-y-3">
        <div className="flex gap-2 text-xs text-gray-500 mb-2">
          <button onClick={selectAll} className="hover:underline">Select all</button>
          <span>·</span>
          <span>{papers.length} papers</span>
        </div>

        {loading && <p className="text-gray-400 text-sm">Loading…</p>}

        {papers.map(paper => {
          const triage = triageMap.get(paper.id);
          return (
            <div
              key={paper.id}
              className={`border rounded-lg p-4 bg-white hover:border-gray-300 transition-colors ${
                selectedIds.has(paper.id) ? "border-blue-400 bg-blue-50/30" : ""
              }`}
            >
              <div className="flex items-start gap-3">
                <input
                  type="checkbox"
                  checked={selectedIds.has(paper.id)}
                  onChange={() => toggleSelect(paper.id)}
                  className="mt-1 shrink-0"
                />
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2">
                    <Link
                      href={`/papers/${paper.id}`}
                      className="font-medium text-gray-900 hover:text-blue-700 leading-snug"
                    >
                      {paper.title}
                    </Link>
                    <WorkflowBadge status={paper.workflow_status} />
                  </div>
                  <p className="text-xs text-gray-500 mt-0.5">
                    {paper.authors.slice(0, 3).join(", ")}
                    {paper.authors.length > 3 ? " et al." : ""}
                    {paper.year ? ` · ${paper.year}` : ""}
                    {paper.venue ? ` · ${paper.venue}` : ""}
                  </p>
                  {paper.abstract && (
                    <p className="text-sm text-gray-600 mt-2 line-clamp-2">{paper.abstract}</p>
                  )}
                  {paper.reading_reason && (
                    <p className="text-xs text-gray-400 mt-1 italic">Why: {paper.reading_reason}</p>
                  )}

                  {/* AI triage suggestion */}
                  {triage && (
                    <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded text-sm">
                      <div className="flex items-center gap-2 mb-2">
                        <AIBadge />
                        <span className="font-medium text-amber-800">
                          Recommend: {triage.recommended_action.replace("_", " ")}
                        </span>
                        <span className="text-amber-600 text-xs">
                          (relevance {(triage.relevance_score * 100).toFixed(0)}%, confidence {(triage.confidence * 100).toFixed(0)}%)
                        </span>
                      </div>
                      <p className="text-gray-700 text-xs mb-2">{triage.reason}</p>
                      {triage.sections_to_inspect.length > 0 && (
                        <p className="text-xs text-gray-500">
                          Inspect: {triage.sections_to_inspect.join(", ")}
                        </p>
                      )}
                      <p className="text-xs text-gray-600 mt-1 italic">
                        Suggested intent: {triage.suggested_reading_intent}
                      </p>
                      <div className="flex gap-2 mt-3">
                        <button
                          onClick={() => applyTriageResult(triage)}
                          disabled={applying === triage.paper_id}
                          className="px-2 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
                        >
                          {applying === triage.paper_id ? "Applying…" : "Apply this recommendation"}
                        </button>
                        <button
                          onClick={() => setTriageResults(prev => prev.filter(t => t.paper_id !== triage.paper_id))}
                          className="px-2 py-1 text-xs border rounded hover:bg-gray-50"
                        >
                          Dismiss
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}

        {!loading && papers.length === 0 && (
          <div className="text-center py-12 text-gray-400">
            <p>No papers. Sync from Zotero or add manually.</p>
          </div>
        )}
      </div>
    </div>
  );
}
