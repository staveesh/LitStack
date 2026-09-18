"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { api } from "@/lib/api";
import type { Claim, Evidence, Project } from "@/lib/types";

const STATUS_COLORS: Record<string, string> = {
  hypothesis:    "bg-gray-100 text-gray-600",
  weak_evidence: "bg-yellow-100 text-yellow-700",
  supported:     "bg-green-100 text-green-700",
  contested:     "bg-orange-100 text-orange-700",
  rejected:      "bg-red-100 text-red-700",
};

const EVIDENCE_COLORS: Record<string, string> = {
  supports:       "text-green-700",
  contradicts:    "text-red-700",
  qualifies:      "text-yellow-700",
  background:     "text-gray-500",
  methodological: "text-blue-600",
};

function ClaimsContent() {
  const searchParams = useSearchParams();
  const projectFilter = searchParams.get("project");
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<number | "">(
    projectFilter ? Number(projectFilter) : ""
  );
  const [claims, setClaims] = useState<Claim[]>([]);
  const [evidenceMap, setEvidenceMap] = useState<Record<number, Evidence[]>>({});
  const [expandedClaim, setExpandedClaim] = useState<number | null>(null);

  useEffect(() => {
    api.projects.list().then(setProjects);
  }, []);

  useEffect(() => {
    if (!selectedProject) return;
    api.projects.claims(Number(selectedProject)).then(setClaims);
  }, [selectedProject]);

  async function loadEvidence(claimId: number) {
    if (evidenceMap[claimId]) {
      setExpandedClaim(expandedClaim === claimId ? null : claimId);
      return;
    }
    const ev = await api.claims.evidence(claimId);
    setEvidenceMap(prev => ({ ...prev, [claimId]: ev }));
    setExpandedClaim(claimId);
  }

  async function updateStatus(id: number, status: string) {
    const updated = await api.claims.update(id, { status: status as Claim["status"] });
    setClaims(prev => prev.map(c => c.id === id ? updated : c));
  }

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Claim Ledger</h1>

      <div className="mb-6 flex items-center gap-3">
        <select
          value={selectedProject}
          onChange={e => setSelectedProject(e.target.value ? Number(e.target.value) : "")}
          className="text-sm border rounded px-2 py-1.5"
        >
          <option value="">Select a project</option>
          {projects.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
        </select>
        {selectedProject && (
          <button
            onClick={async () => {
              const text = await api.projects.exportBibtex(Number(selectedProject));
              const url = URL.createObjectURL(new Blob([text], { type: "text/plain" }));
              Object.assign(document.createElement("a"), { href: url, download: "references.bib" }).click();
              URL.revokeObjectURL(url);
            }}
            className="text-sm border rounded px-3 py-1.5 hover:bg-gray-50"
          >
            Export BibTeX
          </button>
        )}
      </div>

      {!selectedProject && (
        <p className="text-gray-400 text-sm">Select a project to view its claims.</p>
      )}

      <div className="space-y-4">
        {claims.map(claim => (
          <div key={claim.id} className="border rounded-lg bg-white">
            <div className="p-4">
              <div className="flex items-start gap-3">
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">{claim.claim}</p>
                  {claim.confidence != null && (
                    <p className="text-xs text-gray-400 mt-1">
                      Confidence: {(claim.confidence * 100).toFixed(0)}%
                    </p>
                  )}
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <select
                    value={claim.status}
                    onChange={e => updateStatus(claim.id, e.target.value)}
                    className={`text-xs border rounded px-1.5 py-1 ${STATUS_COLORS[claim.status] ?? ""}`}
                  >
                    {Object.keys(STATUS_COLORS).map(s => (
                      <option key={s} value={s}>{s.replace("_", " ")}</option>
                    ))}
                  </select>
                </div>
              </div>

              <button
                onClick={() => loadEvidence(claim.id)}
                className="text-xs text-blue-500 hover:underline mt-2"
              >
                {expandedClaim === claim.id ? "Hide evidence" : "Show evidence"}
              </button>
            </div>

            {expandedClaim === claim.id && (
              <div className="border-t px-4 py-3 bg-gray-50">
                {(evidenceMap[claim.id] ?? []).length === 0 ? (
                  <p className="text-xs text-gray-400">No evidence linked yet.</p>
                ) : (
                  <div className="space-y-3">
                    {(evidenceMap[claim.id] ?? []).map(ev => (
                      <div key={ev.id} className="text-sm">
                        <span className={`font-semibold text-xs uppercase ${EVIDENCE_COLORS[ev.evidence_type] ?? ""}`}>
                          {ev.evidence_type}
                        </span>
                        <p className="text-gray-700 mt-0.5">{ev.evidence_text}</p>
                        {ev.source_location && (
                          <p className="text-xs text-gray-400 mt-0.5">Source: {ev.source_location}</p>
                        )}
                        {ev.strength && (
                          <p className="text-xs text-gray-400">Strength: {(ev.strength * 100).toFixed(0)}%</p>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}

        {selectedProject && claims.length === 0 && (
          <p className="text-gray-400 text-sm">No claims in this project yet.</p>
        )}
      </div>
    </div>
  );
}

export default function ClaimsPage() {
  return (
    <Suspense>
      <ClaimsContent />
    </Suspense>
  );
}
