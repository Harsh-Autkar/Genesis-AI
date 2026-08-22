"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";

export interface ErrorStateProps {
  title?: string;
  description?: string;
  detail?: string;
  onRetry?: () => void;
}

export function ErrorState({
  title = "Something went wrong",
  description = "This section couldn't be loaded. You can try again.",
  detail,
  onRetry,
}: ErrorStateProps) {
  const [showDetail, setShowDetail] = useState(false);

  return (
    <div className="rounded-lg border border-border bg-danger-bg/40 px-6 py-8 text-center">
      <p className="text-h3 text-foreground">{title}</p>
      <p className="mt-1.5 text-body-sm text-muted-foreground">{description}</p>
      <div className="mt-4 flex items-center justify-center gap-3">
        {onRetry ? (
          <Button variant="outline" size="sm" onClick={onRetry}>
            Retry
          </Button>
        ) : null}
        {detail ? (
          <Button variant="ghost" size="sm" onClick={() => setShowDetail((v) => !v)}>
            {showDetail ? "Hide details" : "Show details"}
          </Button>
        ) : null}
      </div>
      {showDetail && detail ? (
        <pre className="mt-4 overflow-x-auto rounded-md bg-surface p-3 text-left text-code text-muted-foreground">
          {detail}
        </pre>
      ) : null}
    </div>
  );
}
