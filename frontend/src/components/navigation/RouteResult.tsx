import { Route } from "lucide-react"

interface RouteResultProps {
  route: {
    from_location: string
    to_location: string
    total_distance_m: number
    estimated_minutes: number
    steps: { instruction: string; distance_m: number; landmark: string }[]
    wheelchair_accessible: boolean
  }
}

export function RouteResult({ route }: RouteResultProps) {
  return (
    <div className="rounded-xl border border-border p-4">
      <div className="flex items-center gap-2 mb-4">
        <Route className="w-5 h-5 text-primary" />
        <h3 className="font-semibold">Directions</h3>
      </div>
      <div className="flex items-center gap-4 mb-4 text-sm">
        <span className="text-muted-foreground">
          {route.from_location} → {route.to_location}
        </span>
        <span className="px-2 py-0.5 rounded-full bg-muted text-xs font-medium">
          {route.total_distance_m}m
        </span>
        <span className="px-2 py-0.5 rounded-full bg-muted text-xs font-medium">
          ~{route.estimated_minutes} min
        </span>
        {route.wheelchair_accessible && (
          <span className="px-2 py-0.5 rounded-full bg-green-100 text-green-700 text-xs font-medium">
            Wheelchair
          </span>
        )}
      </div>
      <div className="space-y-2">
        {route.steps.map((step, i) => (
          <div key={i} className="flex items-start gap-3">
            <div className="flex flex-col items-center">
              <div className="w-6 h-6 rounded-full bg-primary/10 text-primary text-xs font-bold flex items-center justify-center">
                {i + 1}
              </div>
              {i < route.steps.length - 1 && (
                <div className="w-px h-8 bg-border" />
              )}
            </div>
            <div className="flex-1 pb-4">
              <p className="text-sm">{step.instruction}</p>
              <p className="text-xs text-muted-foreground mt-0.5">
                {step.distance_m}m — Past {step.landmark}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
