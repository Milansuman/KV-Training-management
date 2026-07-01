"use client";

import { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface MagicBentoProps {
  children: ReactNode;
  className?: string;
}

export default function MagicBento({
  children,
  className,
}: MagicBentoProps) {
  return (
    <>
      <style jsx global>{`
        .magic-bento-grid {
          display: grid;
          gap: 1rem;
          grid-template-columns: repeat(4, minmax(0, 1fr));
          grid-auto-rows: 220px;
        }

        @media (max-width: 1280px) {
          .magic-bento-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
          }
        }

        @media (max-width: 768px) {
          .magic-bento-grid {
            grid-template-columns: 1fr;
          }
        }

        .magic-card {
          position: relative;
          overflow: hidden;
          border-radius: 24px;
          border: 1px solid hsl(var(--border));
          background: hsl(var(--card));
          transition: all 250ms ease;
        }

        .magic-card:hover {
          transform: translateY(-6px);
          box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
        }

        .magic-card::before {
          content: "";
          position: absolute;
          inset: -1px;
          border-radius: inherit;
          padding: 1px;
          background: linear-gradient(
            135deg,
            rgba(99, 102, 241, 0.7),
            rgba(168, 85, 247, 0.4),
            rgba(59, 130, 246, 0.7)
          );

          mask: linear-gradient(#fff 0 0) content-box,
            linear-gradient(#fff 0 0);
          mask-composite: exclude;
          -webkit-mask: linear-gradient(#fff 0 0) content-box,
            linear-gradient(#fff 0 0);
          -webkit-mask-composite: xor;

          opacity: 0;
          transition: opacity 0.3s;
        }

        .magic-card:hover::before {
          opacity: 1;
        }

        .magic-card::after {
          content: "";
          position: absolute;
          width: 250px;
          height: 250px;
          border-radius: 50%;
          left: var(--mouse-x, -100%);
          top: var(--mouse-y, -100%);
          transform: translate(-50%, -50%);
          background: radial-gradient(
            circle,
            rgba(99, 102, 241, 0.18),
            transparent 70%
          );
          pointer-events: none;
          transition: left 120ms, top 120ms;
        }
      `}</style>

      <div
        className={cn("magic-bento-grid", className)}
        onMouseMove={(e) => {
          const cards = document.querySelectorAll(".magic-card");

          cards.forEach((card) => {
            const rect = (card as HTMLElement).getBoundingClientRect();

            (card as HTMLElement).style.setProperty(
              "--mouse-x",
              `${e.clientX - rect.left}px`
            );

            (card as HTMLElement).style.setProperty(
              "--mouse-y",
              `${e.clientY - rect.top}px`
            );
          });
        }}
      >
        {children}
      </div>
    </>
  );
}