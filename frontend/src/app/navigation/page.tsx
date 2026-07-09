"use client"

import { useEffect, useState } from "react"
import { Header } from "@/components/layout/Header"
import { StadiumMap } from "@/components/navigation/StadiumMap"
import { RouteFinder } from "@/components/navigation/RouteFinder"
import { RouteResult } from "@/components/navigation/RouteResult"
import { getNavigationData } from "@/lib/navigation"
import { Loader2, Map } from "lucide-react"

interface NavData {
  zones: string[]
  gates: { gate: string; recommended_for: string[]; distance_m: number; crowd_level: string }[]
  amenities: string[]
}

interface RouteData {
  from_location: string
  to_location: string
  total_distance_m: number
  estimated_minutes: number
  steps: { instruction: string; distance_m: number; landmark: string }[]
  wheelchair_accessible: boolean
}

export default function NavigationPage() {
  const [data, setData] = useState<NavData | null>(null)
  const [route, setRoute] = useState<RouteData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getNavigationData()
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 max-w-6xl mx-auto px-4 py-8 w-full">
        <div className="flex items-center gap-2 mb-8">
          <Map className="w-6 h-6 text-primary" />
          <h1 className="text-2xl font-bold">Smart Navigation</h1>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
          </div>
        ) : data ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
              <StadiumMap
                zones={data.zones.slice(0, 6)}
                onSelectZone={(z) => console.log(z)}
              />
              {route && <RouteResult route={route} />}
            </div>
            <div className="space-y-6">
              <RouteFinder
                locations={data.zones}
                onRouteFound={setRoute}
              />

              <div className="rounded-xl border border-border p-4">
                <h3 className="font-semibold mb-3">Gate Recommendations</h3>
                <div className="space-y-2">
                  {data.gates.map((g) => (
                    <div
                      key={g.gate}
                      className="flex items-center justify-between p-3 rounded-lg bg-muted/50"
                    >
                      <div>
                        <p className="text-sm font-medium">{g.gate}</p>
                        <p className="text-xs text-muted-foreground">
                          {g.recommended_for.join(", ")}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-bold">{g.distance_m}m</p>
                        <p className="text-xs capitalize text-muted-foreground">
                          {g.crowd_level}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="rounded-xl border border-border p-4">
                <h3 className="font-semibold mb-3">Amenities</h3>
                <ul className="space-y-1">
                  {data.amenities.map((a) => (
                    <li key={a} className="text-sm text-muted-foreground">
                      • {a}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        ) : (
          <p className="text-center text-muted-foreground py-20">
            Failed to load navigation data.
          </p>
        )}
      </main>
    </div>
  )
}
