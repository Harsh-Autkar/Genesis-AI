"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { navSections } from "@/lib/nav-items";
import { cn } from "@/lib/utils";

export function MobileNav() {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();

  return (
    <div className="md:hidden">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-controls="mobile-nav-panel"
        aria-label={open ? "Close navigation" : "Open navigation"}
        className="flex h-9 w-9 items-center justify-center rounded-md text-foreground hover:bg-surface-muted"
      >
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none" aria-hidden="true">
          {open ? (
            <path d="M4 4L14 14M14 4L4 14" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
          ) : (
            <path d="M2 5H16M2 9H16M2 13H16" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
          )}
        </svg>
      </button>

      {open ? (
        <div
          id="mobile-nav-panel"
          className="fixed inset-x-0 top-[var(--header-height)] bottom-0 z-40 overflow-y-auto bg-surface px-4 py-4"
        >
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
                        <span className="flex items-center justify-between rounded-md px-2 py-2 text-body text-muted-foreground/70">
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
                        onClick={() => setOpen(false)}
                        aria-current={isActive ? "page" : undefined}
                        className={cn(
                          "flex items-center rounded-md px-2 py-2 text-body transition-colors",
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
        </div>
      ) : null}
    </div>
  );
}
