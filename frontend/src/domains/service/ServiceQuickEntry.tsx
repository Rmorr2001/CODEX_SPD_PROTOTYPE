import { useCallback, useEffect, useRef, useState } from 'react';
import { Link, useBeforeUnload, useBlocker, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import { ServiceEntryForm } from './ServiceEntryForm';
import type { ServiceGuard } from './useServiceDraft';

/** A service-page Sheet protects drafts across refresh and navigation. */
export function ServiceQuickEntry() {
  const [open, setOpen] = useState(false);
  const [guard, setGuard] = useState<ServiceGuard>({ dirty: false, busy: false });
  const [savedYear, setSavedYear] = useState<number | null>(null);
  useEffect(() => {
    if (savedYear === null) return;
    const timer = window.setTimeout(() => setSavedYear(null), 6000);
    return () => window.clearTimeout(timer);
  }, [savedYear]);
  const firstField = useRef<HTMLInputElement>(null);
  const location = useLocation();
  const blocker = useBlocker(open && (guard.dirty || guard.busy));
  const previousLocation = useRef(location.key);
  function close(next: boolean) {
    if (!next && guard.busy) return;
    if (!next && guard.dirty && !window.confirm('Discard unsaved service entry?')) return;
    setOpen(next);
    if (!next) setGuard({ dirty: false, busy: false });
  }
  useBeforeUnload(
    useCallback(
      (event) => {
        if (open && (guard.dirty || guard.busy)) {
          event.preventDefault();
          event.returnValue = '';
        }
      },
      [open, guard.dirty, guard.busy],
    ),
  );
  useEffect(() => {
    if (blocker.state !== 'blocked') return;
    if (!guard.busy && window.confirm('Discard unsaved service entry?')) {
      setOpen(false);
      setGuard({ dirty: false, busy: false });
      blocker.proceed();
    } else blocker.reset();
  }, [blocker, guard.busy]);
  useEffect(() => {
    if (previousLocation.current !== location.key) {
      setOpen(false);
      setGuard({ dirty: false, busy: false });
      previousLocation.current = location.key;
    }
  }, [location.key]);
  return (
    <>
      <Sheet open={open} onOpenChange={close}>
        <SheetTrigger asChild>
          <Button>Log service</Button>
        </SheetTrigger>
        <SheetContent
          title="Log service"
          closeLabel="Close service drawer"
          busy={guard.busy}
          onOpenAutoFocus={(event) => {
            event.preventDefault();
            firstField.current?.focus();
          }}
        >
          <ServiceEntryForm
            compact
            firstFieldRef={firstField}
            onGuardChange={setGuard}
            onCancel={() => close(false)}
            onSaved={({ year }) => {
              setSavedYear(year);
              setGuard({ dirty: false, busy: false });
              setOpen(false);
            }}
          />
        </SheetContent>
      </Sheet>
      {savedYear !== null && (
        <div className="fixed bottom-5 right-5 z-30 max-w-[calc(100%-40px)] rounded-lg border border-border bg-white p-4 shadow-sm">
          <span role="status" className="text-sm">
            Service submitted.
          </span>{' '}
          <Link
            className="text-sm font-semibold"
            to={`/service?year=${savedYear}`}
            onClick={() => setSavedYear(null)}
          >
            View service
          </Link>
          <Button
            variant="ghost"
            className="ml-2 min-h-8 px-2"
            aria-label="Dismiss service confirmation"
            onClick={() => setSavedYear(null)}
          >
            ×
          </Button>
        </div>
      )}
    </>
  );
}
