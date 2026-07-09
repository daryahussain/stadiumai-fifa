import { Calendar } from "lucide-react"

interface Match {
  id: string
  home_team: string
  away_team: string
  match_date: string
  status: string
  sold_tickets: number
  total_tickets: number
}

interface MatchScheduleProps {
  matches: Match[]
}

export function MatchSchedule({ matches }: MatchScheduleProps) {
  return (
    <div className="rounded-xl border border-border p-4">
      <div className="flex items-center gap-2 mb-4">
        <Calendar className="w-5 h-5 text-primary" />
        <h3 className="font-semibold">Upcoming Matches</h3>
      </div>
      {matches.length === 0 ? (
        <p className="text-sm text-muted-foreground">No matches scheduled today.</p>
      ) : (
        <div className="space-y-3">
          {matches.map((m) => (
            <div
              key={m.id}
              className="flex items-center justify-between p-3 rounded-lg bg-muted/50"
            >
              <div>
                <p className="text-sm font-medium">
                  {m.home_team} vs {m.away_team}
                </p>
                <p className="text-xs text-muted-foreground mt-0.5">
                  {new Date(m.match_date).toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm font-medium">
                  {m.sold_tickets}/{m.total_tickets}
                </p>
                <p className="text-xs text-muted-foreground">tickets sold</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
