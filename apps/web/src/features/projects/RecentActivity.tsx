import { Card } from "@/components/ui/Card";
import { formatRelativeTime } from "@/lib/utils";
import type { ActivityItem } from "@/types/activity";

export function RecentActivity({ items }: { items: ActivityItem[] }) {
  return (
    <Card>
      <div className="border-b border-border p-5">
        <p className="text-h3 text-foreground">Recent Activity</p>
      </div>
      <ul className="divide-y divide-border">
        {items.map((item) => (
          <li key={item.id} className="flex items-center justify-between px-5 py-3">
            <div>
              <p className="text-body-sm text-foreground">{item.label}</p>
              <p className="text-caption">{item.projectName}</p>
            </div>
            <span className="text-caption">{formatRelativeTime(item.timestamp)}</span>
          </li>
        ))}
      </ul>
    </Card>
  );
}
