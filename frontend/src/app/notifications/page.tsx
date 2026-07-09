"use client"

import { useEffect, useState } from "react"
import { Header } from "@/components/layout/Header"
import { ProtectedRoute } from "@/components/auth/ProtectedRoute"
import { getNotifications, markNotificationRead } from "@/lib/notifications"
import { Loader2, Bell, AlertTriangle, Cloud, Bus, Info, Calendar } from "lucide-react"
import { cn } from "@/lib/utils"

type Notification = { id: string; title: string; message: string; notification_type: string; is_read: boolean; created_at: string }

const typeIcons: Record<string, typeof Bell> = { match: Calendar, crowd: AlertTriangle, weather: Cloud, transport: Bus, info: Info }

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getNotifications().then((d) => setNotifications(d.notifications)).catch(console.error).finally(() => setLoading(false))
  }, [])

  const handleMarkRead = async (id: string) => {
    await markNotificationRead(id).catch(() => {})
    setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, is_read: true } : n)))
  }

  const unread = notifications.filter((n) => !n.is_read).length

  return (
    <ProtectedRoute>
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 max-w-3xl mx-auto px-4 py-8 w-full">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-2">
            <Bell className="w-6 h-6 text-primary" />
            <h1 className="text-2xl font-bold">Notifications</h1>
          </div>
          {unread > 0 && (
            <span className="px-2.5 py-0.5 rounded-full bg-primary/10 text-primary text-xs font-medium">
              {unread} unread
            </span>
          )}
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20"><Loader2 className="w-6 h-6 animate-spin" /></div>
        ) : notifications.length > 0 ? (
          <div className="space-y-2">
            {notifications.map((n) => {
              const Icon = typeIcons[n.notification_type] || Bell
              return (
                <div key={n.id} onClick={() => !n.is_read && handleMarkRead(n.id)} className={cn(
                  "flex items-start gap-3 p-4 rounded-xl border transition-colors cursor-pointer",
                  n.is_read ? "border-border" : "border-primary/20 bg-primary/5"
                )}>
                  <Icon className={cn("w-5 h-5 mt-0.5 flex-shrink-0", n.is_read ? "text-muted-foreground" : "text-primary")} />
                  <div className="flex-1 min-w-0">
                    <p className={cn("text-sm", !n.is_read && "font-semibold")}>{n.title}</p>
                    <p className="text-xs text-muted-foreground mt-0.5">{n.message}</p>
                  </div>
                  {!n.is_read && <div className="w-2 h-2 rounded-full bg-primary flex-shrink-0 mt-2" />}
                </div>
              )
            })}
          </div>
        ) : (
          <p className="text-center text-muted-foreground py-20">No notifications yet.</p>
        )}
      </main>
    </div>
    </ProtectedRoute>
  )
}
