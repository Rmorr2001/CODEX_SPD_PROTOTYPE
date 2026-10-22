import { useEffect, useState } from 'react';
import { chapterSite } from '../../app/links';
import { Arrow } from './Arrow';
import { fetchAbout, type AboutContent, type Executive } from './aboutContent';
import { publicAsset } from './content';
import './about.css';

function ExecutiveCard({ member }: { member: Executive }) {
  const [broken, setBroken] = useState(false);
  return (
    <article className="executive-card">
      {member.image && !broken ? (
        <img
          src={publicAsset(member.image)}
          alt={`${member.name}, ${member.position}`}
          onError={() => setBroken(true)}
        />
      ) : (
        <div className="executive-placeholder" aria-hidden="true">
          {member.name
            .split(' ')
            .map((part) => part[0])
            .slice(0, 2)
            .join('')}
        </div>
      )}
      <h3>{member.name}</h3>
      <p>{member.position}</p>
    </article>
  );
}

function Leadership({
  content,
  failed,
  retry,
}: {
  content: AboutContent | null;
  failed: boolean;
  retry: () => void;
}) {
  return (
    <section id="leadership" className="about-leadership" aria-labelledby="leadership-title">
      <div className="about-section-top">
        <div>
          <p className="eyebrow">CHAPTER LEADERSHIP</p>
          <h2 id="leadership-title">A team that builds a stronger chapter.</h2>
        </div>
        <a href={`${chapterSite}executive-board/`}>
          Original executive board <Arrow />
        </a>
      </div>
      {!content && !failed && <p role="status">Loading chapter leadership…</p>}
      {failed && (
        <div className="inline-notice">
          <p role="alert">Chapter leadership is unavailable right now.</p>
          <button onClick={retry}>Try again</button>
        </div>
      )}
      {content && (
        <>
          <p className="chapter-count">
            <strong>{content.active_count}</strong> active members in the chapter directory
          </p>
          {content.executives.length ? (
            <div className="executive-grid">
              {content.executives.map((member, index) => (
                <ExecutiveCard member={member} key={`${member.position}-${index}`} />
              ))}
            </div>
          ) : (
            <p className="inline-notice">Chapter leadership has not been published yet.</p>
          )}
        </>
      )}
    </section>
  );
}

export function About() {
  const [content, setContent] = useState<AboutContent | null>(null);
  const [failed, setFailed] = useState(false);
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let active = true;
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 15000);
    setFailed(false);
    fetchAbout(controller.signal)
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
    <div className="about-page">
      <section className="about-intro" aria-labelledby="about-title">
        <div>
          <p className="eyebrow">ABOUT OUR CHAPTER</p>
          <h1 id="about-title">Built together.</h1>
          <p>
            The Beta-Omicron chapter of Sigma Phi Delta brings engineers together at Mizzou. We
            challenge ourselves, support one another, and put science, friendship, and duty into
            practice.
          </p>
        </div>
        <blockquote>
          Better people.
          <br />
          Stronger engineers.
          <br />A stronger community.
        </blockquote>
      </section>
      <figure className="about-photo">
        <img
          src={publicAsset('/static/images/charter_class.webp')}
          alt="The Beta-Omicron charter class with their Sigma Phi Delta banner"
        />
        <figcaption>FROM THE CHAPTER ARCHIVE · BETA-OMICRON CHARTER CLASS</figcaption>
      </figure>
      <section className="about-story" aria-labelledby="story-title">
        <div>
          <p className="eyebrow">OUR BROTHERHOOD</p>
          <h2 id="story-title">
            Different paths.
            <br />A shared purpose.
          </h2>
          <p>
            Founded at the University of Missouri on December 13, 2014, our chapter grew from a
            colony of students who wanted to better themselves and the engineering profession.
          </p>
          <p>
            Our code of ethics begins with truth and honesty. Those principles guide how we work,
            support each other, and serve our community.
          </p>
          <div className="story-links">
            <a href={`${chapterSite}ourHistory/`}>
              Read our full history <Arrow />
            </a>
            <a href={`${chapterSite}codeOfEthics/`}>
              Our code of ethics <Arrow />
            </a>
          </div>
        </div>
        <div className="about-values">
          <article>
            <span>01</span>
            <div>
              <h3>Professional growth</h3>
              <p>Share knowledge, strengthen skills, and learn from the people around you.</p>
            </div>
          </article>
          <article>
            <span>02</span>
            <div>
              <h3>Lifelong friendship</h3>
              <p>Build relationships that extend beyond the classroom and the chapter.</p>
            </div>
          </article>
          <article>
            <span>03</span>
            <div>
              <h3>Meaningful service</h3>
              <p>Put engineering values to work for the wider community.</p>
            </div>
          </article>
        </div>
      </section>
      <Leadership
        content={content}
        failed={failed}
        retry={() => setAttempt((value) => value + 1)}
      />
      <section className="about-recruitment">
        <div>
          <p className="eyebrow">YOUR PLACE IN THE CHAPTER</p>
          <h2>Build what comes next.</h2>
          <p>Start by getting to know us.</p>
        </div>
        <a className="button primary" href={`${chapterSite}rush/`}>
          Explore recruitment <Arrow />
        </a>
      </section>
    </div>
  );
}
