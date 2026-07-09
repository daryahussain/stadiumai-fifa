export interface ChatMessage {
  id: string
  role: "user" | "assistant"
  content: string
  created_at: string
}

export interface ChatState {
  messages: ChatMessage[]
  sessionId: string | null
  isLoading: boolean
  error: string | null
}
