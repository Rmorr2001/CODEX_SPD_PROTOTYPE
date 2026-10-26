import { useEffect, useRef, useState } from 'react';
import { memberJson } from '../../api/read';
import { command } from '../../api/write';
import { serviceRecord } from './transactions';

export type ServiceGuard = { dirty: boolean; busy: boolean };
export type ServiceSaved = { year: number };
function initialDraft() {
  return { title: '', hours: '', date: new Date().toLocaleDateString('en-CA') };
}

/** A form-local draft is independent of all background resource refreshes. */
export function useServiceDraft(eventId?: string) {
  const [draft, setDraft] = useState(initialDraft);
  const [baseline, setBaseline] = useState(initialDraft);
  const [loading, setLoading] = useState(Boolean(eventId));
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const sending = useRef(false);
  useEffect(() => {
    if (!eventId) return;
    let active = true;
    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), 15000);
    void memberJson(`/api/v1/service/${eventId}/`, controller.signal)
      .then((result) => {
        if (!serviceRecord(result)) throw new Error('Invalid entry');
        if (active) {
          const next = { title: result.title, hours: String(result.hours), date: result.date };
          setDraft(next);
          setBaseline(next);
        }
      })
      .catch(() => {
        if (active) setError('Unable to load this entry. Return to service and try again.');
      })
      .finally(() => {
        window.clearTimeout(timer);
        if (active) setLoading(false);
      });
    return () => {
      active = false;
      controller.abort();
      window.clearTimeout(timer);
    };
  }, [eventId]);
  const dirty =
    draft.title !== baseline.title ||
    draft.hours !== baseline.hours ||
    draft.date !== baseline.date;
  async function save(): Promise<ServiceSaved | null> {
    if (sending.current) return null;
    sending.current = true;
    setBusy(true);
    setError('');
    try {
      const result = await command(
        eventId ? `/api/v1/service/${eventId}/` : '/api/v1/service/',
        eventId ? 'PATCH' : 'POST',
        {
          event_title: draft.title,
          hours: draft.hours,
          event_date: draft.date,
        },
      );
      if (!serviceRecord(result)) throw new Error('Check your service records before retrying.');
      setBaseline(draft);
      return {
        year: Number(draft.date.slice(0, 4)) - (Number(draft.date.slice(5, 7)) <= 6 ? 1 : 0),
      };
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unable to save. Please try again.');
      return null;
    } finally {
      sending.current = false;
      setBusy(false);
    }
  }
  return { draft, setDraft, loading, busy, dirty, error, save };
}
