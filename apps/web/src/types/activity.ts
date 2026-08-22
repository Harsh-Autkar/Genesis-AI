export type ActivityType =
  | "paper_uploaded"
  | "analysis_completed"
  | "citation_updated"
  | "research_gap_detected";

export interface ActivityItem {
  id: string;
  type: ActivityType;
  label: string;
  projectName: string;
  timestamp: string; // ISO date string
}
