"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { ResearchQuestion } from "@/lib/types";

const STATUS_OPTIONS = ["active", "partially_answered", "answered", "abandoned"] as const;

export default function ResearchQuestionsPage() {
  const [rqs, setRqs] = useState<ResearchQuestion[]>([]);

  useEffect(() => {
    api.rqs.listAll().then(setRqs);
  }, []);

  async function updateStatus(id: number, status: string) {
    const updated = await api.rqs.update(id, { status: status as ResearchQuestion["status"] });
    setRqs(prev => prev.map(r => r.id === id ? updated : r));
  }

  const grouped = rqs.reduce<Record<string, ResearchQuestion[]>>((acc, rq) => {
    (acc[rq.status] = acc[rq.status] ?? []).push(rq);
    return acc;
  }, {});

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Research Questions</h1>
      {STATUS_OPTIONS.map(status => {
        const items = grouped[status];
        if (!items?.length) return null;
        return (
          <section key={status} className="mb-8">
            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
              {status.replace("_", " ")} ({items.length})
            </h2>
            <div className="space-y-2">
              {items.map(rq => (
                <div key={rq.id} className="p-3 border rounded bg-white flex items-start gap-3">
                  <div className="flex-1">
                    <p className="text-sm text-gray-800">{rq.question}</p>
                    {rq.motivation && <p className="text-xs text-gray-400 mt-1">{rq.motivation}</p>}
                  </div>
                  <select
                    value={rq.status}
                    onChange={e => updateStatus(rq.id, e.target.value)}
                    className="text-xs border rounded px-1.5 py-1 shrink-0"
                  >
                    {STATUS_OPTIONS.map(s => <option key={s} value={s}>{s.replace("_", " ")}</option>)}
                  </select>
                </div>
              ))}
            </div>
          </section>
        );
      })}
      {rqs.length === 0 && (
        <p className="text-gray-400 text-sm text-center py-8">
          No research questions. Create them inside a project.
        </p>
      )}
    </div>
  );
}
