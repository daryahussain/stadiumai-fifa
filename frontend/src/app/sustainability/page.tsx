"use client"

import { useEffect, useState } from "react"
import { Header } from "@/components/layout/Header"
import { getSustainabilityData } from "@/lib/sustainability"
import { Loader2, Leaf, TrendingUp, TrendingDown, Minus, Brain } from "lucide-react"
import { cn } from "@/lib/utils"

type Metric = { label: string; value: string; unit: string; change: string; trend: string }
interface SustainabilityData { metrics: Metric[]; ai_recommendation: string }

const trendIcons = { up: TrendingUp, down: TrendingDown, neutral: Minus }

export default function SustainabilityPage() {
  const [data, setData] = useState<SustainabilityData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getSustainabilityData().then(setData).catch(console.error).finally(() => setLoading(false))
  }, [])

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 max-w-6xl mx-auto px-4 py-8 w-full">
        <div className="flex items-center gap-2 mb-8">
          <Leaf className="w-6 h-6 text-primary" />
          <h1 className="text-2xl font-bold">Sustainability</h1>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20"><Loader2 className="w-6 h-6 animate-spin" /></div>
        ) : data ? (
          <div className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {data.metrics.map((m) => {
                const Trend = trendIcons[m.trend as keyof typeof trendIcons] || Minus
                return (
                  <div key={m.label} className="rounded-xl border border-border p-4">
                    <p className="text-sm text-muted-foreground">{m.label}</p>
                    <p className="text-2xl font-bold mt-1">
                      {m.value} <span className="text-sm font-normal text-muted-foreground">{m.unit}</span>
                    </p>
                    <span className={cn("flex items-center gap-1 text-xs mt-2 font-medium",
                      m.trend === "up" && "text-green-600",
                      m.trend === "down" && "text-red-600",
                      m.trend === "neutral" && "text-muted-foreground"
                    )}>
                      <Trend className="w-3 h-3" />
                      {m.change}
                    </span>
                  </div>
                )
              })}
            </div>

            <div className="rounded-xl border border-border p-4">
              <div className="flex items-center gap-2 mb-3">
                <Brain className="w-5 h-5 text-primary" />
                <h3 className="font-semibold">AI Sustainability Insights</h3>
              </div>
              <p className="text-sm text-muted-foreground leading-relaxed">{data.ai_recommendation}</p>
            </div>
          </div>
        ) : (
          <p className="text-center text-muted-foreground py-20">Failed to load sustainability data.</p>
        )}
      </main>
    </div>
  )
}
