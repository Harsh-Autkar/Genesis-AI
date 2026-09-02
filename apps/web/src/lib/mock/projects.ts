import type { Project } from "@/types/project";

export const mockProjects: Project[] = [
  {
    id: "proj-001",
    name: "LLM Hallucination Detection",
    description:
      "Evaluating factual consistency of generated claims against retrieved source evidence.",
    status: "active",
    papersCount: 34,
    updatedAt: "2026-08-19T10:12:00.000Z",
    tags: ["NLP", "Evaluation"],
  },
  {
    id: "proj-002",
    name: "Multimodal Medical AI",
    description:
      "Literature review on vision-language models applied to diagnostic imaging.",
    status: "active",
    papersCount: 51,
    updatedAt: "2026-08-18T15:40:00.000Z",
    tags: ["Multimodal", "Healthcare"],
  },
  {
    id: "proj-003",
    name: "Retrieval-Augmented Generation",
    description:
      "Comparing retrieval strategies and grounding techniques across RAG architectures.",
    status: "paused",
    papersCount: 22,
    updatedAt: "2026-08-12T09:05:00.000Z",
    tags: ["RAG", "Retrieval"],
  },
  {
    id: "proj-004",
    name: "Efficient Transformer Architectures",
    description:
      "Survey of sparsity, quantization, and attention-approximation methods for inference cost.",
    status: "completed",
    papersCount: 40,
    updatedAt: "2026-08-02T13:22:00.000Z",
    tags: ["Architecture", "Efficiency"],
  },
];
