import { Clock, TrendingUp, TrendingDown, Minus } from "lucide-react"
import { cn } from "@/lib/utils"

interface Queue {
  location: string
  type: string
  wait_minutes: number
  trend: string
}

interface QueueListProps {
  queues: Queue[]
}

const typeLabels: Record<string, string> = {
  entry: "Entry Gate",
  food: "Food Court",
  restroom: "Restroom",
  service: "Service",
}

export function QueueList({ queues }: QueueListProps) {
  return (
    <div className="rounded-xl border border-border p-4">
      <div className="flex items-center gap-2 mb-4">
        <Clock className="w-5 h-5 text-primary" />
        <h3 className="font-semibold">Wait Times</h3>
      </div>
      <div className="space-y-3">
        {queues.map((q) => {
          const TrendIcon =
            q.trend === "rising"
              ? TrendingUp
              : q.trend === "falling"
                ? TrendingDown
                : Minus
          return (
            <div
              key={q.location}
              className="flex items-center justify-between p-3 rounded-lg bg-muted/50"
            >
              <div>
                <p className="text-sm font-medium">{q.location}</p>
                <p className="text-xs text-muted-foreground">
                  {typeLabels[q.type] || q.type}
                </p>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-sm font-bold">{q.wait_minutes} min</span>
                <TrendIcon
                  className={cn(
                    "w-4 h-4",
                    q.trend === "rising" && "text-red-500",
                    q.trend === "falling" && "text-green-500",
                    q.trend === "stable" && "text-muted-foreground"
                  )}
                />
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
