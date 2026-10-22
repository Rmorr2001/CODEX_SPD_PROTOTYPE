import { safePublicUrl } from '../../api/links';
import { memberJson } from '../../api/read';

export type ServiceEvent = {
  id: number;
  title: string;
  date: string;
  hours: number;
  status: 'requested' | 'approved' | 'denied';
};
export type ServiceContent = {
  year: number;
  available_years: number[];
  start_date: string;
  end_date: string;
  approved_hours: number;
  can_review: boolean;
  history_url: string;
  events: ServiceEvent[];
};

function event(value: unknown): value is ServiceEvent {
  return Boolean(
    value &&
    typeof value === 'object' &&
    'id' in value &&
    Number.isInteger(value.id) &&
    'title' in value &&
    typeof value.title === 'string' &&
    'date' in value &&
    typeof value.date === 'string' &&
    /^\d{4}-\d{2}-\d{2}$/.test(value.date) &&
    !Number.isNaN(Date.parse(value.date)) &&
    'hours' in value &&
    typeof value.hours === 'number' &&
    Number.isInteger(value.hours) &&
    value.hours >= 0 &&
    'status' in value &&
    ['requested', 'approved', 'denied'].includes(String(value.status)),
  );
}

export async function fetchService(
  year: string | null,
  signal: AbortSignal,
): Promise<ServiceContent> {
  const value = await memberJson(
    `/api/v1/service/${year ? `?year=${encodeURIComponent(year)}` : ''}`,
    signal,
  );
  if (!value || typeof value !== 'object') throw new Error('Invalid service response');
  const data = value as Record<string, unknown>;
  if (
    typeof data.year !== 'number' ||
    !Number.isInteger(data.year) ||
    !Array.isArray(data.available_years) ||
    !data.available_years.every(
      (year: unknown) => typeof year === 'number' && Number.isInteger(year),
    ) ||
    !data.available_years.includes(data.year) ||
    typeof data.start_date !== 'string' ||
    typeof data.end_date !== 'string' ||
    !/^\d{4}-\d{2}-\d{2}$/.test(data.start_date) ||
    !/^\d{4}-\d{2}-\d{2}$/.test(data.end_date) ||
    typeof data.approved_hours !== 'number' ||
    !Number.isInteger(data.approved_hours) ||
    data.approved_hours < 0 ||
    typeof data.can_review !== 'boolean' ||
    typeof data.history_url !== 'string' ||
    !safePublicUrl(data.history_url) ||
    !Array.isArray(data.events) ||
    !data.events.every(event)
  )
    throw new Error('Invalid service response');
  return data as ServiceContent;
}
