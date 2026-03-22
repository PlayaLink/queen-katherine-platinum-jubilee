import type { Memory } from "@/data/memories";
import MemoryCard from "@/components/MemoryCard";

export default function ScrollLayout({ memories }: { memories: Memory[] }) {
  return (
    <div className="scroll-layout">
      {memories.map((memory) => (
        <MemoryCard key={memory.name} memory={memory} />
      ))}
    </div>
  );
}
