"use client";

export type LayoutMode = "scroll" | "pages";

export default function LayoutToggle({
  mode,
  onChange,
}: {
  mode: LayoutMode;
  onChange: (mode: LayoutMode) => void;
}) {
  return (
    <div className="layout-toggle" role="tablist" aria-label="Layout mode">
      <button
        role="tab"
        aria-selected={mode === "scroll"}
        className={mode === "scroll" ? "active" : ""}
        onClick={() => onChange("scroll")}
      >
        Scroll
      </button>
      <button
        role="tab"
        aria-selected={mode === "pages"}
        className={mode === "pages" ? "active" : ""}
        onClick={() => onChange("pages")}
      >
        Pages
      </button>
    </div>
  );
}
