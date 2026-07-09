"use client"

import { cn } from "@/lib/utils"

interface StadiumMapProps {
  zones: string[]
  onSelectZone: (zone: string) => void
}

const sectionColors = [
  "bg-red-100 border-red-300 text-red-700",
  "bg-blue-100 border-blue-300 text-blue-700",
  "bg-green-100 border-green-300 text-green-700",
  "bg-amber-100 border-amber-300 text-amber-700",
  "bg-purple-100 border-purple-300 text-purple-700",
]

export function StadiumMap({ zones, onSelectZone }: StadiumMapProps) {
  return (
    <div className="rounded-xl border border-border p-6">
      <div className="relative mx-auto max-w-md aspect-square">
        <div className="absolute inset-4 rounded-full border-4 border-muted-foreground/20 flex items-center justify-center">
          <span className="text-xs text-muted-foreground">PITCH</span>
        </div>

        <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2">
          <div className="bg-muted-foreground/10 rounded-full px-3 py-1 text-xs font-medium">
            NORTH
          </div>
        </div>

        <div className="grid grid-cols-3 gap-2 absolute inset-0 p-4">
          <div className="flex flex-col gap-2 justify-center">
            {zones.slice(0, 2).map((z, i) => (
              <button
                key={z}
                onClick={() => onSelectZone(z)}
                className={cn(
                  "text-[10px] leading-tight px-2 py-2 rounded-lg border text-center hover:opacity-80 transition-opacity cursor-pointer",
                  sectionColors[i % sectionColors.length]
                )}
              >
                {z}
              </button>
            ))}
          </div>
          <div className="flex flex-col gap-2 justify-center">
            {zones.slice(2, 4).map((z, i) => (
              <button
                key={z}
                onClick={() => onSelectZone(z)}
                className={cn(
                  "text-[10px] leading-tight px-2 py-2 rounded-lg border text-center hover:opacity-80 transition-opacity cursor-pointer",
                  sectionColors[(i + 2) % sectionColors.length]
                )}
              >
                {z}
              </button>
            ))}
          </div>
          <div className="flex flex-col gap-2 justify-center">
            {zones.slice(4, 6).map((z, i) => (
              <button
                key={z}
                onClick={() => onSelectZone(z)}
                className={cn(
                  "text-[10px] leading-tight px-2 py-2 rounded-lg border text-center hover:opacity-80 transition-opacity cursor-pointer",
                  sectionColors[(i + 4) % sectionColors.length]
                )}
              >
                {z}
              </button>
            ))}
          </div>
        </div>
      </div>
      <p className="text-xs text-muted-foreground text-center mt-4">
        Click a zone to select it as a destination
      </p>
    </div>
  )
}
