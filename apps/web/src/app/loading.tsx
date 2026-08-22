import { Skeleton } from "@/components/ui/Skeleton";

export default function Loading() {
  return (
    <div className="flex min-h-full">
      <div className="hidden shrink-0 border-r border-border md:block" style={{ width: "var(--sidebar-width)" }} />
      <div className="flex-1 px-4 py-6 md:px-6 md:py-8">
        <div className="mx-auto w-full" style={{ maxWidth: "var(--content-max-width)" }}>
          <Skeleton className="h-8 w-72" />
          <Skeleton className="mt-3 h-4 w-96" />
          <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton key={i} className="h-24" />
            ))}
          </div>
          <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-40" />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
