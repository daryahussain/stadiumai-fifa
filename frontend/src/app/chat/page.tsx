"use client"

import { ProtectedRoute } from "@/components/auth/ProtectedRoute"
import { ChatContainer } from "@/components/chat/ChatContainer"

export default function ChatPage() {
  return (
    <ProtectedRoute>
    <main className="h-screen flex flex-col">
      <ChatContainer />
    </main>
    </ProtectedRoute>
  )
}
