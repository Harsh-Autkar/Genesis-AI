import { Badge } from "@/components/ui/Badge";
import type { ProjectStatus } from "@/types/project";

const statusConfig: Record<ProjectStatus, { label: string; tone: "success" | "warning" | "neutral" | "info" }> = {
  active: { label: "Active", tone: "success" },
  paused: { label: "Paused", tone: "warning" },
  completed: { label: "Completed", tone: "info" },
  archived: { label: "Archived", tone: "neutral" },
};

export function StatusBadge({ status }: { status: ProjectStatus }) {
  const config = statusConfig[status];
  return <Badge tone={config.tone}>{config.label}</Badge>;
}
