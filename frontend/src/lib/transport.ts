const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

export async function getTransportData() {
  const res = await fetch(`${API_BASE}/transport/`)
  if (!res.ok) throw new Error("Failed to fetch transport data")
  return res.json()
}
