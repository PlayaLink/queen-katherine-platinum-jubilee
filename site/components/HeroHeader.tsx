export default function HeroHeader({ memoryCount }: { memoryCount: number }) {
  return (
    <header className="hero-header">
      <p className="hero-crown" aria-hidden="true">♛</p>
      <h1 className="hero-title">
        The Platinum Jubilee of{" "}
        <span className="hero-accent">Queen Katherine</span>
      </h1>
      <p className="hero-subtitle">
        Words of Tribute from Her Royal Subjects
      </p>
    </header>
  );
}
