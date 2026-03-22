import Image from "next/image";
import type { Memory } from "@/data/memories";

export default function MemoryCard({
  memory,
  priority = false,
}: {
  memory: Memory;
  priority?: boolean;
}) {
  const initial = memory.name.charAt(0).toUpperCase();

  return (
    <div className="memory-card">
      {memory.photo ? (
        <div className="card-image-wrapper">
          <Image
            src={`/photos/${memory.photo}`}
            alt={`Photo from ${memory.name}`}
            fill
            className="object-cover"
            sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
            quality={75}
            priority={priority}
          />
        </div>
      ) : (
        <div className="card-decorative-bg" aria-hidden="true">
          <span className="decorative-initial">{initial}</span>
        </div>
      )}
      <blockquote className="card-quote">
        &ldquo;{memory.quote}&rdquo;
      </blockquote>
      <p className="card-attribution">— {memory.name}</p>
    </div>
  );
}
