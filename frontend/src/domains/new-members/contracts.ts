import { memberJson } from '../../api/read';

export type MarkRecord = {
  id: number;
  title: string;
  value: number;
  date: string;
  status: 'requested' | 'approved' | 'denied';
  target_id: number;
  target_name: string;
  requester_id: number;
  requester_name: string;
  reviewed_by: string | null;
  reviewed_at: string | null;
  edited_by: string | null;
  edited_at: string | null;
  revision: string;
};
export type MarkOptions = { targets: { id: number; name: string }[]; classes: string[] };
export function isMark(value: unknown): value is MarkRecord {
  if (!value || typeof value !== 'object') return false;
  const row = value as Record<string, unknown>;
  return (
    ['id', 'value', 'target_id', 'requester_id'].every((key) => Number.isInteger(row[key])) &&
    ['title', 'date', 'target_name', 'requester_name', 'revision'].every(
      (key) => typeof row[key] === 'string',
    ) &&
    /^\d{4}-\d{2}-\d{2}$/.test(String(row.date)) &&
    !Number.isNaN(Date.parse(String(row.date))) &&
    /^[a-f0-9]{64}$/.test(String(row.revision)) &&
    ['requested', 'approved', 'denied'].includes(String(row.status)) &&
    ['reviewed_by', 'reviewed_at', 'edited_by', 'edited_at'].every(
      (key) => row[key] === null || typeof row[key] === 'string',
    )
  );
}
export async function readOptions(signal: AbortSignal): Promise<MarkOptions> {
  const data = (await memberJson('/api/v1/new-members/options/', signal)) as MarkOptions;
  if (
    !data ||
    !Array.isArray(data.targets) ||
    !data.targets.every(
      (item) => item && Number.isInteger(item.id) && typeof item.name === 'string',
    ) ||
    !Array.isArray(data.classes) ||
    !data.classes.every((item) => typeof item === 'string')
  )
    throw new Error('Invalid marks options.');
  return data;
}
export async function readMark(id: string, signal: AbortSignal): Promise<MarkRecord> {
  const data = await memberJson(`/api/v1/new-members/${id}/`, signal);
  if (!isMark(data)) throw new Error('Invalid mark.');
  return data;
}
export async function readReview(signal: AbortSignal): Promise<MarkRecord[]> {
  const data = await memberJson('/api/v1/new-members/review/', signal);
  if (!Array.isArray(data) || !data.every(isMark)) throw new Error('Invalid mark requests.');
  return data;
}
export function historyPath(legacy: string) {
  const id = /\/newmember\/history\/(\d+)\/$/.exec(legacy)?.[1];
  return id ? `/new-members/history/${id}` : '/new-members';
}
