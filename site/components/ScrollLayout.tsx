"use client";

import { useState, useEffect } from "react";
import type { Memory } from "@/data/memories";
import MemoryCard from "@/components/MemoryCard";

function sortByQuoteLength(memories: Memory[]): Memory[] {
  return [...memories].sort((a, b) => a.quote.length - b.quote.length);
}

function useColumns() {
  const [cols, setCols] = useState(1);
  useEffect(() => {
    function update() {
      if (window.innerWidth >= 1024) setCols(3);
      else if (window.innerWidth >= 640) setCols(2);
      else setCols(1);
    }
    update();
    window.addEventListener("resize", update);
    return () => window.removeEventListener("resize", update);
  }, []);
  return cols;
}

export default function ScrollLayout({ memories }: { memories: Memory[] }) {
  const cols = useColumns();
  const sorted = cols > 1 ? sortByQuoteLength(memories) : memories;

  return (
    <div className="scroll-layout">
      {sorted.map((memory, i) => (
        <MemoryCard key={memory.name} memory={memory} priority={i < 6} />
      ))}
    </div>
  );
}
