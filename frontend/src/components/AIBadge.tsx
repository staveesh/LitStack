/**
 * Visual marker for AI-generated content.
 * Must always be visible when AI content is displayed — never omit.
 */
export function AIBadge({ model, version }: { model?: string | null; version?: string | null }) {
  return (
    <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
      <span className="w-1.5 h-1.5 rounded-full bg-amber-400 inline-block" />
      AI
      {model && <span className="opacity-60 font-normal">· {model.split("/").pop()}</span>}
      {version && <span className="opacity-40 font-normal">v{version.split("-v").pop()}</span>}
    </span>
  );
}

export function HumanBadge() {
  return (
    <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 inline-block" />
      Your Notes
    </span>
  );
}
