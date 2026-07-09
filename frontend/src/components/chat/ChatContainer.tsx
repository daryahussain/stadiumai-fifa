"use client"

import { useEffect, useRef } from "react"
import { ChatMessage } from "./ChatMessage"
import { ChatInput } from "./ChatInput"
import { useChatStore } from "@/store/chat"
import { Bot, Sparkles } from "lucide-react"

export function ChatContainer() {
  const { messages, isLoading, isStreaming, error, sendMessage, loadHistory, sessionId } =
    useChatStore()
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    loadHistory()
  }, [loadHistory])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center space-y-4">
            <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
              <Bot className="w-8 h-8 text-primary" />
            </div>
            <div>
              <h2 className="text-xl font-semibold">StadiumAI Assistant</h2>
              <p className="text-sm text-muted-foreground mt-1">
                Ask me anything about the stadium, matches, or services
              </p>
            </div>
            <div className="grid grid-cols-2 gap-2 max-w-md">
              {[
                "Where is my seat?",
                "Food recommendations?",
                "Nearest restroom?",
                "Match schedule?",
              ].map((q) => (
                <button
                  key={q}
                  onClick={() => sendMessage(q)}
                  disabled={isLoading}
                  className="text-sm px-3 py-2 rounded-xl border border-border bg-muted/50 hover:bg-muted transition-colors text-left disabled:opacity-50"
                >
                  <Sparkles className="w-3 h-3 inline mr-1 text-primary" />
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}
        {messages.map((msg) => {
          const isCurrentlyStreaming = isStreaming && msg.id.startsWith("streaming-")
          return (
            <ChatMessage
              key={msg.id}
              message={msg}
              isStreaming={isCurrentlyStreaming && msg.content.length > 0}
            />
          )
        })}
        {error && (
          <div className="text-sm text-destructive text-center">{error}</div>
        )}
        <div ref={bottomRef} />
      </div>
      <ChatInput onSend={sendMessage} isLoading={isLoading} />
    </div>
  )
}
