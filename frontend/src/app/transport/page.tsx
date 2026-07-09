"use client"

import { useEffect, useState } from "react"
import { Header } from "@/components/layout/Header"
import { getTransportData } from "@/lib/transport"
import { Loader2, Bus, Train, Car, Brain, Clock } from "lucide-react"

type TransportOption = { type: string; name: string; status: string; next_arrival: string; wait_minutes: number }
type ParkingInfo = { lot: string; available_spots: number; total_spots: number; distance_m: number; status: string }

interface TransportData {
  options: TransportOption[]
  parking: ParkingInfo[]
  ai_recommendation: string
}

const typeIcons: Record<string, typeof Bus> = { metro: Train, bus: Bus, taxi: Car }

export default function TransportPage() {
  const [data, setData] = useState<TransportData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getTransportData().then(setData).catch(console.error).finally(() => setLoading(false))
  }, [])

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 max-w-6xl mx-auto px-4 py-8 w-full">
        <h1 className="text-2xl font-bold mb-8">Transportation Intelligence</h1>

        {loading ? (
          <div className="flex items-center justify-center py-20"><Loader2 className="w-6 h-6 animate-spin" /></div>
        ) : data ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-6">
              <div className="rounded-xl border border-border p-4">
                <div className="flex items-center gap-2 mb-4">
                  <Bus className="w-5 h-5 text-primary" />
                  <h3 className="font-semibold">Transit Options</h3>
                </div>
                <div className="space-y-3">
                  {data.options.map((o) => {
                    const Icon = typeIcons[o.type] || Bus
                    return (
                      <div key={o.name} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                        <div className="flex items-center gap-3">
                          <Icon className="w-5 h-5 text-muted-foreground" />
                          <div>
                            <p className="text-sm font-medium">{o.name}</p>
                            <p className="text-xs text-muted-foreground capitalize">{o.status}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-bold">{o.next_arrival}</p>
                          <p className="text-xs text-muted-foreground">{o.wait_minutes > 0 ? `${o.wait_minutes} min wait` : "now"}</p>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>

              <div className="rounded-xl border border-border p-4">
                <div className="flex items-center gap-2 mb-4">
                  <Clock className="w-5 h-5 text-primary" />
                  <h3 className="font-semibold">AI Travel Recommendation</h3>
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed">{data.ai_recommendation}</p>
              </div>
            </div>

            <div className="rounded-xl border border-border p-4">
              <div className="flex items-center gap-2 mb-4">
                <Car className="w-5 h-5 text-primary" />
                <h3 className="font-semibold">Parking Availability</h3>
              </div>
              <div className="space-y-3">
                {data.parking.map((p) => (
                  <div key={p.lot} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                    <div>
                      <p className="text-sm font-medium">{p.lot}</p>
                      <p className="text-xs text-muted-foreground">{p.distance_m}m from stadium</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-bold">{p.available_spots}/{p.total_spots}</p>
                      <p className="text-xs capitalize text-muted-foreground">{p.status}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <p className="text-center text-muted-foreground py-20">Failed to load transport data.</p>
        )}
      </main>
    </div>
  )
}
