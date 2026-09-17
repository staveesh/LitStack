import type { WorkflowStatus } from "@/lib/types";

const COLORS: Record<WorkflowStatus, string> = {
  inbox:        "bg-gray-100 text-gray-700",
  triaged:      "bg-blue-100 text-blue-700",
  skim:         "bg-yellow-100 text-yellow-700",
  deep_read:    "bg-purple-100 text-purple-700",
  read:         "bg-green-100 text-green-700",
  citation_only:"bg-orange-100 text-orange-700",
  archived:     "bg-gray-200 text-gray-500",
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
    <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${COLORS[status]}`}>
      {LABELS[status]}
    </span>
  );
}
