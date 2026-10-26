import { useRef, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useMemberRead } from '../../api/read';
import { readOptions } from './contracts';
import { MarksFrame, MarksIcon } from './MarksFrame';

export function MarkExport() {
  const { state, retry } = useMemberRead(readOptions);
  const [pclass, setClass] = useState('Current'),
    [busy, setBusy] = useState(false),
    [error, setError] = useState('');
  const pending = useRef(false);
  async function download() {
    if (pending.current) return;
    pending.current = true;
    setBusy(true);
    setError('');
    const controller = new AbortController(),
      timer = window.setTimeout(() => controller.abort(), 15000);
    try {
      const response = await fetch(
        `/api/v1/new-members/export/?pclass=${encodeURIComponent(pclass)}`,
        { credentials: 'same-origin', cache: 'no-store', signal: controller.signal },
      );
      if (!response.ok || !response.headers.get('content-type')?.includes('spreadsheetml'))
        throw new Error('Unable to export marks. Check your access and selected class.');
      const url = URL.createObjectURL(await response.blob());
      const link = document.createElement('a');
      link.href = url;
      link.download = `Approved_${pclass}_Class_Newmember_Marks.xlsx`;
      document.body.append(link);
      link.click();
      link.remove();
      window.setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : 'Unable to export marks.');
    } finally {
      window.clearTimeout(timer);
      pending.current = false;
      setBusy(false);
    }
  }
  return (
    <MarksFrame
      title="Export marks"
      legacy={`/newmember/export-newmember-marks/?pclass=${encodeURIComponent(pclass)}`}
    >
      {state.kind === 'ready' ? (
        <Card className="max-w-2xl p-6 sm:p-8">
          <div className="mb-6 grid gap-2 text-sm font-semibold">
            <label htmlFor="marks-export-class">Class</label>
            <select
              id="marks-export-class"
              disabled={busy}
              className="rounded-lg border border-border bg-white p-3"
              value={pclass}
              onChange={(e) => setClass(e.target.value)}
            >
              {state.data.classes.map((value) => (
                <option key={value} value={value}>
                  {value}
                </option>
              ))}
            </select>
          </div>
          <Button disabled={busy} onClick={() => void download()}>
            <MarksIcon kind="export" />
            {busy ? 'Preparing…' : 'Download marks'}
          </Button>
          {error && (
            <p role="alert" className="mt-4 text-sm text-primary">
              {error}
            </p>
          )}
        </Card>
      ) : (
        <p role={state.kind === 'loading' ? 'status' : 'alert'}>
          {state.kind === 'loading'
            ? 'Loading classes…'
            : 'Marks export is unavailable or access is denied.'}{' '}
          {state.kind === 'failed' && (
            <Button variant="outline" onClick={retry}>
              Try again
            </Button>
          )}
        </p>
      )}
    </MarksFrame>
  );
}
