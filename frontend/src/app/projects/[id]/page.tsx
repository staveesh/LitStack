"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import type { Project, ResearchQuestion, Claim, OpenQuestion } from "@/lib/types";

export default function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>();
  const projectId = Number(id);

  const [project, setProject] = useState<Project | null>(null);
  const [rqs, setRqs] = useState<ResearchQuestion[]>([]);
  const [claims, setClaims] = useState<Claim[]>([]);
  const [oqs, setOqs] = useState<OpenQuestion[]>([]);
  const [newRQ, setNewRQ] = useState("");
  const [newClaim, setNewClaim] = useState("");
  const [newOQ, setNewOQ] = useState("");

  useEffect(() => {
    Promise.all([
      api.projects.get(projectId),
      api.projects.rqs(projectId),
      api.projects.claims(projectId),
      api.projects.openQuestions(projectId),
    ]).then(([proj, r, c, o]) => {
      setProject(proj);
      setRqs(r);
      setClaims(c);
      setOqs(o);
    });
  }, [projectId]);

  async function addRQ() {
    if (!newRQ.trim()) return;
    const rq = await api.projects.createRQ(projectId, { question: newRQ.trim() });
    setRqs(prev => [...prev, rq]);
    setNewRQ("");
  }

  async function addClaim() {
    if (!newClaim.trim()) return;
    const claim = await api.projects.createClaim(projectId, { claim: newClaim.trim() });
    setClaims(prev => [...prev, claim]);
    setNewClaim("");
  }

  async function addOQ() {
    if (!newOQ.trim()) return;
    const oq = await api.projects.createOQ(projectId, { question: newOQ.trim() });
    setOqs(prev => [...prev, oq]);
    setNewOQ("");
  }

  const STATUS_COLORS: Record<string, string> = {
    hypothesis: "bg-gray-100 text-gray-600",
    weak_evidence: "bg-yellow-100 text-yellow-700",
    supported: "bg-green-100 text-green-700",
    contested: "bg-orange-100 text-orange-700",
    rejected: "bg-red-100 text-red-700",
    active: "bg-blue-100 text-blue-700",
    partially_answered: "bg-purple-100 text-purple-700",
    answered: "bg-green-100 text-green-700",
    abandoned: "bg-gray-100 text-gray-400",
    open: "bg-blue-100 text-blue-700",
    investigating: "bg-purple-100 text-purple-700",
    converted_to_experiment: "bg-teal-100 text-teal-700",
  };

  if (!project) return <div className="p-6 text-gray-400">Loading…</div>;

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-1">{project.name}</h1>
      {project.description && <p className="text-gray-500 text-sm mb-6">{project.description}</p>}

      <div className="grid grid-cols-1 gap-8">

        {/* Research Questions */}
        <section>
          <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
            Research Questions
            <span className="text-xs text-gray-400 font-normal">({rqs.length})</span>
          </h2>
          <div className="space-y-2 mb-3">
            {rqs.map(rq => (
              <div key={rq.id} className="flex items-start gap-2 p-3 border rounded bg-white">
                <div className="flex-1">
                  <p className="text-sm text-gray-800">{rq.question}</p>
                  {rq.motivation && <p className="text-xs text-gray-400 mt-1">{rq.motivation}</p>}
                </div>
                <span className={`text-xs px-2 py-0.5 rounded shrink-0 ${STATUS_COLORS[rq.status] ?? "bg-gray-100"}`}>
                  {rq.status.replace("_", " ")}
                </span>
              </div>
            ))}
          </div>
          <div className="flex gap-2">
            <input
              value={newRQ}
              onChange={e => setNewRQ(e.target.value)}
              onKeyDown={e => e.key === "Enter" && addRQ()}
              placeholder="Add research question…"
              className="flex-1 text-sm border rounded px-3 py-1.5"
            />
            <button onClick={addRQ} className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700">
              Add
            </button>
          </div>
        </section>

        {/* Claims */}
        <section>
          <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
            Claims
            <span className="text-xs text-gray-400 font-normal">({claims.length})</span>
          </h2>
          <div className="space-y-2 mb-3">
            {claims.map(claim => (
              <Link
                key={claim.id}
                href={`/claims?project=${projectId}`}
                className="flex items-start gap-2 p-3 border rounded bg-white hover:border-blue-300 block"
              >
                <div className="flex-1">
                  <p className="text-sm text-gray-800">{claim.claim}</p>
                  {claim.confidence != null && (
                    <p className="text-xs text-gray-400 mt-1">
                      Confidence: {(claim.confidence * 100).toFixed(0)}%
                    </p>
                  )}
                </div>
                <span className={`text-xs px-2 py-0.5 rounded shrink-0 ${STATUS_COLORS[claim.status] ?? "bg-gray-100"}`}>
                  {claim.status.replace("_", " ")}
                </span>
              </Link>
            ))}
          </div>
          <div className="flex gap-2">
            <input
              value={newClaim}
              onChange={e => setNewClaim(e.target.value)}
              onKeyDown={e => e.key === "Enter" && addClaim()}
              placeholder="Add a claim…"
              className="flex-1 text-sm border rounded px-3 py-1.5"
            />
            <button onClick={addClaim} className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700">
              Add
            </button>
          </div>
        </section>

        {/* Open Questions */}
        <section>
          <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
            Open Questions
            <span className="text-xs text-gray-400 font-normal">({oqs.length})</span>
          </h2>
          <div className="space-y-2 mb-3">
            {oqs.map(oq => (
              <div key={oq.id} className="flex items-start gap-2 p-3 border rounded bg-white">
                <div className="flex-1">
                  <p className="text-sm text-gray-800">{oq.question}</p>
                  {oq.origin && <p className="text-xs text-gray-400 mt-1">Origin: {oq.origin}</p>}
                </div>
                <div className="flex flex-col items-end gap-1 shrink-0">
                  <span className={`text-xs px-2 py-0.5 rounded ${STATUS_COLORS[oq.status] ?? "bg-gray-100"}`}>
                    {oq.status.replace("_", " ")}
                  </span>
                  {oq.importance && (
                    <span className="text-xs text-gray-400">importance {oq.importance}/5</span>
                  )}
                </div>
              </div>
            ))}
          </div>
          <div className="flex gap-2">
            <input
              value={newOQ}
              onChange={e => setNewOQ(e.target.value)}
              onKeyDown={e => e.key === "Enter" && addOQ()}
              placeholder="Add open question…"
              className="flex-1 text-sm border rounded px-3 py-1.5"
            />
            <button onClick={addOQ} className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700">
              Add
            </button>
          </div>
        </section>

      </div>
    </div>
  );
}
