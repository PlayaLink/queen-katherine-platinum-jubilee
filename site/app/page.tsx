import { memories } from "@/data/memories";
import HeroHeader from "@/components/HeroHeader";
import MemoryViewer from "@/components/MemoryViewer";

export default function Home() {
  return (
    <main className="min-h-screen">
      <HeroHeader memoryCount={memories.length} />
      <MemoryViewer memories={memories} />
    </main>
  );
}
