"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function SettingsPage() {
  const [zoteroStatus, setZoteroStatus] = useState<Record<string, unknown>>({});
  const [syncing, setSyncing] = useState(false);
  const [health, setHealth] = useState<string>("checking…");

  useEffect(() => {
    api.zotero.status().then(setZoteroStatus).catch(() => {});
    fetch("/api/health")
      .then(r => r.json())
      .then(d => setHealth(d.status ?? "ok"))
      .catch(() => setHealth("unreachable"));
  }, []);

  async function sync() {
    setSyncing(true);
    const result = await api.zotero.sync().catch(e => ({ error: String(e) }));
    setZoteroStatus(result);
    setSyncing(false);
  }

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Settings</h1>

      <section className="mb-8">
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">Backend</h2>
        <div className="p-3 border rounded bg-white text-sm">
          <span className="text-gray-600">API status: </span>
          <span className={health === "ok" ? "text-green-600" : "text-red-500"}>{health}</span>
        </div>
      </section>

      <section className="mb-8">
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">Zotero Sync</h2>
        <div className="p-4 border rounded bg-white space-y-3">
          {zoteroStatus.synced ? (
            <div className="text-sm">
              <p className="text-gray-600">
                Last sync: {zoteroStatus.last_sync
                  ? new Date(zoteroStatus.last_sync as string).toLocaleString()
                  : "never"}
              </p>
              {zoteroStatus.imported != null && (
                <p className="text-gray-500 text-xs mt-1">
                  {zoteroStatus.imported as number} imported, {zoteroStatus.updated as number} updated, {zoteroStatus.skipped as number} skipped
                </p>
              )}
            </div>
          ) : (
            <p className="text-sm text-gray-400">
              {zoteroStatus.error
                ? String(zoteroStatus.error)
                : "Not synced yet. Configure ZOTERO_API_KEY and ZOTERO_LIBRARY_ID in .env"}
            </p>
          )}
          <button
            onClick={sync}
            disabled={syncing}
            className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {syncing ? "Syncing…" : "Sync Now"}
          </button>
        </div>
      </section>

      <section>
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">AI Provider</h2>
        <div className="p-4 border rounded bg-white text-sm text-gray-500">
          <p>Configure via environment variables in <code className="bg-gray-100 px-1 rounded">.env</code>:</p>
          <ul className="mt-2 space-y-1 font-mono text-xs">
            <li>ANTHROPIC_API_KEY</li>
            <li>OPENAI_API_KEY</li>
            <li>DEFAULT_AI_PROVIDER=anthropic|openai|local</li>
            <li>LOCAL_LLM_BASE_URL (optional, for LM Studio)</li>
          </ul>
          <p className="mt-3 text-amber-700 text-xs">
            ⚠ When AI features are used, paper abstracts and PDF text are sent to the configured provider.
            Content leaves this machine. Use local models to keep all data local.
          </p>
        </div>
      </section>
    </div>
  );
}
