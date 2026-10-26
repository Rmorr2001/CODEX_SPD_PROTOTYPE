import { Link, Route, Routes } from 'react-router-dom';
import { ServiceConnection } from '../components/ServiceConnection';
import { PublicLayout } from '../domains/public/PublicLayout';
import { Home } from '../domains/public/Home';
import { About } from '../domains/public/About';
import { Join } from '../domains/public/Join';
import { Login } from '../domains/identity/Login';
import { MemberLayout } from '../domains/identity/MemberLayout';
import { Dashboard } from '../domains/identity/Dashboard';
import { Directory } from '../domains/identity/Directory';
import { Profile } from '../domains/identity/Profile';
import { PollDetail } from '../domains/decisions/PollDetail';
import { Decisions } from '../domains/decisions/Decisions';
import { ServiceForm } from '../domains/service/ServiceForm';
import { ServiceReview } from '../domains/service/ServiceReview';
import { ServiceChapter, ServiceHistory } from '../domains/service/ServiceReports';
import { ServiceHours } from '../domains/service/ServiceHours';
import { MarkForm } from '../domains/new-members/MarkForm';
import { MarkReview } from '../domains/new-members/MarkReview';
import { MarkHistory } from '../domains/new-members/MarkHistory';
import { MarkExport } from '../domains/new-members/MarkExport';
import { NewMemberMarks } from '../domains/new-members/NewMemberMarks';

export function App() {
  return (
    <Routes>
      <Route element={<MemberLayout />}>
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="members" element={<Directory />} />
        <Route path="profile" element={<Profile />} />
        <Route path="polls" element={<Decisions />} />
        <Route path="polls/:id" element={<PollDetail />} />
        <Route path="service" element={<ServiceHours />} />
        <Route path="service/new" element={<ServiceForm />} />
        <Route path="service/review" element={<ServiceReview />} />
        <Route path="service/history" element={<ServiceHistory />} />
        <Route path="service/history/:userId" element={<ServiceHistory />} />
        <Route path="service/chapter" element={<ServiceChapter />} />
        <Route path="service/events/:id/edit" element={<ServiceForm />} />
        <Route path="new-members" element={<NewMemberMarks />} />
        <Route path="new-members/new" element={<MarkForm />} />
        <Route path="new-members/review" element={<MarkReview />} />
        <Route path="new-members/history/:userId" element={<MarkHistory />} />
        <Route path="new-members/marks/:id/edit" element={<MarkForm />} />
        <Route path="new-members/export" element={<MarkExport />} />
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
