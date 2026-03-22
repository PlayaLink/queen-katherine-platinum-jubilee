import { memories } from "@/data/memories";
import HeroHeader from "@/components/HeroHeader";
import ScrollLayout from "@/components/ScrollLayout";

export default function Home() {
  return (
    <main className="min-h-screen">
      <HeroHeader memoryCount={memories.length} />
      <ScrollLayout memories={memories} />
    </main>
  );
}
