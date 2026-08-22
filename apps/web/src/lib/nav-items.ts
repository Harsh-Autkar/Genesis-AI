import type { NavSection } from "@/types/navigation";

export const navSections: NavSection[] = [
  {
    label: "",
    items: [{ label: "Overview", href: "/", available: true }],
  },
  {
    label: "Workspace",
    items: [
      { label: "Projects", href: "/projects", available: true },
      { label: "Papers", href: "/papers", available: false },
      { label: "Search", href: "/search", available: false },
    ],
  },
  {
    label: "Analysis",
    items: [
      { label: "Citations", href: "/citations", available: false },
      { label: "Claims", href: "/claims", available: false },
      { label: "Novelty", href: "/novelty", available: false },
      { label: "Research Gaps", href: "/research-gaps", available: false },
    ],
  },
  {
    label: "Intelligence",
    items: [
      { label: "Recommendations", href: "/recommendations", available: false },
    ],
  },
  {
    label: "System",
    items: [{ label: "Settings", href: "/settings", available: false }],
  },
];
