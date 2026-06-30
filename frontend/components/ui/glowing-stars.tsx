"use client";

import React, { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { cn } from "@/lib/utils";

export const GlowingStarsBackgroundCard = ({
  className,
  children,
}: {
  className?: string;
  children?: React.ReactNode;
}) => {
  const [mouseEnter, setMouseEnter] = useState(false);

  return (
    <div
      onMouseEnter={() => setMouseEnter(true)}
      onMouseLeave={() => setMouseEnter(false)}
      className={cn(
        `
        group
        relative
        h-full
        w-full
        overflow-hidden
        rounded-2xl
        border
        border-border
        bg-card
        shadow-sm
        transition-all
        duration-300
        hover:-translate-y-1
        hover:border-primary/40
        hover:shadow-[0_0_20px_rgba(39,87,255,0.15)]
        `,
        className
      )}
    >
      <div className="flex justify-center pt-5">
        <Illustration mouseEnter={mouseEnter} />
      </div>

      <div className="px-6 pb-6">
        {children}
      </div>
    </div>
  );
};

export const GlowingStarsTitle = ({
  className,
  children,
}: {
  className?: string;
  children?: React.ReactNode;
}) => {
  return (
    <h2
      className={cn(
        `
        text-2xl
        font-bold
        text-foreground
        transition-colors
        duration-300
        group-hover:text-primary
        `,
        className
      )}
    >
      {children}
    </h2>
  );
};

export const GlowingStarsDescription = ({
  className,
  children,
}: {
  className?: string;
  children?: React.ReactNode;
}) => {
  return (
    <p
      className={cn(
        `
        mt-3
        text-sm
        leading-6
        text-muted-foreground
        `,
        className
      )}
    >
      {children}
    </p>
  );
};

export const Illustration = ({
  mouseEnter,
}: {
  mouseEnter: boolean;
}) => {
  const stars = 108;
  const columns = 18;

  const [glowingStars, setGlowingStars] = useState<number[]>([]);

  const highlightedStars = useRef<number[]>([]);

  useEffect(() => {
    const interval = setInterval(() => {
      highlightedStars.current = Array.from({ length: 5 }, () =>
        Math.floor(Math.random() * stars)
      );

      setGlowingStars([...highlightedStars.current]);
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div
      className="h-40 w-full p-2"
      style={{
        display: "grid",
        gridTemplateColumns: `repeat(${columns},1fr)`,
        gap: "2px",
      }}
    >
      {[...Array(stars)].map((_, starIdx) => {
        const isGlowing = glowingStars.includes(starIdx);

        const delay = (starIdx % 10) * 0.1;

        const staticDelay = starIdx * 0.01;

        return (
          <div
            key={starIdx}
            className="relative flex items-center justify-center"
          >
            <Star
              isGlowing={mouseEnter ? true : isGlowing}
              delay={mouseEnter ? staticDelay : delay}
            />

            {mouseEnter && <Glow delay={staticDelay} />}

            <AnimatePresence mode="wait">
              {isGlowing && <Glow delay={delay} />}
            </AnimatePresence>
          </div>
        );
      })}
    </div>
  );
};

const Star = ({
  isGlowing,
  delay,
}: {
  isGlowing: boolean;
  delay: number;
}) => {
  return (
    <motion.div
      initial={{ scale: 1 }}
      animate={{
        scale: isGlowing ? [1, 1.5, 2.2, 1.5, 1] : 1,

        backgroundColor: isGlowing
          ? "#2757ff"
          : "rgba(255,255,255,0.25)",
      }}
      transition={{
        duration: 2,
        ease: "easeInOut",
        delay,
      }}
      className="relative z-20 h-[2px] w-[2px] rounded-full"
    />
  );
};

const Glow = ({
  delay,
}: {
  delay: number;
}) => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{
        duration: 2,
        ease: "easeInOut",
        delay,
      }}
      className="
      absolute
      left-1/2
      -translate-x-1/2
      z-10
      h-[6px]
      w-[6px]
      rounded-full
      bg-primary
      blur-[2px]
      shadow-[0_0_12px_3px_rgba(39,87,255,0.45)]
      "
    />
  );
};