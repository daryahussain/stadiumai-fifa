"use client"

import Link from "next/link"
import { useRef } from "react"
import { Header } from "@/components/layout/Header"
import { Footer } from "@/components/layout/Footer"
import { MouseFollower } from "@/components/effects/MouseFollower"
import { HeroParallax } from "@/components/effects/HeroParallax"
import { PitchParticles } from "@/components/effects/PitchParticles"
import { motion } from "framer-motion"
import { Bot, Map, Activity, Shield, Bus, Leaf, Bell, TrendingUp, ArrowRight, Sparkles } from "lucide-react"
import { useAuthStore } from "@/store/auth"

const features = [
  { name: "AI Chat", href: "/chat", icon: Bot, desc: "Ask anything about the stadium", color: "from-emerald-500 to-green-600" },
  { name: "Live Crowd", href: "/crowd", icon: Activity, desc: "Real-time crowd intelligence", color: "from-blue-500 to-cyan-600" },
  { name: "Navigation", href: "/navigation", icon: Map, desc: "Interactive stadium maps", color: "from-violet-500 to-purple-600" },
  { name: "Transport", href: "/transport", icon: Bus, desc: "Bus, metro & parking", color: "from-amber-500 to-orange-600" },
  { name: "Emergency", href: "/emergency", icon: Shield, desc: "Emergency assistance", color: "from-red-500 to-rose-600" },
  { name: "Dashboard", href: "/dashboard", icon: TrendingUp, desc: "Operational analytics", color: "from-sky-500 to-indigo-600" },
  { name: "Sustainability", href: "/sustainability", icon: Leaf, desc: "Environmental metrics", color: "from-teal-500 to-emerald-600" },
  { name: "Notifications", href: "/notifications", icon: Bell, desc: "Real-time alerts & updates", color: "from-pink-500 to-rose-600" },
]

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.08 } },
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5 } },
}

function MagneticCard({ children }: { children: React.ReactNode }) {
  const ref = useRef<HTMLDivElement>(null)

  const handleMove = (e: React.MouseEvent) => {
    const el = ref.current
    if (!el) return
    const rect = el.getBoundingClientRect()
    const x = e.clientX - rect.left - rect.width / 2
    const y = e.clientY - rect.top - rect.height / 2
    el.style.transform = `translate(${x * 0.15}px, ${y * 0.15}px)`
  }

  const handleLeave = () => {
    const el = ref.current
    if (!el) return
    el.style.transform = "translate(0px, 0px)"
  }

  return (
    <div ref={ref} onMouseMove={handleMove} onMouseLeave={handleLeave} style={{ transition: "transform 0.3s ease-out" }}>
      {children}
    </div>
  )
}

export default function Home() {
  const user = useAuthStore((s) => s.user)

  return (
    <div className="min-h-screen flex flex-col">
      <MouseFollower />
      <Header />

      <section className="relative overflow-hidden">
        <PitchParticles />
        <div className="relative bg-pitch-pattern">
          <div className="absolute inset-0 bg-gradient-to-b from-background/80 via-transparent to-background/80 pointer-events-none" />
          <div className="relative max-w-6xl mx-auto px-4 py-24 sm:py-32">
            <HeroParallax>
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
                className="text-center max-w-3xl mx-auto"
              >
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2, duration: 0.5 }}
              className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-sm text-primary mb-8"
            >
              <Sparkles className="w-3.5 h-3.5" />
              FIFA World Cup 2026
            </motion.div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight leading-tight">
              The Beautiful Game,{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-emerald-400">
                Intelligently Powered
              </span>
            </h1>

            <p className="mt-6 text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
              &ldquo;Football is the most important of the unimportant things.&rdquo;
              <br />
              <span className="text-sm text-muted-foreground/60">— Eduardo Galeano</span>
            </p>

            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.6, duration: 0.5 }}
              className="mt-4 text-base text-muted-foreground/80"
            >
              StadiumAI brings generative AI to every corner of the venue — from finding your seat to
              live crowd insights, all in real time.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8, duration: 0.5 }}
              className="flex items-center justify-center gap-4 mt-10"
            >
              <Link
                href={user ? "/chat" : "/register"}
                className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-all hover:shadow-lg hover:shadow-primary/25"
              >
                {user ? "Start Chatting" : "Get Started"}
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                href="/crowd"
                className="inline-flex items-center gap-2 px-6 py-3 rounded-xl border border-border bg-card font-medium hover:bg-muted transition-all"
              >
                <Activity className="w-4 h-4" />
                Live Demo
              </Link>
            </motion.div>
          </motion.div>
            </HeroParallax>
          </div>
        </div>
      </section>

      <section className="border-y border-border bg-card/50">
        <div className="max-w-6xl mx-auto px-4 py-12">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {[
              { label: "Stadiums", value: "12" },
              { label: "Matches", value: "64" },
              { label: "Total Capacity", value: "780K" },
              { label: "Countries", value: "48" },
            ].map((stat) => (
              <div key={stat.label} className="text-center">
                <p className="text-3xl sm:text-4xl font-bold text-primary">{stat.value}</p>
                <p className="text-sm text-muted-foreground mt-1">{stat.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20">
        <div className="max-w-6xl mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="text-center mb-12"
          >
            <h2 className="text-3xl font-bold">Everything You Need</h2>
            <p className="text-muted-foreground mt-2">AI-powered tools for the ultimate matchday experience</p>
          </motion.div>

          <motion.div
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4"
          >
            {features.map((f) => {
              const Icon = f.icon
              return (
                <motion.div key={f.name} variants={itemVariants}>
                  <MagneticCard>
                    <Link
                      href={f.href}
                      className="group relative block rounded-xl border border-border bg-card p-6 hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5 transition-all duration-300 overflow-hidden"
                    >
                      <div className={`absolute inset-0 bg-gradient-to-br ${f.color} opacity-0 group-hover:opacity-5 transition-opacity duration-300`} />
                      <div className="relative">
                        <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${f.color} flex items-center justify-center mb-4`}>
                          <Icon className="w-5 h-5 text-white" />
                        </div>
                        <h3 className="font-semibold group-hover:text-primary transition-colors">{f.name}</h3>
                        <p className="text-sm text-muted-foreground mt-1">{f.desc}</p>
                      </div>
                    </Link>
                  </MagneticCard>
                </motion.div>
              )
            })}
          </motion.div>
        </div>
      </section>

      <Footer />
    </div>
  )
}
