const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"
const WS_BASE = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000"

export async function getCrowdData() {
  const res = await fetch(`${API_BASE}/crowd/`)
  if (!res.ok) throw new Error("Failed to fetch crowd data")
  return res.json()
}

export function connectCrowdWebSocket(
  onMessage: (data: unknown) => void,
  onError?: () => void,
): WebSocket {
  const ws = new WebSocket(`${WS_BASE}/ws/crowd`)

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      onMessage(data)
    } catch {
      // ignore parse errors
    }
  }

  ws.onerror = () => onError?.()
  ws.onclose = () => onError?.()

  return ws
}
