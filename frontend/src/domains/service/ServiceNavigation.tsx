import { NavLink } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { useMember } from '../identity/MemberLayout';

const icons = {
  hours: 'M12 8v4l3 2 M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0',
  totals: 'M4 20V10h4v10 M10 20V4h4v16 M16 20v-7h4v7',
  requests: 'M9 4H5v17h14V4h-4 M9 2h6v5H9z M8 12h8 M8 16h5',
  history: 'M4 5v5h5 M4 10a8 8 0 1 1 0 5 M12 8v5l3 2',
  download: 'M12 3v12 M7 10l5 5 5-5 M4 17v4h16v-4',
  plus: 'M12 4v16 M4 12h16',
};
export function ServiceIcon({ name }: { name: keyof typeof icons }) {
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
      <path d={icons[name]} />
    </svg>
  );
}

/** Navigation remains native links; buttons supply consistent visual and keyboard affordances. */
export function ServiceNavigation() {
  const member = useMember();
  if (!member.capabilities.service_hours) return null;
  const canReview = member.roles.some((role) => role.code === 'PHIL_CHAIR');
  const items = [
    { to: '/service', label: 'Your hours', icon: 'hours', allowed: true, end: true },
    { to: '/service/chapter', label: 'Chapter totals', icon: 'totals', allowed: true },
    {
      to: '/service/review',
      label: 'Review service requests',
      text: 'Requests',
      icon: 'requests',
      allowed: canReview,
    },
    {
      to: '/service/history',
      label: 'View your service history',
      text: 'History',
      icon: 'history',
      allowed: true,
    },
  ] as const;
  return (
    <nav aria-label="Service tools" className="mb-6 flex flex-wrap gap-2">
      {items
        .filter((item) => item.allowed)
        .map((item) => (
          <Button asChild variant="outline" key={item.to}>
            <NavLink
              to={item.to}
              end={'end' in item && item.end}
              aria-label={item.label}
              className="no-underline aria-[current=page]:border-primary aria-[current=page]:bg-primary/5 aria-[current=page]:text-primary"
            >
              <ServiceIcon name={item.icon} />
              {'text' in item ? item.text : item.label}
            </NavLink>
          </Button>
        ))}
      <Button asChild variant="outline">
        <a
          className="no-underline"
          href="/api/v1/service/export/"
          aria-label="Download approved hours (XLSX)"
        >
          <ServiceIcon name="download" />
          Export
        </a>
      </Button>
    </nav>
  );
}
