"use client";

import React, { useEffect, useRef } from "react";
import { gsap } from "gsap";

interface AnimatedContentProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  distance?: number;
  direction?: "vertical" | "horizontal";
  reverse?: boolean;
  duration?: number;
  delay?: number;
  animateOpacity?: boolean;
  className?: string;
}

export default function AnimatedContent({
  children,
  distance = 80,
  direction = "vertical",
  reverse = false,
  duration = 0.7,
  delay = 0,
  animateOpacity = true,
  className = "",
  ...props
}: AnimatedContentProps) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;

    if (!el) return;

    // Determine animation axis
    const axis = direction === "horizontal" ? "x" : "y";

    // Determine animation direction
    const offset = reverse ? -distance : distance;

    // Initial state
    gsap.set(el, {
      [axis]: offset,
      opacity: animateOpacity ? 0 : 1,
      willChange: "transform, opacity",
    });

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (!entry.isIntersecting) return;

        // Prevent duplicate animations
        gsap.killTweensOf(el);

        gsap.to(el, {
          [axis]: 0,
          opacity: animateOpacity ? 1 : undefined,
          duration,
          delay,
          ease: "power3.out",
          clearProps: "transform",
          onComplete: () => {
            gsap.set(el, {
              willChange: "auto",
            });
          },
        });

        observer.unobserve(el);
      },
      {
        threshold: 0.15,
      }
    );

    observer.observe(el);

    return () => {
      observer.disconnect();
      gsap.killTweensOf(el);
    };
  }, [
    distance,
    direction,
    reverse,
    duration,
    delay,
    animateOpacity,
  ]);

  return (
    <div ref={ref} className={className} {...props}>
      {children}
    </div>
  );
}