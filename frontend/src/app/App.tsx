import { Link, Route, Routes } from 'react-router-dom';
import { ServiceConnection } from '../components/ServiceConnection';
import { PublicLayout } from '../domains/public/PublicLayout';
import { Home } from '../domains/public/Home';
import { About } from '../domains/public/About';
import { Join } from '../domains/public/Join';
import { Login } from '../domains/identity/Login';
import { MemberLayout } from '../domains/identity/MemberLayout';
import { Dashboard } from '../domains/identity/Dashboard';
import { NewMemberBridge } from '../domains/identity/NewMemberBridge';

export function App() {
  return (
    <Routes>
      <Route element={<MemberLayout />}>
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="new-members" element={<NewMemberBridge />} />
      </Route>
      <Route element={<PublicLayout />}>
        <Route index element={<Home />} />
        <Route path="about" element={<About />} />
        <Route path="join" element={<Join />} />
        <Route path="login" element={<Login />} />
        <Route
          path="connection"
          element={
            <div className="utility-page">
              <p className="eyebrow">Chapter workspace</p>
              <h1>Connection</h1>
              <ServiceConnection />
              <Link to="/">Workspace</Link>
            </div>
          }
        />
        <Route
          path="*"
          element={
            <div className="utility-page">
              <h1>Page not found</h1>
              <p>This workspace page is not available.</p>
              <Link to="/">Return to workspace</Link>
            </div>
          }
        />
      </Route>
    </Routes>
  );
}
