import { AppShell } from "@/components/layout/AppShell";
import { Button } from "@/components/ui/Button";
import { ProjectList } from "@/features/projects/ProjectList";
import { mockProjects } from "@/lib/mock/projects";

export default function ProjectsPage() {
  return (
    <AppShell title="Projects">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <p className="text-h1 text-foreground">Projects</p>
          <p className="mt-1 text-body-sm text-muted-foreground">
            {mockProjects.length} research projects
          </p>
        </div>
        <Button size="sm">New Project</Button>
      </div>

      <ProjectList projects={mockProjects} />
    </AppShell>
  );
}
