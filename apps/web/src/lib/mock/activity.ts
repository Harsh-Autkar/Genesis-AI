import type { ActivityItem } from "@/types/activity";

export const mockActivity: ActivityItem[] = [
  {
    id: "act-001",
    type: "paper_uploaded",
    label: "Paper uploaded",
    projectName: "LLM Hallucination Detection",
    timestamp: "2026-08-21T16:03:00.000Z",
  },
  {
    id: "act-002",
    type: "analysis_completed",
    label: "Analysis completed",
    projectName: "Multimodal Medical AI",
    timestamp: "2026-08-21T11:47:00.000Z",
  },
  {
    id: "act-003",
    type: "citation_updated",
    label: "Citation network updated",
    projectName: "Retrieval-Augmented Generation",
    timestamp: "2026-08-20T09:15:00.000Z",
  },
  {
    id: "act-004",
    type: "research_gap_detected",
    label: "Research gap detected",
    projectName: "Efficient Transformer Architectures",
    timestamp: "2026-08-19T14:30:00.000Z",
  },
];
