"use client";

import { useState } from "react";
import type { Memory } from "@/data/memories";
import LayoutToggle, { type LayoutMode } from "@/components/LayoutToggle";
import ScrollLayout from "@/components/ScrollLayout";
import PagesLayout from "@/components/PagesLayout";

export default function MemoryViewer({ memories }: { memories: Memory[] }) {
  const [mode, setMode] = useState<LayoutMode>("scroll");

  return (
    <>
      <LayoutToggle mode={mode} onChange={setMode} />
      {mode === "scroll" ? (
        <ScrollLayout memories={memories} />
      ) : (
        <PagesLayout memories={memories} />
      )}
    </>
  );
}
