"use client";

import { useCallback, useEffect, useState } from "react";
import { memories } from "../data/memories";
import MemoryCard from "./MemoryCard";

export default function PagesLayout() {
  const [index, setIndex] = useState(0);
  const total = memories.length;

  const prev = useCallback(
    () => setIndex((i) => (i > 0 ? i - 1 : total - 1)),
    [total],
  );
  const next = useCallback(
    () => setIndex((i) => (i < total - 1 ? i + 1 : 0)),
    [total],
  );

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "ArrowLeft") prev();
      if (e.key === "ArrowRight") next();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [prev, next]);

  return (
    <div className="mx-auto max-w-2xl px-4 py-8 sm:py-12">
      {/* Position indicator */}
      <p
        className="mb-6 text-center text-sm tabular-nums"
        style={{ color: "var(--text-secondary)" }}
      >
        {index + 1} of {total}
      </p>

      {/* Current memory */}
      <MemoryCard memory={memories[index]} />

      {/* Navigation controls */}
      <div className="mt-6 flex items-center justify-between gap-4">
        <button
          onClick={prev}
          className="flex h-10 items-center gap-2 rounded-lg border px-4 text-sm transition-colors hover:brightness-125 cursor-pointer"
          style={{
            backgroundColor: "var(--card-bg)",
            borderColor: "var(--border)",
            color: "var(--text)",
          }}
          aria-label="Previous memory"
        >
          <span aria-hidden="true">&larr;</span>
          <span className="hidden sm:inline">Prev</span>
        </button>

        {/* Dot indicators (small screens show subset) */}
        <div
          className="flex flex-wrap justify-center gap-1.5"
          aria-hidden="true"
        >
          {memories.map((_, i) => (
            <button
              key={i}
              onClick={() => setIndex(i)}
              className="h-2 w-2 rounded-full transition-all cursor-pointer"
              style={{
                backgroundColor:
                  i === index ? "var(--accent-bright)" : "var(--border)",
                transform: i === index ? "scale(1.3)" : "scale(1)",
              }}
              aria-label={`Go to memory ${i + 1}`}
            />
          ))}
        </div>

        <button
          onClick={next}
          className="flex h-10 items-center gap-2 rounded-lg border px-4 text-sm transition-colors hover:brightness-125 cursor-pointer"
          style={{
            backgroundColor: "var(--card-bg)",
            borderColor: "var(--border)",
            color: "var(--text)",
          }}
          aria-label="Next memory"
        >
          <span className="hidden sm:inline">Next</span>
          <span aria-hidden="true">&rarr;</span>
        </button>
      </div>

      {/* Keyboard hint */}
      <p
        className="mt-4 hidden text-center text-xs sm:block"
        style={{ color: "var(--text-secondary)", opacity: 0.5 }}
      >
        Use &larr; &rarr; arrow keys to navigate
      </p>
    </div>
  );
}
