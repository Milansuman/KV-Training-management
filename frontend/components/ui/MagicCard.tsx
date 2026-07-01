"use client";

import { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface MagicCardProps {
  children: ReactNode;
  className?: string;
  glow?: boolean;
  hover?: boolean;
}

export default function MagicCard({
  children,
  className,
}: MagicCardProps) {
  return (
    <div
      className={cn(
        "group relative overflow-hidden rounded-3xl border border-border/60 bg-card p-6 transition-all duration-300",
        "hover:-translate-y-1 hover:shadow-2xl",
        className
      )}
    >
      {/* Glow */}
      <div className="pointer-events-none absolute inset-0 opacity-0 transition-opacity duration-300 group-hover:opacity-100">
        <div className="absolute left-1/2 top-1/2 h-[250px] w-[250px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary/15 blur-3xl" />
      </div>

      {/* Border glow */}
      <div className="pointer-events-none absolute inset-0 rounded-3xl border border-primary/10 group-hover:border-primary/40 transition-colors" />

      {/* Content */}
      <div className="relative z-10">
        {children}
      </div>
    </div>
  );
}