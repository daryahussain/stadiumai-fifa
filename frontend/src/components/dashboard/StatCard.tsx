import { TrendingUp, TrendingDown, Minus } from "lucide-react"
import { cn } from "@/lib/utils"

interface StatCardProps {
  label: string
  value: string
  change: string
  trend: "up" | "down" | "neutral"
}

export function StatCard({ label, value, change, trend }: StatCardProps) {
  const Icon =
    trend === "up"
      ? TrendingUp
      : trend === "down"
        ? TrendingDown
        : Minus

  return (
    <div className="rounded-xl border border-border p-4">
      <p className="text-sm text-muted-foreground">{label}</p>
      <div className="flex items-end justify-between mt-2">
        <p className="text-2xl font-bold">{value}</p>
        <span
          className={cn(
            "flex items-center gap-1 text-xs font-medium",
            trend === "up" && "text-green-600",
            trend === "down" && "text-red-600",
            trend === "neutral" && "text-muted-foreground"
          )}
        >
          <Icon className="w-3 h-3" />
          {change}
        </span>
      </div>
    </div>
  )
}
