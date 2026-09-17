/**
 * Visual marker for AI-generated content.
 * Must always be visible when AI content is displayed — never omit.
 */
export function AIBadge({ model, version }: { model?: string | null; version?: string | null }) {
  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs bg-amber-100 text-amber-700 border border-amber-300 font-medium">
      <span>AI</span>
      {model && <span className="opacity-70">· {model.split("/").pop()}</span>}
      {version && <span className="opacity-50">v{version.split("-v").pop()}</span>}
    </span>
  );
}

export function HumanBadge() {
  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs bg-green-100 text-green-700 border border-green-300 font-medium">
      Your Notes
    </span>
  );
}
