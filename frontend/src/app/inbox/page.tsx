"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { Paper, Project, ResearchQuestion, TriageResult, WorkflowStatus } from "@/lib/types";
import { WorkflowBadge } from "@/components/WorkflowBadge";
import { AIBadge } from "@/components/AIBadge";

const WORKFLOW_OPTIONS: WorkflowStatus[] = [
  "inbox", "triaged", "skim", "deep_read", "read", "citation_only", "archived",
];

export default function InboxPage() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [rqs, setRqs] = useState<ResearchQuestion[]>([]);
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [filterStatus, setFilterStatus] = useState<WorkflowStatus | "">("");
  const [projectFilter, setProjectFilter] = useState<number | "">("");
  const [rqFilter, setRqFilter] = useState<number | "">("");
  const [searchQuery, setSearchQuery] = useState("");
  const [triageResults, setTriageResults] = useState<TriageResult[]>([]);
  const [triageProject, setTriageProject] = useState<number | "">("");
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [loading, setLoading] = useState(false);
  const [triaging, setTriaging] = useState(false);
  const [applying, setApplying] = useState<number | null>(null);
  const [zoteroStatus, setZoteroStatus] = useState<Record<string, unknown>>({});
  const [syncing, setSyncing] = useState(false);
  const [deleting, setDeleting] = useState<number | null>(null);

  async function load() {
    setLoading(true);
    const params: Record<string, string> = { limit: "10", offset: String(page * 10) };
    if (filterStatus) params.status = filterStatus;
    if (projectFilter) params.project_id = String(projectFilter);
    if (rqFilter) params.research_question_id = String(rqFilter);
    if (searchQuery) params.q = searchQuery;
    const [ps, projs, allRqs] = await Promise.all([
      api.papers.list(params),
      api.projects.list(),
      api.rqs.listAll(),
    ]);
    setPapers(ps);
    setHasMore(ps.length === 10);
    setProjects(projs);
    setRqs(allRqs);
    setLoading(false);
  }

  async function loadZoteroStatus() {
    const s = await api.zotero.status().catch(() => ({}));
    setZoteroStatus(s);
  }

  useEffect(() => { loadZoteroStatus(); }, []);
  useEffect(() => {
    setPage(0);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filterStatus, projectFilter, rqFilter, searchQuery]);

  useEffect(() => {
    const t = setTimeout(load, searchQuery ? 300 : 0);
    return () => clearTimeout(t);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filterStatus, projectFilter, rqFilter, searchQuery, page]);

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

  async function deletePaper(paper: Paper) {
    const hasZotero = Boolean(paper.zotero_key);
    const msg = hasZotero
      ? `Delete "${paper.title}" from this tracker AND from your Zotero library?`
      : `Delete "${paper.title}" from this tracker?`;
    if (!confirm(msg)) return;
    setDeleting(paper.id);
    try {
      await api.papers.delete(paper.id, hasZotero);
      setPapers(prev => prev.filter(p => p.id !== paper.id));
      setSelectedIds(prev => { const n = new Set(prev); n.delete(paper.id); return n; });
    } catch (e) {
      alert(`Delete failed: ${e instanceof Error ? e.message : e}`);
    } finally {
      setDeleting(null);
    }
  }

  const triageMap = new Map(triageResults.map(r => [r.paper_id, r]));
  const filteredRqs = projectFilter ? rqs.filter(rq => rq.project_id === projectFilter) : rqs;

  return (
    <div className="p-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Inbox</h1>
          <p className="text-sm text-slate-400 mt-0.5">Page {page + 1}</p>
        </div>
        <div className="flex items-center gap-3">
          {zoteroStatus.last_sync && (
            <span className="text-xs text-slate-400">
              Synced {new Date(zoteroStatus.last_sync as string).toLocaleString()}
            </span>
          )}
          <button
            onClick={syncZotero}
            disabled={syncing}
            className="px-4 py-2 text-sm font-medium border border-slate-200 rounded-lg hover:bg-white hover:border-slate-300 hover:shadow-sm disabled:opacity-50 transition-all bg-white shadow-card"
          >
            {syncing ? "Syncing…" : "Sync Zotero"}
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="mb-5 bg-white border border-slate-200 rounded-xl shadow-card p-3 space-y-2">
        <input
          type="search"
          placeholder="Search title or abstract…"
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
          className="w-full text-sm rounded-lg px-3 py-2 bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:border-indigo-300 transition-all"
        />
        <div className="flex gap-2">
          <select
            value={filterStatus}
            onChange={e => setFilterStatus(e.target.value as WorkflowStatus | "")}
            className="text-sm border border-slate-200 rounded-lg px-2.5 py-2 bg-slate-50 focus:outline-none focus:ring-2 focus:ring-indigo-300 cursor-pointer flex-1"
          >
            <option value="">All statuses</option>
            {WORKFLOW_OPTIONS.map(s => (
              <option key={s} value={s}>{s.replace("_", " ")}</option>
            ))}
          </select>
          <select
            value={projectFilter}
            onChange={e => { setProjectFilter(e.target.value ? Number(e.target.value) : ""); setRqFilter(""); }}
            className="text-sm border border-slate-200 rounded-lg px-2.5 py-2 bg-slate-50 focus:outline-none focus:ring-2 focus:ring-indigo-300 cursor-pointer flex-1"
          >
            <option value="">All projects</option>
            {projects.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
          <select
            value={rqFilter}
            onChange={e => setRqFilter(e.target.value ? Number(e.target.value) : "")}
            className="text-sm border border-slate-200 rounded-lg px-2.5 py-2 bg-slate-50 focus:outline-none focus:ring-2 focus:ring-indigo-300 cursor-pointer flex-1"
          >
            <option value="">All questions</option>
            {filteredRqs.map(rq => (
              <option key={rq.id} value={rq.id}>{rq.question}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Bulk triage toolbar */}
      {selectedIds.size > 0 && (
        <div className="flex items-center gap-3 mb-5 p-3.5 bg-indigo-50 border border-indigo-200 rounded-xl">
          <span className="text-sm font-medium text-indigo-800">{selectedIds.size} selected</span>
          <select
            value={triageProject}
            onChange={e => setTriageProject(e.target.value ? Number(e.target.value) : "")}
            className="text-sm border border-indigo-200 rounded-lg px-2.5 py-1 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-300"
          >
            <option value="">No project context</option>
            {projects.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
          <button
            onClick={runTriage}
            disabled={triaging}
            className="px-4 py-1.5 text-sm font-medium bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors shadow-sm"
          >
            {triaging ? "Running AI triage…" : "AI Triage"}
          </button>
          {triaging && (
            <span className="text-xs text-amber-700 flex items-center gap-1.5">
              <AIBadge /> Sending abstracts to AI — content will leave this machine
            </span>
          )}
          <button onClick={() => setSelectedIds(new Set())} className="text-xs text-slate-400 hover:text-slate-600 ml-auto transition-colors">
            Clear selection
          </button>
        </div>
      )}

      {/* Select all */}
      <div className="flex gap-3 text-xs text-slate-400 mb-3">
        <button onClick={selectAll} className="hover:text-slate-600 hover:underline transition-colors">Select all</button>
      </div>

      {/* Paper list */}
      <div className="space-y-2.5">
        {loading && (
          <div className="text-center py-12 text-slate-400 text-sm">Loading…</div>
        )}

        {papers.map(paper => {
          const triage = triageMap.get(paper.id);
          const isSelected = selectedIds.has(paper.id);
          return (
            <div
              key={paper.id}
              className={`rounded-xl border bg-white transition-all duration-200 ${
                isSelected
                  ? "border-indigo-300 shadow-md ring-1 ring-indigo-200"
                  : "border-slate-200 shadow-card hover:shadow-card-hover hover:-translate-y-0.5"
              }`}
            >
              <div className="p-5">
                <div className="flex items-start gap-3">
                  <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={() => toggleSelect(paper.id)}
                    className="mt-1 shrink-0 accent-indigo-600"
                  />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-3">
                      <Link
                        href={`/papers/${paper.id}`}
                        className="font-semibold text-slate-900 hover:text-indigo-700 leading-snug transition-colors"
                      >
                        {paper.title}
                      </Link>
                      <div className="flex items-center gap-2 shrink-0">
                        <WorkflowBadge status={paper.workflow_status} />
                        <button
                          onClick={() => deletePaper(paper)}
                          disabled={deleting === paper.id}
                          title={paper.zotero_key ? "Delete from tracker + Zotero" : "Delete from tracker"}
                          className="text-slate-300 hover:text-red-400 disabled:opacity-50 text-sm leading-none transition-colors p-1"
                        >
                          {deleting === paper.id ? "…" : "✕"}
                        </button>
                      </div>
                    </div>
                    <p className="text-xs text-slate-400 mt-1">
                      {paper.authors.slice(0, 3).join(", ")}
                      {paper.authors.length > 3 ? " et al." : ""}
                      {paper.year ? ` · ${paper.year}` : ""}
                      {paper.venue ? ` · ${paper.venue}` : ""}
                    </p>
                    {paper.abstract && (
                      <p className="text-sm text-slate-500 mt-2.5 line-clamp-2 leading-relaxed">{paper.abstract}</p>
                    )}
                    {paper.reading_reason && (
                      <p className="text-xs text-slate-400 mt-1.5 italic">Why: {paper.reading_reason}</p>
                    )}

                    {/* AI triage suggestion */}
                    {triage && (
                      <div className="mt-4 p-4 bg-amber-50 border border-amber-200 rounded-lg text-sm">
                        <div className="flex items-center gap-2.5 mb-2">
                          <AIBadge />
                          <span className="font-semibold text-amber-800">
                            Recommend: {triage.recommended_action.replace("_", " ")}
                          </span>
                          <span className="text-amber-500 text-xs ml-auto">
                            {(triage.relevance_score * 100).toFixed(0)}% relevant · {(triage.confidence * 100).toFixed(0)}% confident
                          </span>
                        </div>
                        <p className="text-slate-600 text-xs mb-2 leading-relaxed">{triage.reason}</p>
                        {triage.sections_to_inspect.length > 0 && (
                          <p className="text-xs text-slate-400">
                            Inspect: {triage.sections_to_inspect.join(", ")}
                          </p>
                        )}
                        <p className="text-xs text-slate-500 mt-1 italic">
                          Suggested intent: {triage.suggested_reading_intent}
                        </p>
                        <div className="flex gap-2 mt-3">
                          <button
                            onClick={() => applyTriageResult(triage)}
                            disabled={applying === triage.paper_id}
                            className="px-3 py-1.5 text-xs font-medium bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:opacity-50 transition-colors"
                          >
                            {applying === triage.paper_id ? "Applying…" : "Apply recommendation"}
                          </button>
                          <button
                            onClick={() => setTriageResults(prev => prev.filter(t => t.paper_id !== triage.paper_id))}
                            className="px-3 py-1.5 text-xs border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
                          >
                            Dismiss
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          );
        })}

        {!loading && papers.length === 0 && (
          <div className="text-center py-16 text-slate-400">
            <p className="text-4xl mb-3">📚</p>
            <p className="text-sm">No papers. Sync from Zotero or add manually.</p>
          </div>
        )}
      </div>

      {/* Pagination */}
      {(page > 0 || hasMore) && (
        <div className="flex items-center justify-between mt-6 pt-4 border-t border-slate-200">
          <button
            onClick={() => setPage(p => p - 1)}
            disabled={page === 0}
            className="px-4 py-2 text-sm font-medium border border-slate-200 rounded-lg bg-white hover:bg-slate-50 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-card"
          >
            ← Previous
          </button>
          <span className="text-sm text-slate-400">Page {page + 1}</span>
          <button
            onClick={() => setPage(p => p + 1)}
            disabled={!hasMore}
            className="px-4 py-2 text-sm font-medium border border-slate-200 rounded-lg bg-white hover:bg-slate-50 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-card"
          >
            Next →
          </button>
        </div>
      )}
    </div>
  );
}
