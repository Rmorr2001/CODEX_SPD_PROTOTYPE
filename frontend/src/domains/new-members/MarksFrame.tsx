import type { ReactNode } from 'react';
import { NavLink } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { useMember } from '../identity/MemberLayout';

export function MarksIcon({
  kind,
}: {
  kind: 'overview' | 'submit' | 'review' | 'export' | 'legacy';
}) {
  const paths = {
    overview: 'M4 5h16v15H4z M8 9h8 M8 13h8 M8 17h5',
    submit: 'M12 4v16 M4 12h16',
    review: 'M4 12l5 5L20 6',
    export: 'M12 3v12 M7 10l5 5 5-5 M4 17v4h16v-4',
    legacy: 'M14 4h6v6 M20 4L10 14 M10 4H4v16h16v-6',
  };
  return (
    <svg
      aria-hidden="true"
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d={paths[kind]} />
    </svg>
  );
}
export function MarksFrame({
  title,
  legacy,
  children,
}: {
  title: string;
  legacy: string;
  children: ReactNode;
}) {
  const member = useMember();
  const active = member.roles.some((role) => role.code === 'ACTIVE');
  const board = member.roles.some((role) => role.code === 'NM_BOARD');
  const eligible = active || board || member.roles.some((role) => role.code === 'NEW_MEMBER');
  const links = [
    { to: '/new-members', label: 'Overview', icon: 'overview', allowed: eligible, end: true },
    { to: '/new-members/new', label: 'Submit marks', icon: 'submit', allowed: active },
    { to: '/new-members/review', label: 'Review marks', icon: 'review', allowed: board },
    { to: '/new-members/export', label: 'Export marks', icon: 'export', allowed: eligible },
  ] as const;
  return (
    <section>
      <h1 className="mb-6">{title}</h1>
      <nav aria-label="Marks tools" className="mb-6 flex flex-wrap gap-2">
        {links
          .filter((link) => link.allowed)
          .map((link) => (
            <Button asChild variant="outline" key={link.to}>
              <NavLink
                to={link.to}
                end={'end' in link && link.end}
                className="no-underline aria-[current=page]:border-primary aria-[current=page]:bg-primary/5 aria-[current=page]:text-primary"
              >
                <MarksIcon kind={link.icon} />
                {link.label}
              </NavLink>
            </Button>
          ))}
        <Button asChild variant="ghost">
          <a className="no-underline text-muted-foreground" href={legacy}>
            <MarksIcon kind="legacy" />
            Legacy view
          </a>
        </Button>
      </nav>
      {children}
    </section>
  );
}
