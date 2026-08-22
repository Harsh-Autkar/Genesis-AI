import { Card } from "@/components/ui/Card";
import type { ResearchMetric } from "@/types/metric";

export function MetricCard({ metric }: { metric: ResearchMetric }) {
  const hasDelta = typeof metric.delta === "number" && metric.delta !== 0;
  const isPositive = (metric.delta ?? 0) > 0;

  return (
    <Card className="p-5">
      <p className="text-label">{metric.label}</p>
      <div className="mt-2 flex items-baseline gap-2">
        <p className="text-display text-foreground">{metric.value}</p>
        {hasDelta ? (
          <span
            className={`text-body-sm font-medium ${isPositive ? "text-success" : "text-danger"}`}
          >
            {isPositive ? "+" : ""}
            {metric.delta}
          </span>
        ) : null}
      </div>
    </Card>
  );
}
