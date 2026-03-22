"use client";

import { useState } from "react";
import ScrollLayout from "./ScrollLayout";
import PagesLayout from "./PagesLayout";

export default function LayoutToggle() {
  const [mode, setMode] = useState<"scroll" | "pages">("scroll");

  return (
    <>
      {/* Toggle bar */}
      <div className="flex justify-center px-4 pt-8">
        <div
          className="inline-flex rounded-lg border p-1"
          style={{
            backgroundColor: "var(--card-bg)",
            borderColor: "var(--border)",
          }}
          role="tablist"
          aria-label="Layout mode"
        >
          <button
            role="tab"
            aria-selected={mode === "scroll"}
            onClick={() => setMode("scroll")}
            className="rounded-md px-4 py-2 text-sm font-medium transition-colors cursor-pointer"
            style={{
              backgroundColor:
                mode === "scroll" ? "var(--border-light)" : "transparent",
              color:
                mode === "scroll"
                  ? "var(--accent-bright)"
                  : "var(--text-secondary)",
            }}
          >
            Scroll
          </button>
          <button
            role="tab"
            aria-selected={mode === "pages"}
            onClick={() => setMode("pages")}
            className="rounded-md px-4 py-2 text-sm font-medium transition-colors cursor-pointer"
            style={{
              backgroundColor:
                mode === "pages" ? "var(--border-light)" : "transparent",
              color:
                mode === "pages"
                  ? "var(--accent-bright)"
                  : "var(--text-secondary)",
            }}
          >
            Pages
          </button>
        </div>
      </div>

      {/* Layout content */}
      {mode === "scroll" ? <ScrollLayout /> : <PagesLayout />}
    </>
  );
}
