import { Link } from 'react-router-dom';
import { Arrow } from './Arrow';
import './home.css';
import { useEffect, useState } from 'react';
import { fetchHome, publicAsset, type HomeContent } from './content';

const pillars = [
  {
    number: '01',
    title: 'Develop engineers',
    text: 'Build professional skills, share academic knowledge, and prepare for what comes next.',
  },
  {
    number: '02',
    title: 'Build brotherhood',
    text: 'Find the people who support your ambitions and become lifelong friends.',
  },
  {
    number: '03',
    title: 'Serve community',
    text: 'Give back through local volunteering and our national philanthropy, FIRST.',
  },
];

export function Home() {
  const [content, setContent] = useState<HomeContent | null>(null);
  const [failed, setFailed] = useState(false);
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    const timer = window.setTimeout(() => controller.abort(), 15000);
    setFailed(false);
    fetchHome(controller.signal)
      .then((data) => {
        if (active) setContent(data);
      })
      .catch(() => {
        if (active) setFailed(true);
      })
      .finally(() => window.clearTimeout(timer));
    return () => {
      active = false;
      controller.abort();
      window.clearTimeout(timer);
    };
  }, [attempt]);

  return (
    <>
      <section className="home-hero" aria-labelledby="home-title">
        <img
          className="hero-image"
          src={publicAsset(content?.banner_image ?? '/static/images/charter_class.webp')}
          alt="Sigma Phi Delta chapter members together with the fraternity banner"
          onError={(event) => {
            const fallback = publicAsset('/static/images/charter_class.webp');
            if (!event.currentTarget.src.endsWith(fallback)) event.currentTarget.src = fallback;
          }}
        />
        <div className="hero-shade" />
        <div className="hero-copy">
          <h1 id="home-title">
            Engineering <br />a stronger <br />
            <em>brotherhood.</em>
          </h1>
          <p className="hero-description">
            A community of engineers at Mizzou. Building careers, making an impact, and supporting
            each other for what’s next.
          </p>
          <div className="hero-actions">
            <Link className="button primary" to="/join">
              Join SPD <Arrow />
            </Link>
            <Link className="button outline" to="/about">
              Meet the chapter
            </Link>
          </div>
          <p className="hero-signature">
            SAME PROBLEMS. BRIGHTER PEOPLE.
            <br />A STRONGER TOMORROW.
          </p>
        </div>
        <div className="hero-caption">
          BETA-OMICRON CHAPTER <span>UNIVERSITY OF MISSOURI</span>
        </div>
      </section>
      <section className="purpose-section" id="purpose" aria-labelledby="purpose-title">
        <div className="section-heading">
          <p className="section-marker">SCIENCE. FRIENDSHIP. DUTY.</p>
        </div>
        <h2 id="purpose-title">Engineering. Friendship. Service.</h2>
        <p className="section-intro">
          Sigma Phi Delta is a social and professional engineering fraternity at the University of
          Missouri. We build professional skills, support academic growth, and create lifelong
          friendships.
        </p>
        <div className="pillar-grid">
          {pillars.map((pillar) => (
            <article className="pillar" key={pillar.number}>
              <span className="pillar-number">{pillar.number}</span>
              <h3>{pillar.title}</h3>
              <p>{pillar.text}</p>
            </article>
          ))}
        </div>
      </section>
      <section className="chapter-next" aria-labelledby="next-title">
        <div>
          <h2 id="next-title">
            Good engineers.
            <br />
            Even better together.
          </h2>
          <p>Get to know the chapter, explore recruitment, and see where you belong.</p>
        </div>
        <div className="next-actions">
          <Link className="button primary" to="/join">
            Explore recruitment <Arrow />
          </Link>
          <a href="https://www.instagram.com/sigphimizzou/">
            Follow chapter events on Instagram <Arrow />
          </a>
        </div>
      </section>
      {failed && (
        <section className="content-notice" aria-label="Chapter updates">
          <p role="alert">
            Chapter updates are unavailable. You can still explore recruitment on the chapter site.
          </p>
          <button type="button" onClick={() => setAttempt((value) => value + 1)}>
            Retry chapter updates
          </button>
        </section>
      )}
    </>
  );
}
