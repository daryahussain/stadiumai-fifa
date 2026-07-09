import { create } from "zustand"
import type { ChatMessage } from "@/types/chat"
import { sendChatMessage, getChatHistory, sendStreamingMessage } from "@/lib/api"

interface ChatStore {
  messages: ChatMessage[]
  sessionId: string | null
  isLoading: boolean
  isStreaming: boolean
  streamingContent: string
  error: string | null
  sendMessage: (content: string) => Promise<void>
  loadHistory: () => Promise<void>
}

export const useChatStore = create<ChatStore>((set, get) => ({
  messages: [],
  sessionId: null,
  isLoading: false,
  isStreaming: false,
  streamingContent: "",
  error: null,

  sendMessage: async (content: string) => {
    const { sessionId } = get()
    set({ isLoading: true, error: null, streamingContent: "" })

    const tempId = `temp-${Date.now()}`
    const userMessage: ChatMessage = {
      id: tempId,
      role: "user",
      content,
      created_at: new Date().toISOString(),
    }
    set((state) => ({ messages: [...state.messages, userMessage] }))

    const tempAiId = `streaming-${Date.now()}`
    const streamingMessage: ChatMessage = {
      id: tempAiId,
      role: "assistant",
      content: "",
      created_at: new Date().toISOString(),
    }
    set((state) => ({
      messages: [...state.messages, streamingMessage],
      isStreaming: true,
    }))

    let accumulated = ""

    await sendStreamingMessage(
      content,
      sessionId || undefined,
      (token) => {
        accumulated += token
        set((state) => ({
          streamingContent: accumulated,
          messages: state.messages.map((m) =>
            m.id === tempAiId ? { ...m, content: accumulated } : m,
          ),
        }))
      },
      (newSessionId, messageId) => {
        set((state) => ({
          messages: state.messages.map((m) =>
            m.id === tempAiId
              ? { ...m, id: messageId, content: accumulated }
              : m,
          ),
          sessionId: newSessionId,
          isLoading: false,
          isStreaming: false,
          streamingContent: "",
        }))
      },
      () => {
        set((state) => ({
          messages: state.messages.filter(
            (m) => m.id !== tempAiId && m.id !== tempId,
          ),
          isLoading: false,
          isStreaming: false,
          streamingContent: "",
          error: "Failed to send message. Is the backend running?",
        }))
      },
    )
  },

  loadHistory: async () => {
    const { sessionId } = get()
    if (!sessionId) return
    try {
      const data = await getChatHistory(sessionId)
      set({ messages: data.messages })
    } catch {
      // no history yet — that's fine
    }
  },
}))
