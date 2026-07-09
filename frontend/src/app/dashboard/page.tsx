"use client"

import { useEffect, useState } from "react"
import { Header } from "@/components/layout/Header"
import { ProtectedRoute } from "@/components/auth/ProtectedRoute"
import { StatCard } from "@/components/dashboard/StatCard"
import { MatchSchedule } from "@/components/dashboard/MatchSchedule"
import { AlertsPanel } from "@/components/dashboard/AlertsPanel"
import { CrowdChart } from "@/components/dashboard/CrowdChart"
import { AIInsights } from "@/components/dashboard/AIInsights"
import { getDashboardData } from "@/lib/dashboard"
import { useAuthStore } from "@/store/auth"
import { Loader2 } from "lucide-react"

interface DashboardData {
  stats: { label: string; value: string; change: string; trend: string }[]
  matches: {
    id: string
    home_team: string
    away_team: string
    match_date: string
    status: string
    sold_tickets: number
    total_tickets: number
  }[]
  alerts: {
    id: string
    type: string
    severity: number
    description: string
    location: string
    created_at: string
  }[]
  crowd_trend: { hour: string; density: number }[]
  ai_insight: string
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const { token } = useAuthStore()

  useEffect(() => {
    getDashboardData(token || undefined)
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [token])

  return (
    <ProtectedRoute>
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 max-w-6xl mx-auto px-4 py-8 w-full">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-2xl font-bold">Operational Dashboard</h1>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
          </div>
        ) : data ? (
          <div className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {data.stats.map((s) => (
                <StatCard key={s.label} {...(s as { label: string; value: string; change: string; trend: "up" | "down" | "neutral" })} />
              ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <CrowdChart data={data.crowd_trend} />
              <AIInsights insight={data.ai_insight} />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <MatchSchedule matches={data.matches} />
              <AlertsPanel alerts={data.alerts} />
            </div>
          </div>
        ) : (
          <p className="text-center text-muted-foreground py-20">
            Failed to load dashboard data.
          </p>
        )}
      </main>
    </div>
    </ProtectedRoute>
  )
}
