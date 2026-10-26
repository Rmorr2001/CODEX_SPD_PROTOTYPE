import { Arrow } from './Arrow';
import './public.css';
import { useEffect } from 'react';
import { Link, NavLink, Outlet, useLocation } from 'react-router-dom';
import { chapterSite } from '../../app/links';

export function PublicLayout() {
  const { pathname, hash } = useLocation();
  useEffect(() => {
    // React renders hash targets after browser navigation; scroll once the outlet exists.
    if (hash) document.getElementById(hash.slice(1))?.scrollIntoView();
    else window.scrollTo(0, 0);
  }, [pathname, hash]);
  return (
    <>
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <header className="public-header">
        <Link className="brand" to="/" aria-label="Sigma Phi Delta home">
          <span className="brand-symbol">ΣΦΔ</span>
          <span className="brand-chapter">
            BETA-OMICRON <small>UNIVERSITY OF MISSOURI</small>
          </span>
        </Link>
        <nav aria-label="Public navigation">
          <NavLink to="/about">About</NavLink>
          <Link to="/about#leadership">Brotherhood</Link>
          <Link to="/#purpose">Our purpose</Link>
          <NavLink to="/join">Join SPD</NavLink>
          <Link className="member-login" to="/login">
            Member login <Arrow />
          </Link>
        </nav>
      </header>
      <main id="main" className="public-main">
        <Outlet />
      </main>
      <footer className="public-footer">
        <Link className="footer-brand" to="/">
          ΣΦΔ
        </Link>
        <div>
          <strong>Sigma Phi Delta</strong>
          <p>Beta-Omicron Chapter · University of Missouri, Columbia</p>
        </div>
        <nav aria-label="Footer navigation">
          <a href={`${chapterSite}legacy/`}>Django HTML/CSS</a>
          <NavLink to="/connection">Connection</NavLink>
        </nav>
      </footer>
    </>
  );
}
