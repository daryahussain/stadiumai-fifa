import { AlertTriangle, Shield } from "lucide-react"
import { cn } from "@/lib/utils"

interface Alert {
  id: string
  type: string
  severity: number
  description: string
  location: string
  created_at: string
}

interface AlertsPanelProps {
  alerts: Alert[]
}

export function AlertsPanel({ alerts }: AlertsPanelProps) {
  return (
    <div className="rounded-xl border border-border p-4">
      <div className="flex items-center gap-2 mb-4">
        <Shield className="w-5 h-5 text-primary" />
        <h3 className="font-semibold">Active Incidents</h3>
      </div>
      {alerts.length === 0 ? (
        <p className="text-sm text-muted-foreground">No active incidents.</p>
      ) : (
        <div className="space-y-2">
          {alerts.map((a) => (
            <div
              key={a.id}
              className="flex items-start gap-3 p-3 rounded-lg bg-muted/50"
            >
              <AlertTriangle
                className={cn(
                  "w-4 h-4 mt-0.5 flex-shrink-0",
                  a.severity >= 4
                    ? "text-red-500"
                    : a.severity >= 2
                      ? "text-amber-500"
                      : "text-blue-500"
                )}
              />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium capitalize">{a.type}</p>
                <p className="text-xs text-muted-foreground truncate">
                  {a.description} — {a.location}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
