const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

export async function getDashboardData(token?: string) {
  const headers: Record<string, string> = { "Content-Type": "application/json" }
  if (token) headers["Authorization"] = `Bearer ${token}`

  const res = await fetch(`${API_BASE}/dashboard/`, { headers })
  if (!res.ok) throw new Error("Failed to fetch dashboard data")
  return res.json()
}
