"use client";

import { motion } from "framer-motion";
import { Vortex } from "@/components/ui/vortex";
import { TypewriterEffectSmooth } from "@/components/ui/typewriter-effect"; // Aceternity typewriter component
import { useRouter } from "next/navigation";

export default function LandingPage() {
  const router = useRouter();
  const words = [
    {
      text: "Designed to help teams learn faster, track progress effortlessly, and build skills that matter.",
      // You can add className to style part of the text differently if the Aceternity component supports it
    },
  ];

  return (
    <div className="relative w-full h-screen bg-[#030712] overflow-hidden flex flex-col">
      <div
        className="absolute inset-0"
        style={{
          filter:
            "grayscale(0.5) sepia(1) hue-rotate(180deg) saturate(3.5) brightness(0.9)",
        }}
      >
        <Vortex
          backgroundColor="black"
          baseHue={215}
          particleCount={350}
          baseSpeed={0.05}
          rangeSpeed={0.8}
          baseRadius={1}
          rangeRadius={1.5}
          rangeY={200}
          className="w-full h-full"
        />
      </div>

      <div className="relative z-10 flex items-center justify-between px-10 py-8">
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="text-white/70 text-sm tracking-[0.3em] font-medium"
        >
          Elevate.
        </motion.div>
      </div>

      <div className="relative z-10 flex-1 flex flex-col items-center justify-center px-6 -mt-16">
        {/* <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="mb-6 px-4 py-1.5 rounded-full border border-white/10 bg-white/[0.03] backdrop-blur-sm"
        >
          <span className="text-sm tracking-widest uppercase text-[#2757ff]">
            Empower Every Learner{" "}
          </span>
        </motion.div> */}

        <motion.div
          initial={{ opacity: 0, y: 30, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.5, ease: [0.16, 1, 0.3, 1] }}
          className="text-[10rem] leading-none font-bold text-transparent bg-clip-text bg-gradient-to-b from-white via-white to-white/60 font-quicksand tracking-tight"
        >
          Elevate.
        </motion.div>

        {/* Typewriter area */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.9 }}
          className="mt-6 w-full flex justify-center px-4"
        >
          <TypewriterEffectSmooth
            words={words}
            className="text-sm sm:text-base md:text-lg font-quicksand text-white/50 leading-relaxed"
          />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 1.15 }}
          className="mt-12 flex items-center gap-4"
        >
          <motion.button
            whileHover={{ scale: 1.04, y: -2 }}
            whileTap={{ scale: 0.97 }}
            className="relative px-8 py-3.5 rounded-full font-medium text-white bg-[#4f8fff]/20 border border-[#4f8fff]/40 backdrop-blur-md shadow-[0_0_20px_rgba(79,143,255,0.35)] hover:bg-[#4f8fff]/30 hover:border-[#2757ff]/60 hover:shadow-[0_0_35px_rgba(79,143,255,0.55)] transition-all duration-300"
          >
            <span className="font-quicksand" onClick={() => router.push("/register")}>
              Sign Up
            </span>
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.04, y: -2 }}
            whileTap={{ scale: 0.97 }}
            
            className="relative px-8 py-3.5 rounded-full font-medium text-white/80 bg-white/[0.04] border border-white/15 backdrop-blur-md hover:bg-white/[0.08] hover:text-white hover:border-white/30 transition-all duration-300"
          >
            <span className="font-quicksand" onClick={() => router.push("/login")}>
              Login
            </span>
          </motion.button>
        </motion.div>
      </div>
    </div>
  );
}
