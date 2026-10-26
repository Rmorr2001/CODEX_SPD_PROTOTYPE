import { memberJson } from '../../api/read';

export type ServiceRecord = {
  id: number;
  title: string;
  date: string;
  hours: number;
  status: 'requested' | 'approved' | 'denied';
  owner_id: number;
  owner_name: string;
  reviewed_by: string | null;
  reviewed_at: string | null;
  edited_at: string | null;
};
export function serviceRecord(value: unknown): value is ServiceRecord {
  if (!value || typeof value !== 'object') return false;
  const row = value as Record<string, unknown>;
  return (
    Number.isInteger(row.id) &&
    Number.isInteger(row.owner_id) &&
    typeof row.owner_name === 'string' &&
    typeof row.title === 'string' &&
    typeof row.date === 'string' &&
    /^\d{4}-\d{2}-\d{2}$/.test(row.date) &&
    typeof row.hours === 'number' &&
    Number.isFinite(row.hours) &&
    row.hours >= 0 &&
    ['requested', 'approved', 'denied'].includes(String(row.status))
  );
}
export type ReviewRecord = ServiceRecord & { can_decide: boolean };
function reviewRecord(value: unknown): value is ReviewRecord {
  return serviceRecord(value) && 'can_decide' in value && typeof value.can_decide === 'boolean';
}

export async function readRecords(url: string, signal: AbortSignal): Promise<ReviewRecord[]> {
  const result = await memberJson(url, signal);
  if (!Array.isArray(result) || !result.every(reviewRecord))
    throw new Error('Invalid service records');
  return result;
}
