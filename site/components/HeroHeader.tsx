export default function HeroHeader({ memoryCount }: { memoryCount: number }) {
  return (
    <header className="hero-header">
      <h1 className="hero-title">
        Happy 70th Birthday, <span className="hero-accent">Katherine</span>!
      </h1>
      <p className="hero-subtitle">
        {memoryCount} memories from the people who love you
      </p>
    </header>
  );
}
