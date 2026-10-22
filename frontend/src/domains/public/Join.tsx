import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { chapterSite } from '../../app/links';
import { Arrow } from './Arrow';
import { publicAsset } from './content';
import {
  fetchRecruitment,
  type RecruitmentContent,
  type RecruitmentSlide,
} from './recruitmentContent';
import './join.css';

const expectations = [
  {
    number: '01',
    title: 'Meet the chapter',
    text: 'Get to know the people behind the letters, and find common ground beyond your classes.',
  },
  {
    number: '02',
    title: 'Grow as an engineer',
    text: 'Explore the professional, academic, and social sides of our engineering brotherhood.',
  },
  {
    number: '03',
    title: 'Make a difference',
    text: 'Learn how the chapter gives back through volunteering and our national philanthropy, FIRST.',
  },
];

function RecruitmentImage({ slide }: { slide: RecruitmentSlide }) {
  const [broken, setBroken] = useState(false);
  return (
    <figure className="recruitment-slide">
      {slide.image && !broken ? (
        <img
          src={publicAsset(slide.image)}
          alt={slide.caption || 'Chapter recruitment photograph'}
          onError={() => setBroken(true)}
        />
      ) : (
        <div className="slide-placeholder">Chapter image unavailable</div>
      )}
      <figcaption>{slide.caption || 'A look at chapter life'}</figcaption>
    </figure>
  );
}

export function Join() {
  const [content, setContent] = useState<RecruitmentContent | null>(null);
  const [failed, setFailed] = useState(false);
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let active = true;
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 15000);
    setFailed(false);
    fetchRecruitment(controller.signal)
      .then((data) => {
        if (active) setContent(data);
      })
      .catch(() => {
        if (active) setFailed(true);
      })
      .finally(() => window.clearTimeout(timeout));
    return () => {
      active = false;
      controller.abort();
      window.clearTimeout(timeout);
    };
  }, [attempt]);
  return (
    <>
      <section className="join-hero" aria-labelledby="join-title">
        <img
          src={publicAsset('/static/images/colony_members.webp')}
          alt="Sigma Phi Delta colony members together with their fraternity banner"
        />
        <div className="join-shade" />
        <div className="join-hero-copy">
          <p className="eyebrow">JOIN SIGMA PHI DELTA</p>
          <h1 id="join-title">
            Find your people.
            <br />
            Build your future.
          </h1>
          <p>
            Engineering is hard. Don’t go through it alone. Find a brotherhood that supports your
            ambitions, your studies, and your life beyond the classroom.
          </p>
          <a className="button primary" href={content?.interest_url ?? `${chapterSite}rush/`}>
            {content?.interest_url ? 'Explore recruitment' : 'View original recruitment page'}
            <Arrow />
          </a>
        </div>
      </section>
      <div className="join-content">
        <section className="recruitment-guidance" aria-labelledby="guidance-title">
          <div>
            <p className="eyebrow">YOUR NEXT STEP</p>
            <h2 id="guidance-title">Start with a conversation.</h2>
            <p>
              Explore recruitment details and find out how to connect with the chapter. Get to know
              Sigma Phi Delta at Mizzou and let us know you’re interested.
            </p>
          </div>
          <aside>
            <h3>Looking for dates and details?</h3>
            <p>
              Check the original recruitment page and chapter Instagram for current information.
            </p>
            <a href={`${chapterSite}rush/`}>
              Recruitment details <Arrow />
            </a>
            <a href="https://www.instagram.com/sigphimizzou/">
              Chapter Instagram <Arrow />
            </a>
          </aside>
        </section>
        <section className="expect-section" aria-labelledby="expect-title">
          <p className="eyebrow">WHAT TO EXPECT</p>
          <h2 id="expect-title">More than a major in common.</h2>
          <div className="expect-grid">
            {expectations.map((item) => (
              <article key={item.number}>
                <span>{item.number}</span>
                <h3>{item.title}</h3>
                <p>{item.text}</p>
              </article>
            ))}
          </div>
        </section>
        <section className="chapter-life" aria-labelledby="life-title">
          <div className="life-heading">
            <div>
              <p className="eyebrow">A LOOK INSIDE</p>
              <h2 id="life-title">Chapter life.</h2>
            </div>
            <Link to="/about">
              Meet the chapter <Arrow />
            </Link>
          </div>
          {!content && !failed && <p role="status">Loading recruitment photos…</p>}
          {failed && (
            <div className="inline-notice">
              <p role="alert">Recruitment updates are unavailable right now.</p>
              <button type="button" onClick={() => setAttempt((value) => value + 1)}>
                Try again
              </button>
            </div>
          )}
          {content &&
            (content.slides.length ? (
              <div className="recruitment-gallery">
                {content.slides.map((slide, index) => (
                  <RecruitmentImage slide={slide} key={`${slide.caption}-${index}`} />
                ))}
              </div>
            ) : (
              <p className="inline-notice">
                Recruitment photos have not been published yet. Explore the chapter’s history while
                you wait.
              </p>
            ))}
          {content && !content.interest_url && (
            <p className="interest-unavailable">
              An interest link has not been published. The original recruitment page remains
              available above.
            </p>
          )}
        </section>
        <section className="join-bottom">
          <p className="eyebrow">ENGINEERING. FRIENDSHIP. SERVICE.</p>
          <h2>
            Same problems.
            <br />
            <em>Brighter people.</em>
          </h2>
          <Link to="/about">
            Get to know Sigma Phi Delta <Arrow />
          </Link>
        </section>
      </div>
    </>
  );
}
