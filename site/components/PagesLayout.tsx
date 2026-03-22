"use client";

import { useState, useEffect, useCallback } from "react";
import type { Memory } from "@/data/memories";
import MemoryCard from "@/components/MemoryCard";

export default function PagesLayout({ memories }: { memories: Memory[] }) {
  const [page, setPage] = useState(0);

  const goPrev = useCallback(
    () => setPage((p) => (p > 0 ? p - 1 : memories.length - 1)),
    [memories.length]
  );

  const goNext = useCallback(
    () => setPage((p) => (p < memories.length - 1 ? p + 1 : 0)),
    [memories.length]
  );

  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "ArrowLeft") goPrev();
      if (e.key === "ArrowRight") goNext();
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [goPrev, goNext]);

  return (
    <div className="pages-layout">
      <MemoryCard memory={memories[page]} />
      <nav className="pages-nav">
        <button onClick={goPrev} aria-label="Previous memory">
          ← Prev
        </button>
        <span style={{ fontVariantNumeric: "tabular-nums" }}>
          {page + 1} of {memories.length}
        </span>
        <button onClick={goNext} aria-label="Next memory">
          Next →
        </button>
      </nav>
    </div>
  );
}
