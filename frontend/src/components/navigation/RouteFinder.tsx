"use client"

import { useState } from "react"
import { getRoute } from "@/lib/navigation"
import { Loader2, MapPin, Footprints, Accessibility } from "lucide-react"

interface RouteResult {
  from_location: string
  to_location: string
  total_distance_m: number
  estimated_minutes: number
  steps: { instruction: string; distance_m: number; landmark: string }[]
  wheelchair_accessible: boolean
}

interface RouteFinderProps {
  locations: string[]
  onRouteFound: (route: RouteResult) => void
}

export function RouteFinder({ locations, onRouteFound }: RouteFinderProps) {
  const [from, setFrom] = useState("")
  const [to, setTo] = useState("")
  const [wheelchair, setWheelchair] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)
    try {
      const data = await getRoute(from, to, wheelchair)
      onRouteFound(data)
    } catch {
      setError("Could not find a route between these locations.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="rounded-xl border border-border p-4">
      <div className="flex items-center gap-2 mb-4">
        <MapPin className="w-5 h-5 text-primary" />
        <h3 className="font-semibold">Find Route</h3>
      </div>
      <form onSubmit={handleSubmit} className="space-y-3">
        <div>
          <label className="text-xs font-medium">From</label>
          <select
            value={from}
            onChange={(e) => setFrom(e.target.value)}
            required
            className="w-full mt-1 rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary"
          >
            <option value="">Select location</option>
            {locations.map((l) => (
              <option key={l} value={l}>{l}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="text-xs font-medium">To</label>
          <select
            value={to}
            onChange={(e) => setTo(e.target.value)}
            required
            className="w-full mt-1 rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary"
          >
            <option value="">Select location</option>
            {locations.map((l) => (
              <option key={l} value={l}>{l}</option>
            ))}
          </select>
        </div>
        <label className="flex items-center gap-2 text-sm cursor-pointer">
          <input
            type="checkbox"
            checked={wheelchair}
            onChange={(e) => setWheelchair(e.target.checked)}
            className="rounded border-input"
          />
          <Accessibility className="w-4 h-4" />
          Wheelchair accessible route
        </label>
        {error && <p className="text-xs text-destructive">{error}</p>}
        <button
          type="submit"
          disabled={loading || !from || !to}
          className="w-full rounded-lg bg-primary text-primary-foreground py-2 text-sm font-medium hover:bg-primary/90 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {loading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Footprints className="w-4 h-4" />
          )}
          Get Directions
        </button>
      </form>
    </div>
  )
}
