import { useEffect, useId, type Ref } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useServiceDraft, type ServiceGuard, type ServiceSaved } from './useServiceDraft';

/** Shared accessible fields for the Sheet and direct full-page create/edit routes. */
export function ServiceEntryForm({
  eventId,
  onSaved,
  onCancel,
  onGuardChange,
  firstFieldRef,
  compact = false,
}: {
  eventId?: string;
  onSaved: (result: ServiceSaved) => void;
  onCancel?: () => void;
  onGuardChange?: (state: ServiceGuard) => void;
  firstFieldRef?: Ref<HTMLInputElement>;
  compact?: boolean;
}) {
  const id = useId();
  const { draft, setDraft, loading, busy, dirty, error, save } = useServiceDraft(eventId);
  useEffect(() => {
    onGuardChange?.({ dirty, busy });
  }, [dirty, busy, onGuardChange]);
  if (loading) return <p role="status">Loading entry…</p>;
  return (
    <form
      className="service-entry flex min-h-0 flex-1 flex-col gap-6"
      onSubmit={async (event) => {
        event.preventDefault();
        const result = await save();
        if (result) onSaved(result);
      }}
    >
      <div className="grid gap-2">
        <label className="text-sm font-semibold" htmlFor={`${id}-event`}>
          {compact ? 'Event' : 'Event title'}
        </label>
        <Input
          id={`${id}-event`}
          ref={firstFieldRef}
          name="event_title"
          autoComplete="off"
          required
          maxLength={100}
          disabled={busy}
          value={draft.title}
          onChange={(e) => setDraft({ ...draft, title: e.target.value })}
        />
      </div>
      <div className="grid gap-2">
        <label className="text-sm font-semibold" htmlFor={`${id}-date`}>
          {compact ? 'Date' : 'Event date'}
        </label>
        <Input
          id={`${id}-date`}
          name="event_date"
          type="date"
          required
          disabled={busy}
          value={draft.date}
          onChange={(e) => setDraft({ ...draft, date: e.target.value })}
        />
      </div>
      <div className="grid gap-2">
        <label className="text-sm font-semibold" htmlFor={`${id}-hours`}>
          Hours
        </label>
        <Input
          id={`${id}-hours`}
          name="hours"
          type="number"
          min="0.5"
          step="0.01"
          max="99999999.99"
          required
          disabled={busy}
          value={draft.hours}
          onChange={(e) => setDraft({ ...draft, hours: e.target.value })}
        />
        <span className="text-xs text-muted-foreground">Minimum 0.5 hours</span>
      </div>
      {error && (
        <p role="alert" className="m-0 text-sm text-[#a91729]">
          {error}
        </p>
      )}
      <div className="mt-auto flex flex-wrap gap-3 border-t border-border pt-6">
        <Button type="submit" disabled={busy || (Boolean(eventId) && !draft.title)}>
          {busy
            ? 'Submitting…'
            : eventId
              ? 'Save service entry'
              : compact
                ? 'Submit'
                : 'Submit hours'}
        </Button>
        {onCancel && (
          <Button variant="outline" disabled={busy} onClick={onCancel}>
            Cancel
          </Button>
        )}
      </div>
    </form>
  );
}
