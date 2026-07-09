import { cn } from "@/lib/utils"

interface Zone {
  zone: string
  density: number
  status: string
  wait_time: number
}

interface ZoneGridProps {
  zones: Zone[]
}

function getStatusColor(status: string) {
  switch (status) {
    case "congested":
      return "bg-red-500/10 border-red-500/30 text-red-600"
    case "busy":
      return "bg-amber-500/10 border-amber-500/30 text-amber-600"
    case "moderate":
      return "bg-blue-500/10 border-blue-500/30 text-blue-600"
    case "clear":
      return "bg-green-500/10 border-green-500/30 text-green-600"
    default:
      return "bg-muted border-border"
  }
}

export function ZoneGrid({ zones }: ZoneGridProps) {
  return (
    <div className="rounded-xl border border-border p-4">
      <h3 className="font-semibold mb-4">Zone Density</h3>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
        {zones.map((z) => (
          <div
            key={z.zone}
            className={cn(
              "rounded-lg border p-3",
              getStatusColor(z.status)
            )}
          >
            <p className="text-xs font-medium uppercase tracking-wide">
              {z.zone}
            </p>
            <p className="text-lg font-bold mt-1">{z.density}%</p>
            <div className="mt-2 w-full h-1.5 rounded-full bg-background/50 overflow-hidden">
              <div
                className={cn(
                  "h-full rounded-full transition-all",
                  z.density >= 80
                    ? "bg-red-500"
                    : z.density >= 60
                      ? "bg-amber-500"
                      : z.density >= 40
                        ? "bg-blue-500"
                        : "bg-green-500"
                )}
                style={{ width: `${z.density}%` }}
              />
            </div>
            <p className="text-xs mt-1 capitalize">{z.status}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
