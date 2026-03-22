"use client";

import { useState } from "react";
import type { Memory } from "@/data/memories";
import MemoryCard from "@/components/MemoryCard";

export default function PagesLayout({ memories }: { memories: Memory[] }) {
  const [page, setPage] = useState(0);

  return (
    <div className="pages-layout">
      <MemoryCard memory={memories[page]} />
      <nav className="pages-nav">
        <button
          onClick={() => setPage((p) => p - 1)}
          disabled={page === 0}
          aria-label="Previous memory"
        >
          ← Prev
        </button>
        <span>
          {page + 1} / {memories.length}
        </span>
        <button
          onClick={() => setPage((p) => p + 1)}
          disabled={page === memories.length - 1}
          aria-label="Next memory"
        >
          Next →
        </button>
      </nav>
    </div>
  );
}
