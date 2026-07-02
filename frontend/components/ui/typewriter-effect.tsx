"use client";

import { cn } from "@/lib/utils";
import { motion, stagger, useAnimate, useInView } from "motion/react";
import { useEffect, useMemo, useState } from "react";

export const TypewriterEffect = ({
  words,
  className,
  cursorClassName,
}: {
  words: {
    text: string;
    className?: string;
  }[];
  className?: string;
  cursorClassName?: string;
}) => {
  // split text inside of words into array of characters
  const wordsArray = words.map((word) => {
    return {
      ...word,
      text: word.text.split(""),
    };
  });

  const [scope, animate] = useAnimate();
  const isInView = useInView(scope);
  useEffect(() => {
    if (isInView) {
      animate(
        "span",
        {
          display: "inline-block",
          opacity: 1,
          width: "fit-content",
        },
        {
          duration: 0.3,
          delay: stagger(0.1),
          ease: "easeInOut",
        }
      );
    }
  }, [isInView]);

  const renderWords = () => {
    return (
      <motion.div ref={scope} className="inline">
        {wordsArray.map((word, idx) => {
          return (
            <div key={`word-${idx}`} className="inline-block">
              {word.text.map((char, index) => (
                <motion.span
                  initial={{}}
                  key={`char-${index}`}
                  className={cn(
                    `dark:text-white text-black opacity-0 hidden`,
                    word.className
                  )}
                >
                  {char}
                </motion.span>
              ))}
              &nbsp;
            </div>
          );
        })}
      </motion.div>
    );
  };
  return (
    <div
      className={cn(
        "text-base sm:text-xl md:text-3xl lg:text-5xl font-bold text-center",
        className
      )}
    >
      {renderWords()}
      <motion.span
        initial={{
          opacity: 0,
        }}
        animate={{
          opacity: 1,
        }}
        transition={{
          duration: 0.8,
          repeat: Infinity,
          repeatType: "reverse",
        }}
        className={cn(
          "inline-block rounded-sm w-[4px] h-4 md:h-6 lg:h-10 bg-blue-500",
          cursorClassName
        )}
      ></motion.span>
    </div>
  );
};

export const TypewriterEffectSmooth = ({
  words,
  className,
  cursorClassName,
}: {
  words: {
    text: string;
    className?: string;
  }[];
  className?: string;
  cursorClassName?: string;
}) => {
  const [displayedText, setDisplayedText] = useState("");
  const [isComplete, setIsComplete] = useState(false);

  const fullText = useMemo(() => words.map((word) => word.text).join(" "), [words]);

  useEffect(() => {
    let currentIndex = 0;
    setDisplayedText("");
    setIsComplete(false);

    const interval = window.setInterval(() => {
      currentIndex += 1;
      setDisplayedText(fullText.slice(0, currentIndex));

      if (currentIndex >= fullText.length) {
        setIsComplete(true);
        window.clearInterval(interval);
      }
    }, 35);

    return () => window.clearInterval(interval);
  }, [fullText]);

  return (
    <div
      className={cn(
        "my-6 flex w-full max-w-3xl items-center justify-center px-4 text-center",
        className
      )}
    >
      <div className="inline-flex max-w-full items-center justify-center">
        <span className="whitespace-nowrap text-sm leading-relaxed text-inherit sm:text-base md:text-lg lg:text-xl xl:text-2xl">
          {displayedText}
        </span>
        <motion.span
          animate={{ opacity: isComplete ? 0 : [0, 1, 0] }}
          transition={{ duration: 0.8, repeat: Infinity, repeatType: "reverse" }}
          className={cn(
            "ml-1 inline-block h-4 w-1 rounded-sm bg-blue-500 sm:h-5 md:h-6 lg:h-7",
            cursorClassName
          )}
        />
      </div>
    </div>
  );
};
