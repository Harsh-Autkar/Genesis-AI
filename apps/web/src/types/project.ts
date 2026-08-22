export type ProjectStatus =
  | "active"
  | "paused"
  | "completed"
  | "archived";

export interface Project {
  id: string;
  name: string;
  description: string;
  status: ProjectStatus;
  papersCount: number;
  updatedAt: string; // ISO date string
  tags: string[];
}
