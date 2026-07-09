const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

export async function getRoute(from: string, to: string, wheelchair = false) {
  const res = await fetch(`${API_BASE}/navigation/route`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ from_location: from, to_location: to, wheelchair }),
  })
  if (!res.ok) throw new Error("Failed to get route")
  return res.json()
}

export async function getNavigationData() {
  const res = await fetch(`${API_BASE}/navigation/data`)
  if (!res.ok) throw new Error("Failed to get navigation data")
  return res.json()
}
