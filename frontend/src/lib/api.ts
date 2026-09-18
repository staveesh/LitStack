const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`API ${res.status}: ${text}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  // Papers
  papers: {
    list: (params?: Record<string, string>) => {
      const qs = params ? "?" + new URLSearchParams(params).toString() : "";
      return req<import("./types").Paper[]>(`/api/papers${qs}`);
    },
    get: (id: number) => req<import("./types").Paper>(`/api/papers/${id}`),
    create: (body: Partial<import("./types").Paper>) =>
      req<import("./types").Paper>("/api/papers", { method: "POST", body: JSON.stringify(body) }),
    update: (id: number, body: Partial<import("./types").Paper>) =>
      req<import("./types").Paper>(`/api/papers/${id}`, { method: "PUT", body: JSON.stringify(body) }),
    delete: (id: number, zotero = false) =>
      req<void>(`/api/papers/${id}${zotero ? "?zotero=true" : ""}`, { method: "DELETE" }),
    linkRQ: (paperId: number, rqId: number) =>
      req<void>(`/api/papers/${paperId}/research-questions/${rqId}`, { method: "POST" }),
    unlinkRQ: (paperId: number, rqId: number) =>
      req<void>(`/api/papers/${paperId}/research-questions/${rqId}`, { method: "DELETE" }),
    linkProject: (paperId: number, projectId: number) =>
      req<void>(`/api/papers/${paperId}/projects/${projectId}`, { method: "POST" }),
    unlinkProject: (paperId: number, projectId: number) =>
      req<void>(`/api/papers/${paperId}/projects/${projectId}`, { method: "DELETE" }),
  },

  // Reading intents
  intents: {
    list: (paperId: number) =>
      req<import("./types").ReadingIntent[]>(`/api/papers/${paperId}/reading-intents`),
    create: (paperId: number, intent: string, rqId?: number) =>
      req<import("./types").ReadingIntent>(`/api/papers/${paperId}/reading-intents`, {
        method: "POST",
        body: JSON.stringify({ paper_id: paperId, intent, research_question_id: rqId }),
      }),
    resolve: (paperId: number, intentId: number, notes?: string) =>
      req<import("./types").ReadingIntent>(`/api/papers/${paperId}/reading-intents/${intentId}/resolve`, {
        method: "POST",
        body: JSON.stringify({ resolution_notes: notes }),
      }),
  },

  // Notes
  notes: {
    get: (paperId: number) => req<import("./types").HumanNote>(`/api/papers/${paperId}/notes`),
    save: (paperId: number, body: Partial<import("./types").HumanNote>) =>
      req<import("./types").HumanNote>(`/api/papers/${paperId}/notes`, {
        method: "PUT",
        body: JSON.stringify(body),
      }),
  },

  // Extraction
  extraction: {
    get: (paperId: number) =>
      req<import("./types").PaperExtraction>(`/api/papers/${paperId}/extraction`),
    trigger: (paperId: number) =>
      req<import("./types").PaperExtraction>(`/api/papers/${paperId}/extraction`, { method: "POST" }),
  },

  // Projects
  projects: {
    list: () => req<import("./types").Project[]>("/api/projects"),
    get: (id: number) => req<import("./types").Project>(`/api/projects/${id}`),
    create: (body: { name: string; description?: string }) =>
      req<import("./types").Project>("/api/projects", { method: "POST", body: JSON.stringify(body) }),
    update: (id: number, body: Partial<import("./types").Project>) =>
      req<import("./types").Project>(`/api/projects/${id}`, { method: "PUT", body: JSON.stringify(body) }),
    rqs: (projectId: number) =>
      req<import("./types").ResearchQuestion[]>(`/api/projects/${projectId}/research-questions`),
    createRQ: (projectId: number, body: { question: string; motivation?: string }) =>
      req<import("./types").ResearchQuestion>(`/api/projects/${projectId}/research-questions`, {
        method: "POST",
        body: JSON.stringify({ ...body, project_id: projectId }),
      }),
    claims: (projectId: number) =>
      req<import("./types").Claim[]>(`/api/projects/${projectId}/claims`),
    exportBibtex: (projectId: number) =>
      fetch(`${BASE}/api/projects/${projectId}/claims/bibtex`).then(r => r.text()),
    createClaim: (projectId: number, body: { claim: string; notes?: string }) =>
      req<import("./types").Claim>(`/api/projects/${projectId}/claims`, {
        method: "POST",
        body: JSON.stringify({ ...body, project_id: projectId }),
      }),
    openQuestions: (projectId: number) =>
      req<import("./types").OpenQuestion[]>(`/api/projects/${projectId}/open-questions`),
    createOQ: (projectId: number, body: { question: string; origin?: string }) =>
      req<import("./types").OpenQuestion>(`/api/projects/${projectId}/open-questions`, {
        method: "POST",
        body: JSON.stringify({ ...body, project_id: projectId }),
      }),
  },

  // Research questions
  rqs: {
    listAll: () => req<import("./types").ResearchQuestion[]>("/api/research-questions"),
    update: (id: number, body: Partial<import("./types").ResearchQuestion>) =>
      req<import("./types").ResearchQuestion>(`/api/research-questions/${id}`, {
        method: "PUT",
        body: JSON.stringify(body),
      }),
  },

  // Claims
  claims: {
    evidence: (claimId: number) => req<import("./types").Evidence[]>(`/api/claims/${claimId}/evidence`),
    addEvidence: (claimId: number, body: Omit<import("./types").Evidence, "id">) =>
      req<import("./types").Evidence>(`/api/claims/${claimId}/evidence`, {
        method: "POST",
        body: JSON.stringify(body),
      }),
    deleteEvidence: (evidenceId: number) =>
      req<void>(`/api/evidence/${evidenceId}`, { method: "DELETE" }),
    update: (id: number, body: Partial<import("./types").Claim>) =>
      req<import("./types").Claim>(`/api/claims/${id}`, { method: "PUT", body: JSON.stringify(body) }),
  },

  // Zotero
  zotero: {
    sync: () => req<Record<string, unknown>>("/api/zotero/sync", { method: "POST" }),
    status: () => req<Record<string, unknown>>("/api/zotero/status"),
  },

  // AI
  ai: {
    triage: (paperIds: number[], projectId?: number) =>
      req<import("./types").TriageResult[]>("/api/ai/triage", {
        method: "POST",
        body: JSON.stringify({ paper_ids: paperIds, project_id: projectId }),
      }),
    applyTriage: (body: {
      paper_id: number;
      workflow_status: string;
      relevance_score: number;
      reading_intent?: string;
      research_question_ids?: number[];
    }) => req<void>("/api/ai/triage/apply", { method: "POST", body: JSON.stringify(body) }),
    claimSuggestions: (paperId: number, projectId: number) =>
      req<unknown[]>(`/api/ai/claim-suggestions/${paperId}?project_id=${projectId}`, { method: "POST" }),
    oqSuggestions: (paperId: number, projectId: number) =>
      req<unknown[]>(`/api/ai/open-question-suggestions/${paperId}?project_id=${projectId}`, { method: "POST" }),
  },
};
