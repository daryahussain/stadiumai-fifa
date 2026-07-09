const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

export async function reportIncident(data: {
  incident_type: string
  description: string
  location: string
  severity: number
}, token?: string) {
  const headers: Record<string, string> = { "Content-Type": "application/json" }
  if (token) headers["Authorization"] = `Bearer ${token}`
  const res = await fetch(`${API_BASE}/reports/incidents`, {
    method: "POST",
    headers,
    body: JSON.stringify(data),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Failed to report" }))
    throw new Error(err.detail)
  }
  return res.json()
}
