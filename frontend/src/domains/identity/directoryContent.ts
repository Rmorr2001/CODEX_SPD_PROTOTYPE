import { safePublicUrl } from '../../api/links';
import { memberJson } from '../../api/read';

export type DirectoryMember = {
  id: number;
  display_name: string;
  roles: { code: string; label: string }[];
  majors: string[];
  pclass: string | null;
  image: string | null;
};
export type DirectoryContent = { group: 'current' | 'alumni'; members: DirectoryMember[] };

function directoryMember(value: unknown): value is DirectoryMember {
  return Boolean(
    value &&
    typeof value === 'object' &&
    'id' in value &&
    typeof value.id === 'number' &&
    Number.isInteger(value.id) &&
    'display_name' in value &&
    typeof value.display_name === 'string' &&
    'roles' in value &&
    Array.isArray(value.roles) &&
    value.roles.every(
      (role: unknown) =>
        role &&
        typeof role === 'object' &&
        'code' in role &&
        typeof role.code === 'string' &&
        'label' in role &&
        typeof role.label === 'string',
    ) &&
    'majors' in value &&
    Array.isArray(value.majors) &&
    value.majors.every((major: unknown) => typeof major === 'string') &&
    'pclass' in value &&
    (value.pclass === null || typeof value.pclass === 'string') &&
    'image' in value &&
    safePublicUrl(value.image),
  );
}

export async function fetchDirectory(
  group: 'current' | 'alumni',
  signal: AbortSignal,
): Promise<DirectoryContent> {
  const data = await memberJson(`/api/v1/members/?group=${group}`, signal);
  if (
    !data ||
    typeof data !== 'object' ||
    !('group' in data) ||
    data.group !== group ||
    !('members' in data) ||
    !Array.isArray(data.members) ||
    !data.members.every(directoryMember)
  )
    throw new Error('Invalid directory content');
  return { group, members: data.members };
}
