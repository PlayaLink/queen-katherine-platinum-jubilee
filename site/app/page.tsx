import { memories } from "@/data/memories";
import MemoryCard from "@/components/MemoryCard";

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-50 px-4 py-12">
      <h1 className="mb-2 text-center text-4xl font-bold text-gray-900">
        Happy 70th Birthday, Katherine!
      </h1>
      <p className="mb-10 text-center text-lg text-gray-600">
        {memories.length} memories from the people who love you
      </p>
      <div className="mx-auto grid max-w-6xl gap-8 sm:grid-cols-2 lg:grid-cols-3">
        {memories.map((memory) => (
          <MemoryCard key={memory.name} memory={memory} />
        ))}
      </div>
    </main>
  );
}
