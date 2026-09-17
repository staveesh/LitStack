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
    <div className="p-6 max-w-3xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Projects</h1>
        <button
          onClick={() => setCreating(true)}
          className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          New Project
        </button>
      </div>

      {creating && (
        <div className="mb-6 p-4 border rounded-lg bg-gray-50 space-y-2">
          <input
            value={newName}
            onChange={e => setNewName(e.target.value)}
            placeholder="Project name"
            className="w-full text-sm border rounded px-3 py-1.5"
            autoFocus
          />
          <input
            value={newDesc}
            onChange={e => setNewDesc(e.target.value)}
            placeholder="Description (optional)"
            className="w-full text-sm border rounded px-3 py-1.5"
          />
          <div className="flex gap-2">
            <button onClick={create} className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700">
              Create
            </button>
            <button onClick={() => setCreating(false)} className="px-3 py-1 text-sm border rounded">
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
            className="block border rounded-lg p-4 bg-white hover:border-blue-300 hover:bg-blue-50/30 transition-colors"
          >
            <div className="flex items-center justify-between">
              <h2 className="font-medium text-gray-900">{proj.name}</h2>
              {!proj.active && <span className="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded">Inactive</span>}
            </div>
            {proj.description && <p className="text-sm text-gray-500 mt-1">{proj.description}</p>}
          </Link>
        ))}
        {projects.length === 0 && (
          <p className="text-gray-400 text-sm text-center py-8">No projects yet.</p>
        )}
      </div>
    </div>
  );
}
