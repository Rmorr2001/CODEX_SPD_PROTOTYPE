import { safePublicUrl } from '../../api/links';
import { memberJson } from '../../api/read';

export type Mark = {
  id: number;
  title: string;
  value: number;
  date: string;
  status: 'approved' | 'requested' | 'denied';
};
export type Submission = Mark & { target_name: string };
export type ClassMember = {
  display_name: string;
  total_marks: number;
  is_negative: boolean;
  history_url: string;
};
export type MarksContent = {
  mode: 'personal' | 'active' | 'review';
  can_submit: boolean;
  can_review: boolean;
  personal: {
    total_marks: number;
    class_average: number;
    standing: string;
    latest_mark: Mark | null;
    history_url: string;
    history: Mark[];
  } | null;
  analytics: {
    total_new_members: number;
    members_in_good_standing: number;
    average_marks: number;
    marks_this_week: number;
    pending_requests: number;
  } | null;
  members: ClassMember[];
  submissions: Submission[];
};

function record(value: unknown): Record<string, unknown> {
  if (!value || typeof value !== 'object') throw new Error('Invalid marks response');
  return value as Record<string, unknown>;
}
function integer(value: unknown): value is number {
  return typeof value === 'number' && Number.isInteger(value);
}
function number(value: unknown): value is number {
  return typeof value === 'number' && Number.isFinite(value);
}
function mark(value: unknown): boolean {
  const data = record(value);
  return (
    integer(data.id) &&
    typeof data.title === 'string' &&
    integer(data.value) &&
    typeof data.date === 'string' &&
    /^\d{4}-\d{2}-\d{2}$/.test(data.date) &&
    !Number.isNaN(Date.parse(data.date)) &&
    ['approved', 'requested', 'denied'].includes(String(data.status))
  );
}
function link(value: unknown): boolean {
  return typeof value === 'string' && Boolean(safePublicUrl(value));
}

/** Validate role-specific data before rendering, including signed marks and safe legacy links. */
export async function fetchMarks(signal: AbortSignal): Promise<MarksContent> {
  const data = record(await memberJson('/api/v1/new-members/', signal));
  if (
    !['personal', 'active', 'review'].includes(String(data.mode)) ||
    typeof data.can_submit !== 'boolean' ||
    typeof data.can_review !== 'boolean' ||
    !Array.isArray(data.members) ||
    !Array.isArray(data.submissions)
  )
    throw new Error('Invalid marks response');
  if (data.personal !== null) {
    const personal = record(data.personal);
    if (
      !integer(personal.total_marks) ||
      !number(personal.class_average) ||
      !['Good Standing', 'Needs Improvement'].includes(String(personal.standing)) ||
      !link(personal.history_url) ||
      !Array.isArray(personal.history) ||
      !personal.history.every(mark) ||
      !(personal.latest_mark === null || mark(personal.latest_mark))
    )
      throw new Error('Invalid personal marks');
  }
  if (data.analytics !== null) {
    const analytics = record(data.analytics);
    if (
      ![
        'total_new_members',
        'members_in_good_standing',
        'marks_this_week',
        'pending_requests',
      ].every((key) => integer(analytics[key]) && (analytics[key] as number) >= 0) ||
      !number(analytics.average_marks)
    )
      throw new Error('Invalid marks analytics');
  }
  if (
    !data.members.every((value) => {
      const member = record(value);
      return (
        typeof member.display_name === 'string' &&
        integer(member.total_marks) &&
        typeof member.is_negative === 'boolean' &&
        link(member.history_url)
      );
    }) ||
    !data.submissions.every((value) => mark(value) && typeof record(value).target_name === 'string')
  )
    throw new Error('Invalid marks records');
  if (
    (data.mode === 'personal') !== (data.personal !== null) ||
    (data.mode === 'active') !== (data.analytics !== null) ||
    (data.mode !== 'active' && (data.members.length > 0 || data.submissions.length > 0))
  )
    throw new Error('Inconsistent marks scope');
  return data as MarksContent;
}

export function markDate(value: string): string {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    timeZone: 'UTC',
  }).format(new Date(`${value}T12:00:00Z`));
}
export function signed(value: number): string {
  return value > 0 ? `+${value}` : String(value);
}
