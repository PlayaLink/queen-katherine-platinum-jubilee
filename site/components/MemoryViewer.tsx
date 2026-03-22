"use client";

import { useState, useEffect, useCallback } from "react";
import type { Memory } from "@/data/memories";
import type { LayoutMode } from "@/components/LayoutToggle";
import ScrollLayout from "@/components/ScrollLayout";
import PagesLayout from "@/components/PagesLayout";
import Controls from "@/components/Controls";

const THEME_KEY = "kb70-theme";
const LAYOUT_KEY = "kb70-layout";
const VALID_THEMES = ["mosaic", "journal", "garden-party", "collage", "gallery"] as const;
export type ThemeName = (typeof VALID_THEMES)[number];

export default function MemoryViewer({ memories }: { memories: Memory[] }) {
  // Start with defaults that match server-rendered HTML to avoid hydration mismatch.
  // The inline script in layout.tsx handles FOUC prevention by setting data-theme
  // before paint. We sync React state from sessionStorage in a mount effect below.
  const [theme, setThemeState] = useState<ThemeName>("mosaic");
  const [mode, setModeState] = useState<LayoutMode>("scroll");
  const [mounted, setMounted] = useState(false);

  // On mount, read persisted values from sessionStorage and sync state.
  useEffect(() => {
    try {
      const storedTheme = sessionStorage.getItem(THEME_KEY);
      if (storedTheme && (VALID_THEMES as readonly string[]).includes(storedTheme)) {
        setThemeState(storedTheme as ThemeName);
        document.documentElement.setAttribute("data-theme", storedTheme);
      }
      const storedLayout = sessionStorage.getItem(LAYOUT_KEY);
      if (storedLayout === "scroll" || storedLayout === "pages") {
        setModeState(storedLayout);
      }
    } catch {}
    setMounted(true);
  }, []);

  const setTheme = useCallback((t: ThemeName) => {
    setThemeState(t);
    document.documentElement.setAttribute("data-theme", t);
    try { sessionStorage.setItem(THEME_KEY, t); } catch {}
  }, []);

  const setMode = useCallback((m: LayoutMode) => {
    setModeState(m);
    try { sessionStorage.setItem(LAYOUT_KEY, m); } catch {}
  }, []);

  return (
    <>
      {mounted && (
        <Controls
          theme={theme}
          onThemeChange={setTheme}
          layout={mode}
          onLayoutChange={setMode}
        />
      )}
      {mode === "scroll" ? (
        <ScrollLayout memories={memories} />
      ) : (
        <PagesLayout memories={memories} />
      )}
    </>
  );
}
