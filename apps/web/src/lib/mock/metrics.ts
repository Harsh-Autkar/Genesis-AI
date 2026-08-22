import type { ResearchMetric } from "@/types/metric";

export const mockMetrics: ResearchMetric[] = [
  { id: "metric-active-projects", label: "Active Projects", value: 2, delta: 1 },
  { id: "metric-papers-analyzed", label: "Papers Analyzed", value: 147, delta: 12 },
  { id: "metric-research-claims", label: "Research Claims", value: 389, delta: 28 },
  { id: "metric-saved-evidence", label: "Saved Evidence", value: 96, delta: -3 },
];
