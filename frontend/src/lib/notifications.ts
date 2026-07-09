const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

export async function getNotifications() {
  const res = await fetch(`${API_BASE}/notifications/`)
  if (!res.ok) throw new Error("Failed to fetch notifications")
  return res.json()
}

export async function markNotificationRead(id: string) {
  const res = await fetch(`${API_BASE}/notifications/${id}/read`, { method: "POST" })
  if (!res.ok) throw new Error("Failed to mark notification as read")
  return res.json()
}
