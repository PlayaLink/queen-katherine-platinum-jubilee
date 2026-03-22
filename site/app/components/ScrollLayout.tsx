import { memories } from "../data/memories";
import MemoryCard from "./MemoryCard";

export default function ScrollLayout() {
  return (
    <div className="mx-auto max-w-2xl space-y-8 px-4 py-8 sm:py-12">
      {memories.map((memory, i) => (
        <MemoryCard key={i} memory={memory} />
      ))}
    </div>
  );
}
