import Link from "next/link";
import { AppShell } from "@/components/layout/AppShell";
import { Button } from "@/components/ui/Button";
import { MetricCard } from "@/features/projects/MetricCard";
import { RecentActivity } from "@/features/projects/RecentActivity";
import { ProjectCard } from "@/features/projects/ProjectCard";
import { mockProjects } from "@/lib/mock/projects";
import { mockActivity } from "@/lib/mock/activity";
import { mockMetrics } from "@/lib/mock/metrics";

export default function DashboardPage() {
  const recentProjects = mockProjects.slice(0, 3);

  return (
    <AppShell title="Overview">
      <section className="mb-8">
        <p className="text-display text-foreground">Research Intelligence Workspace</p>
        <p className="mt-1.5 max-w-2xl text-body text-muted-foreground">
          Organize literature, track evidence, and monitor analysis across your research
          projects.
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          <Button size="sm">New Project</Button>
          <Button size="sm" variant="outline">
            Upload Paper
          </Button>
          <Button size="sm" variant="outline">
            Search Literature
          </Button>
        </div>
      </section>

      <section className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {mockMetrics.map((metric) => (
          <MetricCard key={metric.id} metric={metric} />
        ))}
      </section>

      <section className="mb-8">
        <div className="mb-3 flex items-center justify-between">
          <p className="text-h2 text-foreground">Recent Projects</p>
          <Link href="/projects" className="text-body-sm font-medium text-primary hover:underline">
            View all
          </Link>
        </div>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {recentProjects.map((project) => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>
      </section>

      <section>
        <RecentActivity items={mockActivity} />
      </section>
    </AppShell>
  );
}
