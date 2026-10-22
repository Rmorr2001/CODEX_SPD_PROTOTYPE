import { safePublicUrl } from '../../api/links';
import { memberJson } from '../../api/read';

export type OwnProfile = {
  display_name: string;
  first_name: string;
  last_name: string;
  username: string;
  email: string;
  hometown: string | null;
  pclass: string | null;
  majors: string[];
  roles: { code: string; label: string }[];
  image: string | null;
};

/** No selector is accepted: the server returns the actual caller's own profile. */
export async function fetchOwnProfile(signal: AbortSignal): Promise<OwnProfile> {
  const data = await memberJson('/api/v1/profile/', signal);
  if (!data || typeof data !== 'object') throw new Error('Invalid profile');
  const fields = data as Record<string, unknown>;
  if (
    !['display_name', 'first_name', 'last_name', 'username', 'email'].every(
      (key) => typeof fields[key] === 'string',
    ) ||
    !['hometown', 'pclass'].every(
      (key) => fields[key] === null || typeof fields[key] === 'string',
    ) ||
    !safePublicUrl(fields.image) ||
    !Array.isArray(fields.majors) ||
    !fields.majors.every((major: unknown) => typeof major === 'string') ||
    !Array.isArray(fields.roles) ||
    !fields.roles.every(
      (role: unknown) =>
        role &&
        typeof role === 'object' &&
        'code' in role &&
        typeof role.code === 'string' &&
        'label' in role &&
        typeof role.label === 'string',
    )
  )
    throw new Error('Invalid profile');
  return fields as OwnProfile;
}
