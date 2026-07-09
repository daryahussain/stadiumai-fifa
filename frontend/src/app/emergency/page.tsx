"use client"

import { useState, FormEvent } from "react"
import { Header } from "@/components/layout/Header"
import { ProtectedRoute } from "@/components/auth/ProtectedRoute"
import { reportIncident } from "@/lib/incidents"
import { useAuthStore } from "@/store/auth"
import { Loader2, Shield, AlertTriangle, CheckCircle } from "lucide-react"

const INCIDENT_TYPES = [
  { value: "medical", label: "Medical Emergency" },
  { value: "security", label: "Security Issue" },
  { value: "fire", label: "Fire" },
  { value: "lost_child", label: "Lost Child" },
  { value: "suspicious_activity", label: "Suspicious Activity" },
  { value: "maintenance", label: "Maintenance Issue" },
]

export default function EmergencyPage() {
  const [type, setType] = useState("")
  const [description, setDescription] = useState("")
  const [location, setLocation] = useState("")
  const [severity, setSeverity] = useState(1)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<{ id: string; ai_response: string } | null>(null)
  const [error, setError] = useState("")
  const { token } = useAuthStore()

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError("")
    setLoading(true)
    try {
      const data = await reportIncident({ incident_type: type, description, location, severity }, token || undefined)
      setResult(data)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }

  if (result) {
    return (
      <ProtectedRoute>
      <div className="min-h-screen flex flex-col">
        <Header />
        <main className="flex-1 flex items-center justify-center px-4">
          <div className="max-w-md text-center space-y-4">
            <CheckCircle className="w-16 h-16 text-green-500 mx-auto" />
            <h2 className="text-2xl font-bold">Incident Reported</h2>
            <div className="rounded-xl border border-border p-4 bg-muted/50">
              <p className="text-sm">{result.ai_response}</p>
            </div>
            <p className="text-xs text-muted-foreground">Reference: {result.id.slice(0, 8)}</p>
            <button onClick={() => setResult(null)} className="text-sm text-primary hover:underline">
              Report another
            </button>
          </div>
        </main>
      </div>
      </ProtectedRoute>
    )
  }

  return (
    <ProtectedRoute>
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 max-w-2xl mx-auto px-4 py-8 w-full">
        <div className="flex items-center gap-2 mb-8">
          <Shield className="w-6 h-6 text-primary" />
          <h1 className="text-2xl font-bold">Emergency Response</h1>
        </div>

        <div className="rounded-xl border border-border p-6">
          <div className="flex items-start gap-3 mb-6 p-3 rounded-lg bg-amber-500/10 border border-amber-500/20">
            <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-amber-700">
              For life-threatening emergencies, call <strong>+1-800-FIFA-HELP</strong> or contact the nearest staff member immediately.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-sm font-medium">Incident Type</label>
              <select value={type} onChange={(e) => setType(e.target.value)} required
                className="w-full mt-1 rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary">
                <option value="">Select type</option>
                {INCIDENT_TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
              </select>
            </div>
            <div>
              <label className="text-sm font-medium">Location</label>
              <input type="text" value={location} onChange={(e) => setLocation(e.target.value)} required placeholder="e.g. Gate C, Section 200, Concourse East"
                className="w-full mt-1 rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary" />
            </div>
            <div>
              <label className="text-sm font-medium">Severity (1-5)</label>
              <div className="flex items-center gap-2 mt-1">
                <input type="range" min={1} max={5} value={severity} onChange={(e) => setSeverity(Number(e.target.value))} className="flex-1" />
                <span className="text-sm font-bold w-6 text-center">{severity}</span>
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                {severity === 1 ? "Low" : severity === 2 ? "Moderate" : severity === 3 ? "Medium" : severity === 4 ? "High" : "Critical"}
              </p>
            </div>
            <div>
              <label className="text-sm font-medium">Description</label>
              <textarea value={description} onChange={(e) => setDescription(e.target.value)} required rows={3}
                className="w-full mt-1 rounded-lg border border-input bg-background px-3 py-2 text-sm outline-none focus:border-primary focus:ring-1 focus:ring-primary resize-none" />
            </div>
            {error && <p className="text-sm text-destructive">{error}</p>}
            <button type="submit" disabled={loading}
              className="w-full rounded-lg bg-destructive text-destructive-foreground py-2 text-sm font-medium hover:bg-destructive/90 transition-colors disabled:opacity-50 flex items-center justify-center gap-2">
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Shield className="w-4 h-4" />}
              Report Incident
            </button>
          </form>
        </div>
      </main>
    </div>
    </ProtectedRoute>
  )
}
