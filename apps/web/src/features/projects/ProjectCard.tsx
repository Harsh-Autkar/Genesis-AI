import Link from "next/link";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/Card";
import { StatusBadge } from "@/components/feedback/StatusBadge";
import { formatRelativeTime } from "@/lib/utils";
import type { Project } from "@/types/project";

export function ProjectCard({ project }: { project: Project }) {
  return (
    <Card className="flex flex-col transition-shadow hover:shadow-sm">
      <CardHeader className="flex flex-row items-start justify-between gap-3">
        <div>
          <p className="text-h3 text-foreground">{project.name}</p>
          <p className="mt-1 text-body-sm text-muted-foreground">{project.description}</p>
        </div>
        <StatusBadge status={project.status} />
      </CardHeader>

      <CardContent className="flex flex-wrap gap-1.5">
        {project.tags.map((tag) => (
          <span
            key={tag}
            className="rounded-sm bg-surface-muted px-2 py-0.5 text-caption text-muted-foreground"
          >
            {tag}
          </span>
        ))}
      </CardContent>

      <CardFooter>
        <span className="text-caption">
          {project.papersCount} papers · updated {formatRelativeTime(project.updatedAt)}
        </span>
        <Link
          href={`/projects/${project.id}`}
          className="text-body-sm font-medium text-primary hover:underline"
        >
          Open
        </Link>
      </CardFooter>
    </Card>
  );
}
