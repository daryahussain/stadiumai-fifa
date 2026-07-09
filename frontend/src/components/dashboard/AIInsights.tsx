import { Bot, Sparkles } from "lucide-react"

interface AIInsightsProps {
  insight: string
}

export function AIInsights({ insight }: AIInsightsProps) {
  return (
    <div className="rounded-xl border border-border p-4">
      <div className="flex items-center gap-2 mb-4">
        <Bot className="w-5 h-5 text-primary" />
        <h3 className="font-semibold">AI Insights</h3>
      </div>
      <div className="bg-primary/5 rounded-lg p-4 border border-primary/10">
        <Sparkles className="w-4 h-4 text-primary mb-2" />
        <p className="text-sm leading-relaxed">{insight}</p>
      </div>
    </div>
  )
}
