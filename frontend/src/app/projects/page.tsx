"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { Project } from "@/lib/types";

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [creating, setCreating] = useState(false);
  const [newName, setNewName] = useState("");
  const [newDesc, setNewDesc] = useState("");

  useEffect(() => {
    api.projects.list().then(setProjects);
  }, []);

  async function create() {
    if (!newName.trim()) return;
    const proj = await api.projects.create({ name: newName.trim(), description: newDesc.trim() || undefined });
    setProjects(prev => [proj, ...prev]);
    setNewName("");
    setNewDesc("");
    setCreating(false);
  }

  return (
    <div className="p-8 max-w-3xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Projects</h1>
          <p className="text-sm text-slate-400 mt-0.5">{projects.length} project{projects.length !== 1 ? "s" : ""}</p>
        </div>
        <button
          onClick={() => setCreating(true)}
          className="px-4 py-2 text-sm font-medium bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors shadow-sm"
        >
          New Project
        </button>
      </div>

      {creating && (
        <div className="mb-6 p-5 border border-indigo-200 rounded-xl bg-indigo-50 space-y-3">
          <input
            value={newName}
            onChange={e => setNewName(e.target.value)}
            placeholder="Project name"
            className="w-full text-sm border border-slate-200 rounded-lg px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-300 transition-all"
            autoFocus
          />
          <input
            value={newDesc}
            onChange={e => setNewDesc(e.target.value)}
            placeholder="Description (optional)"
            className="w-full text-sm border border-slate-200 rounded-lg px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-300 transition-all"
          />
          <div className="flex gap-2">
            <button onClick={create} className="px-4 py-1.5 text-sm font-medium bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors">
              Create
            </button>
            <button onClick={() => setCreating(false)} className="px-4 py-1.5 text-sm border border-slate-200 rounded-lg hover:bg-white transition-colors">
              Cancel
            </button>
          </div>
        </div>
      )}

      <div className="space-y-3">
        {projects.map(proj => (
          <Link
            key={proj.id}
            href={`/projects/${proj.id}`}
            className="block border border-slate-200 rounded-xl p-5 bg-white shadow-card hover:shadow-card-hover hover:-translate-y-0.5 transition-all duration-200"
          >
            <div className="flex items-center justify-between">
              <h2 className="font-semibold text-slate-900">{proj.name}</h2>
              {!proj.active && (
                <span className="text-xs text-slate-400 bg-slate-100 border border-slate-200 px-2.5 py-0.5 rounded-full">Inactive</span>
              )}
            </div>
            {proj.description && <p className="text-sm text-slate-500 mt-1.5 leading-relaxed">{proj.description}</p>}
          </Link>
        ))}
        {projects.length === 0 && (
          <div className="text-center py-16 text-slate-400">
            <p className="text-4xl mb-3">🗂</p>
            <p className="text-sm">No projects yet.</p>
          </div>
        )}
      </div>
    </div>
  );
}
