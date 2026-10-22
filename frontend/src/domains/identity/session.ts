import { useEffect, useState } from 'react';

export type Capabilities = {
  dashboard: boolean;
  members: boolean;
  profile: boolean;
  polls: boolean;
  service_hours: boolean;
  new_members: boolean;
};
export type Member = {
  display_name: string;
  roles: { code: string; label: string }[];
  capabilities: Capabilities;
};
export type Session = {
  authenticated: boolean;
  profile_available: boolean;
  demo_enabled: boolean;
  landing_path: string;
  member: Member | null;
};
export type SessionState =
  { kind: 'loading' } | { kind: 'failed' } | { kind: 'ready'; data: Session };

function isMember(value: unknown): value is Member {
  if (
    !value ||
    typeof value !== 'object' ||
    !('display_name' in value) ||
    typeof value.display_name !== 'string' ||
    !('roles' in value) ||
    !Array.isArray(value.roles) ||
    !value.roles.every(
      (role: unknown) =>
        role &&
        typeof role === 'object' &&
        'code' in role &&
        typeof role.code === 'string' &&
        'label' in role &&
        typeof role.label === 'string',
    ) ||
    !('capabilities' in value) ||
    !value.capabilities ||
    typeof value.capabilities !== 'object'
  )
    return false;
  const capabilities = value.capabilities;
  return ['dashboard', 'members', 'profile', 'polls', 'service_hours', 'new_members'].every(
    (key) =>
      key in capabilities && typeof (capabilities as Record<string, unknown>)[key] === 'boolean',
  );
}

/** Session identity comes only from Django, never from browser storage or demo labels. */
async function fetchSession(signal: AbortSignal): Promise<Session> {
  const response = await fetch('/api/v1/session/', {
    credentials: 'same-origin',
    headers: { Accept: 'application/json' },
    signal,
    cache: 'no-store',
  });
  if (!response.ok || !response.headers.get('content-type')?.includes('application/json'))
    throw new Error('Session unavailable');
  const data: unknown = await response.json();
  if (
    !data ||
    typeof data !== 'object' ||
    !('authenticated' in data) ||
    typeof data.authenticated !== 'boolean' ||
    !('profile_available' in data) ||
    typeof data.profile_available !== 'boolean' ||
    !('demo_enabled' in data) ||
    typeof data.demo_enabled !== 'boolean' ||
    !('landing_path' in data) ||
    typeof data.landing_path !== 'string' ||
    !['/app/login', '/app/dashboard', '/app/new-members'].includes(data.landing_path) ||
    !('member' in data) ||
    !(data.member === null || isMember(data.member))
  )
    throw new Error('Invalid session contract');
  if (
    data.profile_available !== Boolean(data.member) ||
    (!data.authenticated && data.member !== null)
  )
    throw new Error('Inconsistent session');
  return {
    authenticated: data.authenticated,
    profile_available: data.profile_available,
    demo_enabled: data.demo_enabled,
    landing_path: data.landing_path,
    member: data.member,
  };
}

export function useSession() {
  const [state, setState] = useState<SessionState>({ kind: 'loading' });
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let active = true;
    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), 15000);
    setState({ kind: 'loading' });
    fetchSession(controller.signal)
      .then((data) => {
        if (active) setState({ kind: 'ready', data });
      })
      .catch(() => {
        if (active) setState({ kind: 'failed' });
      })
      .finally(() => window.clearTimeout(timer));
    return () => {
      active = false;
      controller.abort();
      window.clearTimeout(timer);
    };
  }, [attempt]);
  return { state, retry: () => setAttempt((value) => value + 1) };
}
