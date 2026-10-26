import { memberJson } from '../../api/read';

export type Motion = {
  id: number;
  title: string;
  started_at: string;
  ended_at: string | null;
  aye: number;
  nay: number;
};
export type DecisionsContent = {
  current: Motion | null;
  closed: Motion[];
  can_manage: boolean;
  own_choice?: string | null;
};

export function isMotion(value: unknown): value is Motion {
  return Boolean(
    value &&
    typeof value === 'object' &&
    'id' in value &&
    Number.isInteger(value.id) &&
    'title' in value &&
    typeof value.title === 'string' &&
    'started_at' in value &&
    typeof value.started_at === 'string' &&
    !Number.isNaN(Date.parse(value.started_at)) &&
    'ended_at' in value &&
    (value.ended_at === null ||
      (typeof value.ended_at === 'string' && !Number.isNaN(Date.parse(value.ended_at)))) &&
    'aye' in value &&
    typeof value.aye === 'number' &&
    Number.isInteger(value.aye) &&
    value.aye >= 0 &&
    'nay' in value &&
    typeof value.nay === 'number' &&
    Number.isInteger(value.nay) &&
    value.nay >= 0,
  );
}

export async function fetchDecisions(signal: AbortSignal): Promise<DecisionsContent> {
  const data = await memberJson('/api/v1/polls/', signal);
  if (
    !data ||
    typeof data !== 'object' ||
    !('current' in data) ||
    !(data.current === null || (isMotion(data.current) && data.current.ended_at === null)) ||
    !('closed' in data) ||
    !Array.isArray(data.closed) ||
    !data.closed.every((value: unknown) => isMotion(value) && value.ended_at !== null) ||
    !('can_manage' in data) ||
    typeof data.can_manage !== 'boolean'
  )
    throw new Error('Invalid motion results');
  return {
    current: data.current,
    closed: data.closed,
    can_manage: data.can_manage,
    own_choice:
      'own_choice' in data && typeof data.own_choice === 'string' ? data.own_choice : null,
  };
}
