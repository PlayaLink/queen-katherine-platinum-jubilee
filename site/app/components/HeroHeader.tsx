export default function HeroHeader() {
  return (
    <header
      className="relative overflow-hidden py-16 px-4 text-center sm:py-24"
      style={{
        background: `linear-gradient(180deg, var(--hero-gradient-start), var(--hero-gradient-end))`,
      }}
    >
      {/* Decorative sparkles */}
      <div className="pointer-events-none absolute inset-0" aria-hidden="true">
        {[
          { top: "12%", left: "8%", delay: "0s", size: "1.2rem" },
          { top: "18%", right: "12%", delay: "1.5s", size: "0.9rem" },
          { top: "60%", left: "15%", delay: "0.8s", size: "0.7rem" },
          { top: "45%", right: "8%", delay: "2.2s", size: "1rem" },
          { top: "75%", left: "25%", delay: "1.2s", size: "0.8rem" },
          { top: "30%", right: "22%", delay: "0.4s", size: "0.6rem" },
        ].map((star, i) => (
          <span
            key={i}
            className="absolute animate-pulse"
            style={{
              top: star.top,
              left: star.left,
              right: star.right,
              animationDelay: star.delay,
              fontSize: star.size,
              color: "var(--accent)",
              opacity: 0.5,
            }}
          >
            &#10022;
          </span>
        ))}
      </div>

      {/* Top ornament */}
      <div
        className="mx-auto mb-6 max-w-xs text-sm tracking-[0.3em] uppercase sm:max-w-sm"
        style={{ color: "var(--accent)" }}
      >
        <div className="ornament">&#10022;</div>
      </div>

      {/* Title */}
      <h1
        className="mx-auto max-w-3xl text-3xl font-light tracking-wide sm:text-5xl lg:text-6xl"
        style={{ color: "var(--text)" }}
      >
        The Platinum Jubilee of
        <br />
        <span
          className="mt-2 block font-serif text-4xl font-normal italic sm:text-6xl lg:text-7xl"
          style={{ color: "var(--accent-bright)" }}
        >
          Queen Katherine
        </span>
      </h1>

      {/* Subtitle */}
      <p
        className="mx-auto mt-6 max-w-xl text-base font-light tracking-wide sm:text-lg"
        style={{ color: "var(--text-secondary)" }}
      >
        Seventy years of boldness, creativity, and love &mdash; celebrated by
        those whose lives she has changed forever.
      </p>

      {/* Bottom ornament */}
      <div
        className="mx-auto mt-8 max-w-xs sm:max-w-sm"
        style={{ color: "var(--accent)" }}
      >
        <div className="ornament">&#10022;</div>
      </div>

      {/* Decorative bottom fade */}
      <div
        className="pointer-events-none absolute bottom-0 left-0 right-0 h-16"
        style={{
          background: `linear-gradient(transparent, var(--bg))`,
        }}
      />
    </header>
  );
}
