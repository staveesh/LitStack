"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { OpenQuestion, Project } from "@/lib/types";

export default function OpenQuestionsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<number | "">("");
  const [oqs, setOqs] = useState<OpenQuestion[]>([]);

  useEffect(() => { api.projects.list().then(setProjects); }, []);

  useEffect(() => {
    if (!selectedProject) return;
    api.projects.openQuestions(Number(selectedProject)).then(
      items => setOqs(items.sort((a, b) => (b.importance ?? 0) - (a.importance ?? 0)))
    );
  }, [selectedProject]);

  async function updateStatus(id: number, status: string) {
    const updated = await api.claims.update(id, {} as never); // reuse update endpoint
    // Optimistic update
    setOqs(prev => prev.map(q => q.id === id ? { ...q, status: status as OpenQuestion["status"] } : q));
    // Actually call the right endpoint
    await fetch(`/api/open-questions/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status }),
    });
  }

  const STATUS_COLORS: Record<string, string> = {
    open: "bg-blue-100 text-blue-700",
    investigating: "bg-purple-100 text-purple-700",
    answered: "bg-green-100 text-green-700",
    converted_to_experiment: "bg-teal-100 text-teal-700",
    abandoned: "bg-gray-100 text-gray-400",
  };

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Open Questions</h1>

      <div className="mb-6">
        <select
          value={selectedProject}
          onChange={e => setSelectedProject(e.target.value ? Number(e.target.value) : "")}
          className="text-sm border rounded px-2 py-1.5"
        >
          <option value="">Select a project</option>
          {projects.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
        </select>
      </div>

      <div className="space-y-3">
        {oqs.map(oq => (
          <div key={oq.id} className="p-4 border rounded-lg bg-white">
            <div className="flex items-start gap-3">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">{oq.question}</p>
                {oq.origin && <p className="text-xs text-gray-400 mt-1">Origin: {oq.origin}</p>}
                {oq.notes && <p className="text-xs text-gray-500 mt-1">{oq.notes}</p>}
              </div>
              <div className="flex flex-col items-end gap-1.5 shrink-0">
                <span className={`text-xs px-2 py-0.5 rounded ${STATUS_COLORS[oq.status] ?? "bg-gray-100"}`}>
                  {oq.status.replace("_", " ")}
                </span>
                {oq.importance && (
                  <div className="flex gap-0.5">
                    {Array.from({ length: 5 }, (_, i) => (
                      <div
                        key={i}
                        className={`w-1.5 h-3 rounded-sm ${i < oq.importance! ? "bg-orange-400" : "bg-gray-200"}`}
                      />
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
        {selectedProject && oqs.length === 0 && (
          <p className="text-gray-400 text-sm">No open questions yet.</p>
        )}
        {!selectedProject && (
          <p className="text-gray-400 text-sm">Select a project to view open questions.</p>
        )}
      </div>
    </div>
  );
}
