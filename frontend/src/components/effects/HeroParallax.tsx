"use client"

import { useRef, useState, useEffect } from "react"
import { motion } from "framer-motion"

interface HeroParallaxProps {
  children: React.ReactNode
}

export function HeroParallax({ children }: HeroParallaxProps) {
  const ref = useRef<HTMLDivElement>(null)
  const [rotateX, setRotateX] = useState(0)
  const [rotateY, setRotateY] = useState(0)

  useEffect(() => {
    const el = ref.current
    if (!el) return

    const handleMove = (e: MouseEvent) => {
      const rect = el.getBoundingClientRect()
      const centerX = rect.left + rect.width / 2
      const centerY = rect.top + rect.height / 2
      const maxTilt = 4

      const x = ((e.clientX - centerX) / centerX) * maxTilt
      const y = ((e.clientY - centerY) / centerY) * maxTilt

      setRotateX(-y)
      setRotateY(x)
    }

    const handleLeave = () => {
      setRotateX(0)
      setRotateY(0)
    }

    el.addEventListener("mousemove", handleMove)
    el.addEventListener("mouseleave", handleLeave)

    return () => {
      el.removeEventListener("mousemove", handleMove)
      el.removeEventListener("mouseleave", handleLeave)
    }
  }, [])

  return (
    <motion.div
      ref={ref}
      style={{ perspective: 1000 }}
      animate={{ rotateX, rotateY }}
      transition={{ type: "spring", stiffness: 100, damping: 15 }}
    >
      {children}
    </motion.div>
  )
}
