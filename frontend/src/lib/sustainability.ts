const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

export async function getSustainabilityData() {
  const res = await fetch(`${API_BASE}/sustainability/`)
  if (!res.ok) throw new Error("Failed to fetch sustainability data")
  return res.json()
}
