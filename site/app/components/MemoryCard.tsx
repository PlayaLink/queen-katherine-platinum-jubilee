import Image from "next/image";
import type { Memory } from "../data/memories";

export default function MemoryCard({ memory }: { memory: Memory }) {
  const hasQuote = memory.quote.length > 0;

  return (
    <article
      className="overflow-hidden rounded-xl border transition-colors"
      style={{
        backgroundColor: "var(--card-bg)",
        borderColor: "var(--border)",
      }}
    >
      {/* Photo */}
      <div className="relative aspect-[4/3] w-full">
        {memory.photo ? (
          <Image
            src={memory.photo}
            alt={`Photo from ${memory.name}`}
            fill
            className="object-cover"
            sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 600px"
          />
        ) : (
          <div className="photo-placeholder h-full w-full" />
        )}
      </div>

      {/* Quote + Attribution */}
      <div className="p-5 sm:p-6">
        {hasQuote && (
          <blockquote
            className="mb-4 text-sm leading-relaxed whitespace-pre-line sm:text-base"
            style={{ color: "var(--text)" }}
          >
            <span
              className="mr-1 text-lg"
              style={{ color: "var(--accent)" }}
              aria-hidden="true"
            >
              &ldquo;
            </span>
            {memory.quote}
            <span
              className="ml-1 text-lg"
              style={{ color: "var(--accent)" }}
              aria-hidden="true"
            >
              &rdquo;
            </span>
          </blockquote>
        )}
        <p
          className="text-sm font-medium tracking-wide"
          style={{ color: "var(--accent-bright)" }}
        >
          &mdash; {memory.name}
        </p>
      </div>
    </article>
  );
}
