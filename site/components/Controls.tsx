"use client";

import { useState } from "react";
import type { ThemeName } from "@/components/MemoryViewer";
import type { LayoutMode } from "@/components/LayoutToggle";

const THEMES: { slug: ThemeName; label: string; swatch: string }[] = [
  { slug: "mosaic", label: "Mosaic", swatch: "#2d1b4e" },
  { slug: "journal", label: "Journal", swatch: "#ede4d3" },
  { slug: "garden-party", label: "Garden", swatch: "#e8f0e5" },
  { slug: "collage", label: "Collage", swatch: "#1a1a1a" },
  { slug: "gallery", label: "Gallery", swatch: "#ffffff" },
];

export default function Controls({
  theme,
  onThemeChange,
  layout,
  onLayoutChange,
}: {
  theme: ThemeName;
  onThemeChange: (t: ThemeName) => void;
  layout: LayoutMode;
  onLayoutChange: (m: LayoutMode) => void;
}) {
  const [open, setOpen] = useState(false);

  return (
    <div className={`controls-panel ${open ? "controls-open" : ""}`}>
      <button
        className="controls-toggle"
        onClick={() => setOpen(!open)}
        aria-label={open ? "Close controls" : "Open controls"}
        aria-expanded={open}
      >
        {open ? "✕" : "⚙"}
      </button>

      {open && (
        <div className="controls-body">
          {/* Theme switcher */}
          <fieldset className="controls-section">
            <legend className="controls-label">Theme</legend>
            <div className="controls-themes">
              {THEMES.map((t) => (
                <button
                  key={t.slug}
                  className={`controls-swatch ${theme === t.slug ? "controls-swatch-active" : ""}`}
                  onClick={() => onThemeChange(t.slug)}
                  aria-label={`${t.label} theme`}
                  aria-pressed={theme === t.slug}
                  title={t.label}
                >
                  <span
                    className="controls-swatch-color"
                    style={{ backgroundColor: t.swatch }}
                  />
                  <span className="controls-swatch-label">{t.label}</span>
                </button>
              ))}
            </div>
          </fieldset>

          {/* Layout toggle */}
          <fieldset className="controls-section">
            <legend className="controls-label">Layout</legend>
            <div className="controls-layout-btns" role="tablist" aria-label="Layout mode">
              <button
                role="tab"
                aria-selected={layout === "scroll"}
                className={layout === "scroll" ? "active" : ""}
                onClick={() => onLayoutChange("scroll")}
              >
                Scroll
              </button>
              <button
                role="tab"
                aria-selected={layout === "pages"}
                className={layout === "pages" ? "active" : ""}
                onClick={() => onLayoutChange("pages")}
              >
                Pages
              </button>
            </div>
          </fieldset>
        </div>
      )}
    </div>
  );
}
