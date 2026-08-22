import { ProjectCard } from "@/features/projects/ProjectCard";
import { EmptyState } from "@/components/feedback/EmptyState";
import { Button } from "@/components/ui/Button";
import type { Project } from "@/types/project";

export function ProjectList({ projects }: { projects: Project[] }) {
  if (projects.length === 0) {
    return (
      <EmptyState
        title="No projects yet"
        description="Create a research project to start organizing papers, evidence, and analysis."
        action={<Button size="sm">New Project</Button>}
      />
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
      {projects.map((project) => (
        <ProjectCard key={project.id} project={project} />
      ))}
    </div>
  );
}
