"use client"

import { useEffect, useRef, useState } from "react"
import { Header } from "@/components/layout/Header"
import { ZoneGrid } from "@/components/crowd/ZoneGrid"
import { QueueList } from "@/components/crowd/QueueList"
import { getCrowdData, connectCrowdWebSocket } from "@/lib/crowd"
import { Loader2, Brain, Wifi, WifiOff } from "lucide-react"
import { cn } from "@/lib/utils"

interface CrowdData {
  overview: { total_occupancy: number; total_capacity: number; avg_density: number; congestion_level: string }
  zones: { zone: string; density: number; status: string; wait_time: number }[]
  queues: { location: string; type: string; wait_minutes: number; trend: string }[]
  ai_summary: string
}

export default function CrowdPage() {
  const [data, setData] = useState<CrowdData | null>(null)
  const [loading, setLoading] = useState(true)
  const [connected, setConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    getCrowdData()
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false))

    const ws = connectCrowdWebSocket(
      (d) => {
        setData(d as CrowdData)
        setConnected(true)
        setLoading(false)
      },
      () => setConnected(false),
    )
    wsRef.current = ws

    return () => {
      ws.close()
    }
  }, [])

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 max-w-6xl mx-auto px-4 py-8 w-full">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-2xl font-bold">Live Crowd Intelligence</h1>
          <div className="flex items-center gap-2 text-xs">
            {connected ? (
              <>
                <Wifi className="w-3.5 h-3.5 text-green-500" />
                <span className="flex items-center gap-1.5 text-green-600 font-medium">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75" />
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500" />
                  </span>
                  LIVE
                </span>
              </>
            ) : (
              <>
                <WifiOff className="w-3.5 h-3.5 text-muted-foreground" />
                <span className="text-muted-foreground">Disconnected</span>
              </>
            )}
          </div>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
          </div>
        ) : data ? (
          <div className="space-y-6">
            <div className={cn(
              "grid grid-cols-1 sm:grid-cols-3 gap-4 transition-opacity duration-500",
              connected ? "opacity-100" : "opacity-80",
            )}>
              <div className="rounded-xl border border-border p-4">
                <p className="text-sm text-muted-foreground">Occupancy</p>
                <p className="text-2xl font-bold mt-1">
                  {data.overview.total_occupancy.toLocaleString()} /{" "}
                  {data.overview.total_capacity.toLocaleString()}
                </p>
              </div>
              <div className="rounded-xl border border-border p-4">
                <p className="text-sm text-muted-foreground">Avg Density</p>
                <p className="text-2xl font-bold mt-1">{data.overview.avg_density}%</p>
              </div>
              <div className="rounded-xl border border-border p-4">
                <p className="text-sm text-muted-foreground">Congestion</p>
                <p className="text-2xl font-bold mt-1 capitalize">
                  {data.overview.congestion_level}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <ZoneGrid zones={data.zones} />
              </div>
              <QueueList queues={data.queues} />
            </div>

            <div className="rounded-xl border border-border p-4">
              <div className="flex items-center gap-2 mb-3">
                <Brain className="w-5 h-5 text-primary" />
                <h3 className="font-semibold">AI Analysis</h3>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed">
                {data.ai_summary}
              </p>
            </div>
          </div>
        ) : (
          <p className="text-center text-muted-foreground py-20">
            Failed to load crowd data.
          </p>
        )}
      </main>
    </div>
  )
}
