export interface ResearchMetric {
  id: string;
  label: string;
  value: number;
  delta?: number; // positive/negative change, optional
}
