import { Link, NavLink, Route, Routes } from 'react-router-dom';
import { ServiceConnection } from '../components/ServiceConnection';
import { chapterSite } from './links';
import { Workspace } from '../pages/Workspace';

export function App() {
  return (
    <>
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <header className="site-header">
        <Link className="brand" to="/" aria-label="Sigma Phi Delta workspace">
          ΣΦΔ <span>Beta Omicron</span>
        </Link>
        <nav aria-label="Workspace navigation">
          <NavLink to="/" end>
            Workspace
          </NavLink>
          <NavLink to="/connection">Connection</NavLink>
          <a href={chapterSite}>Chapter site</a>
        </nav>
      </header>
      <main id="main">
        <Routes>
          <Route index element={<Workspace />} />
          <Route
            path="connection"
            element={
              <>
                <p className="eyebrow">Chapter workspace</p>
                <h1>Connection</h1>
                <ServiceConnection />
              </>
            }
          />
          <Route
            path="*"
            element={
              <>
                <h1>Page not found</h1>
                <p>This workspace page is not available.</p>
                <Link to="/">Return to workspace</Link>
              </>
            }
          />
        </Routes>
      </main>
      <footer>Sigma Phi Delta · Beta Omicron Chapter</footer>
    </>
  );
}
