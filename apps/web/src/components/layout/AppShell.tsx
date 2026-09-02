import type { ReactNode } from "react";
import { Sidebar } from "@/components/navigation/Sidebar";
import { TopBar } from "@/components/navigation/TopBar";

export function AppShell({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="flex min-h-full">
      <Sidebar />
      <div className="flex min-h-full flex-1 flex-col">
        <TopBar title={title} />
        <main className="flex-1 px-4 py-6 md:px-6 md:py-8">
          <div className="mx-auto w-full" style={{ maxWidth: "var(--content-max-width)" }}>
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
