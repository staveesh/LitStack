"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api } from "@/lib/api";
import type {
  Paper, PaperExtraction, HumanNote, ReadingIntent,
  ResearchQuestion, Project, WorkflowStatus,
} from "@/lib/types";
import { WorkflowBadge } from "@/components/WorkflowBadge";
import { AIBadge, HumanBadge } from "@/components/AIBadge";

const WORKFLOW_OPTIONS: { value: WorkflowStatus; label: string }[] = [
  { value: "inbox", label: "Inbox" },
  { value: "triaged", label: "Triaged" },
  { value: "skim", label: "Skim" },
  { value: "deep_read", label: "Deep Read" },
  { value: "read", label: "Read" },
  { value: "citation_only", label: "Citation Only" },
  { value: "archived", label: "Archived" },
];

export default function PaperDetailPage() {
  const { id } = useParams<{ id: string }>();
  const paperId = Number(id);
  const router = useRouter();

  const [paper, setPaper] = useState<Paper | null>(null);
  const [extraction, setExtraction] = useState<PaperExtraction | null>(null);
  const [notes, setNotes] = useState<HumanNote | null>(null);
  const [intents, setIntents] = useState<ReadingIntent[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [rqs, setRqs] = useState<ResearchQuestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [savingNotes, setSavingNotes] = useState(false);
  const [extracting, setExtracting] = useState(false);
  const [newIntent, setNewIntent] = useState("");
  const [notesDraft, setNotesDraft] = useState<Partial<HumanNote>>({});
  const [activeTab, setActiveTab] = useState<"extraction" | "notes" | "connections">("extraction");

  async function load() {
    setLoading(true);
    const [p, projs, allRqs] = await Promise.all([
      api.papers.get(paperId),
      api.projects.list(),
      api.rqs.listAll(),
    ]);
    setPaper(p);
    setProjects(projs);
    setRqs(allRqs);

    const [ext, nt, its] = await Promise.all([
      api.extraction.get(paperId).catch(() => null),
      api.notes.get(paperId).catch(() => null),
      api.intents.list(paperId).catch(() => []),
    ]);
    setExtraction(ext);
    setNotes(nt);
    setNotesDraft(nt ?? {});
    setIntents(its);
    setLoading(false);
  }

  useEffect(() => { load(); }, [paperId]);

  async function updateStatus(status: WorkflowStatus) {
    if (!paper) return;
    const updated = await api.papers.update(paperId, { workflow_status: status });
    setPaper(updated);
  }

  async function triggerExtraction() {
    setExtracting(true);
    try {
      const ext = await api.extraction.trigger(paperId);
      setExtraction(ext);
    } catch (e) {
      alert(`Extraction failed: ${e instanceof Error ? e.message : e}`);
    } finally {
      setExtracting(false);
    }
  }

  async function saveNotes() {
    setSavingNotes(true);
    try {
      const saved = await api.notes.save(paperId, notesDraft);
      setNotes(saved);
    } finally {
      setSavingNotes(false);
    }
  }

  async function addIntent() {
    if (!newIntent.trim()) return;
    const intent = await api.intents.create(paperId, newIntent.trim());
    setIntents(prev => [intent, ...prev]);
    setNewIntent("");
  }

  async function resolveIntent(intentId: number) {
    await api.intents.resolve(paperId, intentId);
    setIntents(prev => prev.map(i => i.id === intentId ? { ...i, resolved_at: new Date().toISOString() } : i));
  }

  async function toggleRQ(rqId: number) {
    if (!paper) return;
    const linked = paper.research_question_ids?.includes(rqId);
    if (linked) {
      await api.papers.unlinkRQ(paperId, rqId);
    } else {
      await api.papers.linkRQ(paperId, rqId);
    }
    const updated = await api.papers.get(paperId);
    setPaper(updated);
  }

  if (loading) return <div className="p-6 text-gray-400">Loading…</div>;
  if (!paper) return <div className="p-6 text-red-500">Paper not found</div>;

  const linkedRQIds = new Set(paper.research_question_ids ?? []);
  const linkedRQs = rqs.filter(rq => linkedRQIds.has(rq.id));

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <button onClick={() => router.back()} className="text-xs text-gray-400 hover:text-gray-600 mb-3 block">
          ← Back
        </button>
        <h1 className="text-2xl font-bold text-gray-900 leading-tight">{paper.title}</h1>
        <p className="text-sm text-gray-500 mt-1">
          {paper.authors.join(", ")}
          {paper.year ? ` · ${paper.year}` : ""}
          {paper.venue ? ` · ${paper.venue}` : ""}
          {paper.citation_key ? ` · ${paper.citation_key}` : ""}
        </p>
        <div className="flex items-center gap-3 mt-3">
          <select
            value={paper.workflow_status}
            onChange={e => updateStatus(e.target.value as WorkflowStatus)}
            className="text-sm border rounded px-2 py-1"
          >
            {WORKFLOW_OPTIONS.map(o => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
          {paper.doi && (
            <a href={`https://doi.org/${paper.doi}`} target="_blank" rel="noopener" className="text-xs text-blue-500 hover:underline">
              DOI ↗
            </a>
          )}
          {paper.url && (
            <a href={paper.url} target="_blank" rel="noopener" className="text-xs text-blue-500 hover:underline">
              URL ↗
            </a>
          )}
        </div>
      </div>

      {/* Abstract */}
      {paper.abstract && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg border">
          <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Abstract</h3>
          <p className="text-sm text-gray-700 leading-relaxed">{paper.abstract}</p>
        </div>
      )}

      {/* Reading intents */}
      <section className="mb-6">
        <h2 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
          Why am I reading this?
        </h2>
        <div className="space-y-2">
          {intents.map(intent => (
            <div
              key={intent.id}
              className={`p-3 rounded border text-sm ${
                intent.resolved_at
                  ? "border-gray-200 bg-gray-50 text-gray-400 line-through"
                  : "border-blue-200 bg-blue-50 text-blue-800"
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <span>{intent.intent}</span>
                {!intent.resolved_at && (
                  <button
                    onClick={() => resolveIntent(intent.id)}
                    className="text-xs text-blue-500 hover:underline shrink-0"
                  >
                    Resolve
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
        <div className="flex gap-2 mt-2">
          <input
            value={newIntent}
            onChange={e => setNewIntent(e.target.value)}
            onKeyDown={e => e.key === "Enter" && addIntent()}
            placeholder="Add a reading intent…"
            className="flex-1 text-sm border rounded px-3 py-1.5"
          />
          <button
            onClick={addIntent}
            className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Add
          </button>
        </div>
      </section>

      {/* Tabs: Extraction / My Notes / Connections */}
      <div className="border-b mb-4">
        <div className="flex gap-0">
          {(["extraction", "notes", "connections"] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab
                  ? "border-blue-600 text-blue-700"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              {tab === "extraction" ? "AI Extraction" : tab === "notes" ? "My Notes" : "Connections"}
            </button>
          ))}
        </div>
      </div>

      {/* Extraction tab */}
      {activeTab === "extraction" && (
        <div>
          <div className="flex items-center gap-3 mb-4">
            <AIBadge model={extraction?.model_name} version={extraction?.prompt_version} />
            {extraction?.confidence && (
              <span className="text-xs text-gray-400">
                Confidence: {(extraction.confidence * 100).toFixed(0)}%
              </span>
            )}
            <button
              onClick={triggerExtraction}
              disabled={extracting || !paper.pdf_path}
              className="ml-auto px-3 py-1 text-xs bg-amber-500 text-white rounded hover:bg-amber-600 disabled:opacity-50"
            >
              {extracting ? "Extracting…" : paper.pdf_path ? "Run AI Extraction" : "No PDF"}
            </button>
          </div>

          {!extraction && (
            <p className="text-sm text-gray-400">
              No extraction yet. {paper.pdf_path ? "Click 'Run AI Extraction' above." : "PDF required."}
            </p>
          )}

          {extraction && (
            <div className="ai-content space-y-4">
              <ExtractionField label="Problem" value={extraction.problem} />
              <ExtractionField label="Key Idea" value={extraction.key_idea} />
              <ExtractionField label="Approach" value={extraction.approach} />
              {extraction.architecture && <ExtractionField label="Architecture" value={extraction.architecture} />}
              {extraction.threat_model && <ExtractionField label="Threat Model" value={extraction.threat_model} />}
              <ExtractionList label="Assumptions" items={extraction.assumptions} />
              {extraction.dataset && <ExtractionField label="Dataset" value={extraction.dataset} />}
              {extraction.evaluation_methodology && <ExtractionField label="Evaluation" value={extraction.evaluation_methodology} />}
              <ExtractionList label="Baselines" items={extraction.baselines} />
              <ExtractionList label="Metrics" items={extraction.metrics} />
              <ExtractionField label="Main Results" value={extraction.main_results} />
              <ExtractionList label="Limitations" items={extraction.limitations} />
              <ExtractionList label="Future Work" items={extraction.future_work} />
              <ExtractionList label="Author Claims" items={extraction.claims_made} />
            </div>
          )}
        </div>
      )}

      {/* My Notes tab */}
      {activeTab === "notes" && (
        <div>
          <div className="flex items-center gap-2 mb-4">
            <HumanBadge />
            <span className="text-xs text-gray-400">Your interpretations — never overwritten by AI</span>
          </div>
          <div className="human-content space-y-4">
            <NoteField
              label="Why I care"
              value={notesDraft.why_i_care ?? ""}
              onChange={v => setNotesDraft(prev => ({ ...prev, why_i_care: v }))}
            />
            <NoteField
              label="What surprised me"
              value={notesDraft.what_surprised_me ?? ""}
              onChange={v => setNotesDraft(prev => ({ ...prev, what_surprised_me: v }))}
            />
            <NoteField
              label="What I don't believe"
              value={notesDraft.what_i_dont_believe ?? ""}
              onChange={v => setNotesDraft(prev => ({ ...prev, what_i_dont_believe: v }))}
            />
            <NoteField
              label="Relation to my work"
              value={notesDraft.relation_to_my_work ?? ""}
              onChange={v => setNotesDraft(prev => ({ ...prev, relation_to_my_work: v }))}
            />
            <NoteField
              label="What I might cite this for"
              value={notesDraft.what_i_might_cite_this_for ?? ""}
              onChange={v => setNotesDraft(prev => ({ ...prev, what_i_might_cite_this_for: v }))}
            />
            <NoteField
              label="Methodological ideas"
              value={notesDraft.methodological_ideas ?? ""}
              onChange={v => setNotesDraft(prev => ({ ...prev, methodological_ideas: v }))}
            />
            <NoteField
              label="Unanswered questions"
              value={notesDraft.unanswered_questions ?? ""}
              onChange={v => setNotesDraft(prev => ({ ...prev, unanswered_questions: v }))}
            />
            <NoteField
              label="Freeform notes"
              value={notesDraft.freeform_notes ?? ""}
              onChange={v => setNotesDraft(prev => ({ ...prev, freeform_notes: v }))}
              rows={6}
            />
          </div>
          <button
            onClick={saveNotes}
            disabled={savingNotes}
            className="mt-4 px-4 py-2 bg-green-600 text-white text-sm rounded hover:bg-green-700 disabled:opacity-50"
          >
            {savingNotes ? "Saving…" : "Save Notes"}
          </button>
        </div>
      )}

      {/* Connections tab */}
      {activeTab === "connections" && (
        <div className="space-y-6">
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-3">Research Questions</h3>
            <div className="space-y-2">
              {rqs.map(rq => (
                <label key={rq.id} className="flex items-start gap-2 cursor-pointer group">
                  <input
                    type="checkbox"
                    checked={linkedRQIds.has(rq.id)}
                    onChange={() => toggleRQ(rq.id)}
                    className="mt-0.5"
                  />
                  <div>
                    <span className="text-sm text-gray-800 group-hover:text-blue-700">{rq.question}</span>
                    <span className="ml-2 text-xs text-gray-400">{rq.status.replace("_", " ")}</span>
                  </div>
                </label>
              ))}
              {rqs.length === 0 && (
                <p className="text-sm text-gray-400">No research questions. Create some in a project first.</p>
              )}
            </div>
          </div>

          {linkedRQs.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Linked Questions</h3>
              {linkedRQs.map(rq => (
                <div key={rq.id} className="text-sm text-blue-700 py-1">· {rq.question}</div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function ExtractionField({ label, value }: { label: string; value: string | null | undefined }) {
  if (!value) return null;
  return (
    <div>
      <dt className="text-xs font-semibold text-amber-700 uppercase tracking-wide">{label}</dt>
      <dd className="mt-1 text-sm text-gray-800 leading-relaxed">{value}</dd>
    </div>
  );
}

function ExtractionList({ label, items }: { label: string; items: string[] }) {
  if (!items || items.length === 0) return null;
  return (
    <div>
      <dt className="text-xs font-semibold text-amber-700 uppercase tracking-wide">{label}</dt>
      <dd className="mt-1">
        <ul className="list-disc list-inside space-y-0.5">
          {items.map((item, i) => <li key={i} className="text-sm text-gray-800">{item}</li>)}
        </ul>
      </dd>
    </div>
  );
}

function NoteField({
  label, value, onChange, rows = 3,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  rows?: number;
}) {
  return (
    <div>
      <label className="text-xs font-semibold text-green-700 uppercase tracking-wide block mb-1">
        {label}
      </label>
      <textarea
        value={value}
        onChange={e => onChange(e.target.value)}
        rows={rows}
        placeholder={`Your ${label.toLowerCase()}…`}
        className="w-full text-sm border border-green-200 rounded px-3 py-2 resize-y focus:outline-none focus:border-green-400 bg-white"
      />
    </div>
  );
}
