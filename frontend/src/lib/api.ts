const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

export async function sendChatMessage(message: string, sessionId?: string) {
  const res = await fetch(`${API_BASE}/chat/message`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id: sessionId }),
  })
  if (!res.ok) throw new Error("Failed to send message")
  return res.json()
}

export async function getChatHistory(sessionId: string) {
  const res = await fetch(`${API_BASE}/chat/history/${sessionId}`)
  if (!res.ok) throw new Error("Failed to fetch history")
  return res.json()
}

export async function sendStreamingMessage(
  message: string,
  sessionId: string | undefined,
  onToken: (token: string) => void,
  onDone: (sessionId: string, messageId: string) => void,
  onError: () => void,
): Promise<void> {
  try {
    const res = await fetch(`${API_BASE}/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, session_id: sessionId }),
    })

    if (!res.ok) {
      onError()
      return
    }

    const reader = res.body?.getReader()
    if (!reader) {
      onError()
      return
    }

    const decoder = new TextDecoder()
    let buffer = ""

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split("\n")
      buffer = lines.pop() || ""

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          try {
            const data = JSON.parse(line.slice(6))
            if (data.done) {
              onDone(data.session_id, data.message_id)
              return
            }
            if (data.token) {
              onToken(data.token)
            }
          } catch {
            // skip malformed chunks
          }
        }
      }
    }
  } catch {
    onError()
  }
}
