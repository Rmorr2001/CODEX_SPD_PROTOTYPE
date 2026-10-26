import { Link, NavLink, Outlet, useOutletContext, useLocation } from 'react-router-dom';
import { chapterSite } from '../../app/links';
import { SignOut } from './SignOut';
import { AccessPanel } from './Login';
import { type Member, useSession } from './session';
import { MemberShell } from '@/components/ui/member-shell';
import { cn } from '@/lib/utils';
import { ServiceQuickEntry } from '../service/ServiceQuickEntry';
import './member.css';

export function useMember(): Member {
  return useOutletContext<Member>();
}
const iconPaths: Record<string, string> = {
  Overview: 'M3 3h7v7H3z M14 3h7v7h-7z M3 14h7v7H3z M14 14h7v7h-7z',
  Polls: 'M5 20V12 M12 20V4 M19 20V8',
  Service: 'M4 12h4l3-7 3 14 3-7h3',
  Members:
    'M16 21v-3a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v3 M18 3a4 4 0 0 1 0 8 M22 21v-3a4 4 0 0 0-3-4 M13 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0',
  Profile: 'M20 21v-3a6 6 0 0 0-6-6h-4a6 6 0 0 0-6 6v3 M16 5a4 4 0 1 1-8 0 4 4 0 0 1 8 0',
};
function NavIcon({ name }: { name: string }) {
  return (
    <svg
      aria-hidden="true"
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d={iconPaths[name] ?? iconPaths.Members} />
    </svg>
  );
}

export function MemberLayout() {
  const { state, retry } = useSession();
  const location = useLocation();
  if (state.kind !== 'ready' || !state.data.authenticated || !state.data.member)
    return <AccessPanel state={state} retry={retry} />;
  const member = state.data.member;
  const links = [
    { to: '/dashboard', label: 'Overview', allowed: true },
    { to: '/polls', label: 'Polls', allowed: member.capabilities.polls },
    { to: '/service', label: 'Service', allowed: member.capabilities.service_hours },
    { to: '/members', label: 'Members', allowed: true },
    { to: '/profile', label: 'Profile', allowed: true },
    { to: '/new-members', label: 'New members', allowed: member.capabilities.new_members },
  ];
  const brand = (
    <Link className="mb-10 block no-underline" to="/">
      <span className="block font-serif text-5xl tracking-tight text-[#ef4057]">ΣΦΔ</span>
      <span className="mt-2 block text-sm font-semibold text-white">Sigma Phi Delta</span>
    </Link>
  );
  return (
    <MemberShell
      brand={brand}
      navigation={(close) => (
        <nav aria-label="Member navigation" className="grid gap-2">
          {links
            .filter((link) => link.allowed)
            .map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                onClick={close}
                className={({ isActive }) =>
                  cn(
                    'flex min-h-12 items-center gap-3 rounded-lg px-4 py-3 text-sm no-underline',
                    isActive
                      ? 'bg-primary font-semibold text-white'
                      : 'text-[#e2e2e8] hover:bg-white/10',
                  )
                }
              >
                <NavIcon name={link.label} />
                {link.label}
              </NavLink>
            ))}
        </nav>
      )}
      footer={
        <div className="grid gap-4 text-sm text-[#c9c9d1]">
          {state.data.demo_enabled && (
            <Link className="text-inherit no-underline" to="/login">
              Change demo role
            </Link>
          )}
          <a className="text-inherit no-underline" href={`${chapterSite}legacy/`}>
            Legacy view
          </a>
          <SignOut />
        </div>
      }
      toolbar={
        <>
          <span className="ml-auto min-w-0 truncate text-sm font-medium text-[#5f606b]">
            {member.display_name}
          </span>
          {member.capabilities.service_hours &&
            !/^\/service\/(new|events\/)/.test(location.pathname) && <ServiceQuickEntry />}
        </>
      }
    >
      <Outlet context={member} />
    </MemberShell>
  );
}
