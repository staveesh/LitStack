import type { WorkflowStatus } from "@/lib/types";

const COLORS: Record<WorkflowStatus, string> = {
  inbox:        "bg-slate-100 text-slate-600 border-slate-200",
  triaged:      "bg-blue-50 text-blue-700 border-blue-200",
  skim:         "bg-amber-50 text-amber-700 border-amber-200",
  deep_read:    "bg-violet-50 text-violet-700 border-violet-200",
  read:         "bg-emerald-50 text-emerald-700 border-emerald-200",
  citation_only:"bg-orange-50 text-orange-700 border-orange-200",
  archived:     "bg-slate-100 text-slate-400 border-slate-200",
};

const LABELS: Record<WorkflowStatus, string> = {
  inbox:        "Inbox",
  triaged:      "Triaged",
  skim:         "Skim",
  deep_read:    "Deep Read",
  read:         "Read",
  citation_only:"Citation Only",
  archived:     "Archived",
};

export function WorkflowBadge({ status }: { status: WorkflowStatus }) {
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${COLORS[status]}`}>
      {LABELS[status]}
    </span>
  );
}
