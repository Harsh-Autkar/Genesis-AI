import { MobileNav } from "@/components/navigation/MobileNav";

export function TopBar({ title }: { title: string }) {
  return (
    <header
      className="sticky top-0 z-30 flex items-center justify-between border-b border-border bg-surface/95 px-4 backdrop-blur md:px-6"
      style={{ height: "var(--header-height)" }}
    >
      <div className="flex items-center gap-3">
        <MobileNav />
        <h1 className="text-h3 text-foreground">{title}</h1>
      </div>

      <div className="flex items-center gap-2">
        <button
          type="button"
          aria-label="Search"
          className="flex h-9 w-9 items-center justify-center rounded-md text-muted-foreground hover:bg-surface-muted hover:text-foreground"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
            <circle cx="7" cy="7" r="5" stroke="currentColor" strokeWidth="1.4" />
            <path d="M11 11L14.5 14.5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
          </svg>
        </button>

        <button
          type="button"
          aria-label="Notifications"
          className="flex h-9 w-9 items-center justify-center rounded-md text-muted-foreground hover:bg-surface-muted hover:text-foreground"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
            <path
              d="M8 2.5c-2 0-3.5 1.5-3.5 3.75v2.25L3 10.5h10L11.5 8.5V6.25C11.5 4 10 2.5 8 2.5Z"
              stroke="currentColor"
              strokeWidth="1.3"
              strokeLinejoin="round"
            />
            <path d="M6.5 12.5a1.5 1.5 0 0 0 3 0" stroke="currentColor" strokeWidth="1.3" />
          </svg>
        </button>

        <div
          aria-label="Demo user profile"
          title="Demo profile — not a real account"
          className="ml-1 flex h-8 w-8 items-center justify-center rounded-full bg-secondary text-body-sm font-medium text-secondary-foreground"
        >
          RS
        </div>
      </div>
    </header>
  );
}
