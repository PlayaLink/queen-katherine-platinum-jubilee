import Image from "next/image";
import type { Memory } from "@/data/memories";

export default function MemoryCard({ memory }: { memory: Memory }) {
  return (
    <div className="max-w-md rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      {memory.photo && (
        <div className="relative mb-4 aspect-square w-full overflow-hidden rounded-md">
          <Image
            src={`/photos/${memory.photo}`}
            alt={`Photo from ${memory.name}`}
            fill
            className="object-cover"
            sizes="(max-width: 448px) 100vw, 448px"
          />
        </div>
      )}
      <blockquote className="mb-3 text-gray-700 italic whitespace-pre-line">
        &ldquo;{memory.quote}&rdquo;
      </blockquote>
      <p className="text-right font-semibold text-gray-900">
        — {memory.name}
      </p>
    </div>
  );
}
