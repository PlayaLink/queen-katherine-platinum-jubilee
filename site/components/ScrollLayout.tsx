import type { Memory } from "@/data/memories";
import MemoryCard from "@/components/MemoryCard";

export default function ScrollLayout({ memories }: { memories: Memory[] }) {
  return (
    <div className="scroll-layout">
      {memories.map((memory, i) => (
        <MemoryCard key={memory.name} memory={memory} priority={i < 6} />
      ))}
    </div>
  );
}
