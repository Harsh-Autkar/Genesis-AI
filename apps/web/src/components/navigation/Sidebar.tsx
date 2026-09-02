"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { navSections } from "@/lib/nav-items";
import { cn } from "@/lib/utils";

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside
      className="hidden shrink-0 border-r border-border bg-surface md:flex md:flex-col"
      style={{ width: "var(--sidebar-width)" }}
      aria-label="Primary"
    >
      <div className="flex h-[var(--header-height)] items-center px-5">
        <span className="text-h3 tracking-tight text-foreground">Genesis-AI</span>
      </div>

      <nav className="flex-1 overflow-y-auto px-3 pb-4">
        {navSections.map((section) => (
          <div key={section.label || "root"} className="mb-4">
            {section.label ? (
              <p className="px-2 pb-1 pt-2 text-label">{section.label}</p>
            ) : null}
            <ul className="flex flex-col gap-0.5">
              {section.items.map((item) => {
                const isActive = pathname === item.href;

                if (!item.available) {
                  return (
                    <li key={item.label}>
                      <span
                        aria-disabled="true"
                        className="flex items-center justify-between rounded-md px-2 py-1.5 text-body-sm text-muted-foreground/70"
                      >
                        {item.label}
                        <span className="text-caption">Soon</span>
                      </span>
                    </li>
                  );
                }

                return (
                  <li key={item.label}>
                    <Link
                      href={item.href}
                      aria-current={isActive ? "page" : undefined}
                      className={cn(
                        "flex items-center rounded-md px-2 py-1.5 text-body-sm transition-colors",
                        isActive
                          ? "bg-secondary font-medium text-foreground"
                          : "text-muted-foreground hover:bg-surface-muted hover:text-foreground"
                      )}
                    >
                      {item.label}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </nav>
    </aside>
  );
}
