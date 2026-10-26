import { useCallback, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { useMemberRead } from '../../api/read';
import { command, CommandError } from '../../api/write';
import { useMember } from '../identity/MemberLayout';
import { isMark, readMark, readOptions, type MarkOptions, type MarkRecord } from './contracts';
import { MarksFrame, MarksIcon } from './MarksFrame';
import { useUnsavedMark } from './useUnsavedMark';

type Draft = { targets: number[]; value: string; reason: string; date: string };
const emptyDraft = (): Draft => ({
  targets: [],
  value: '',
  reason: '',
  date: new Date().toLocaleDateString('en-CA'),
});

export function MarkForm() {
  const { id } = useParams();
  const load = useCallback(
    async (signal: AbortSignal) => {
      const [options, mark] = await Promise.all([
        readOptions(signal),
        id ? readMark(id, signal) : null,
      ]);
      return { options, mark };
    },
    [id],
  );
  const { state, retry } = useMemberRead(load);
  return (
    <MarksFrame
      title={id ? 'Edit mark' : 'Submit marks'}
      legacy={id ? `/newmember/edit/${id}/` : '/newmember/request/'}
    >
      {state.kind === 'ready' ? (
        <MarkFields key={id || 'create'} data={state.data} />
      ) : (
        <p role={state.kind === 'loading' ? 'status' : 'alert'}>
          {state.kind === 'loading'
            ? 'Loading form…'
            : 'This form is unavailable or access is denied.'}{' '}
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

function MarkFields({ data }: { data: { options: MarkOptions; mark: MarkRecord | null } }) {
  const member = useMember(),
    navigate = useNavigate();
  const mark = data.mark;
  const [initial] = useState<Draft>(() =>
    mark
      ? {
          targets: [mark.target_id],
          value: String(mark.value),
          reason: mark.title,
          date: mark.date,
        }
      : emptyDraft(),
  );
  const [draft, setDraft] = useState(initial);
  const [requestKey] = useState(() => crypto.randomUUID());
  const [conflict, setConflict] = useState(false);
  const [busy, setBusy] = useState(false),
    [error, setError] = useState('');
  const pending = useRef(false);
  const dirty = JSON.stringify(draft) !== JSON.stringify(initial);
  const allowLeave = useUnsavedMark(dirty, busy);
  const board = member.roles.some((role) => role.code === 'NM_BOARD');
  const allowed = mark ? board : member.roles.some((role) => role.code === 'ACTIVE');
  const canRevoke = board && member.roles.some((role) => role.code === 'NME');
  if (!allowed) return <p role="alert">Your role cannot perform this marks action.</p>;
  async function save(revoke = false) {
    if (pending.current) return;
    if (
      revoke &&
      !window.confirm('Deny this mark and replace its decision? Unsaved edits will not be applied.')
    )
      return;
    if (!revoke && !draft.targets.length) {
      setError('Select at least one new member.');
      return;
    }
    pending.current = true;
    setBusy(true);
    setError('');
    try {
      const fields = { mark_value: draft.value, mark_reason: draft.reason, mark_date: draft.date };
      const result = await command(
        mark
          ? `/api/v1/new-members/${mark.id}/${revoke ? 'revoke/' : ''}`
          : '/api/v1/new-members/submissions/',
        mark && !revoke ? 'PATCH' : 'POST',
        mark
          ? revoke
            ? { revision: mark.revision }
            : { ...fields, target_user: draft.targets[0], revision: mark.revision }
          : { ...fields, target_users: draft.targets, request_key: requestKey },
      );
      if (
        mark ? !isMark(result) : !Array.isArray(result) || !result.length || !result.every(isMark)
      )
        throw new Error('Unable to confirm this save. Check your submissions before retrying.');
      allowLeave();
      navigate(
        mark && !revoke
          ? `/new-members/history/${(result as MarkRecord).target_id}?saved=1`
          : '/new-members?submitted=1',
      );
    } catch (failure) {
      setConflict(failure instanceof CommandError && failure.status === 409);
      setError(failure instanceof Error ? failure.message : 'Unable to save marks.');
    } finally {
      pending.current = false;
      setBusy(false);
    }
  }
  return (
    <Card className="max-w-3xl p-6 sm:p-8">
      <form
        className="grid gap-6"
        onSubmit={(event) => {
          event.preventDefault();
          void save();
        }}
      >
        <fieldset disabled={busy} className="m-0 min-w-0 rounded-lg border border-border p-4">
          <legend className="px-2 text-sm font-semibold">
            {mark ? 'Recipient' : 'Recipients'}
          </legend>
          {mark ? (
            <select
              aria-label="Recipient"
              required
              className="w-full rounded-lg border border-border bg-white p-3"
              value={draft.targets[0] || ''}
              onChange={(e) => setDraft({ ...draft, targets: [Number(e.target.value)] })}
            >
              <option value="">Select a new member</option>
              {data.options.targets.map((target) => (
                <option key={target.id} value={target.id}>
                  {target.name}
                </option>
              ))}
            </select>
          ) : (
            <div className="grid gap-3 sm:grid-cols-2">
              {data.options.targets.map((target) => (
                <label
                  key={target.id}
                  className="flex cursor-pointer items-center gap-3 rounded-lg border border-border p-3 text-sm"
                >
                  <input
                    type="checkbox"
                    checked={draft.targets.includes(target.id)}
                    onChange={(e) =>
                      setDraft({
                        ...draft,
                        targets: e.target.checked
                          ? [...draft.targets, target.id]
                          : draft.targets.filter((id) => id !== target.id),
                      })
                    }
                  />
                  {target.name}
                </label>
              ))}
            </div>
          )}
          {!data.options.targets.length && <p>No eligible new members.</p>}
        </fieldset>
        <div className="grid gap-5 sm:grid-cols-2">
          <label className="grid gap-2 text-sm font-semibold">
            Marks
            <Input
              aria-label="Marks"
              aria-describedby="mark-value-hint"
              type="number"
              required
              step="1"
              min="-2147483648"
              max="2147483647"
              disabled={busy}
              value={draft.value}
              onChange={(e) => setDraft({ ...draft, value: e.target.value })}
            />
            <span id="mark-value-hint" className="text-xs font-normal text-muted-foreground">
              Positive, negative or zero
            </span>
          </label>
          <label className="grid gap-2 text-sm font-semibold">
            Date
            <Input
              type="date"
              required
              disabled={busy}
              value={draft.date}
              onChange={(e) => setDraft({ ...draft, date: e.target.value })}
            />
          </label>
        </div>
        <label className="grid gap-2 text-sm font-semibold">
          Reason
          <Input
            required
            maxLength={100}
            disabled={busy}
            value={draft.reason}
            onChange={(e) => setDraft({ ...draft, reason: e.target.value })}
          />
        </label>
        {error && (
          <p role="alert" className="text-sm text-primary">
            {error}
          </p>
        )}
        {mark && conflict && (
          <Button
            variant="outline"
            onClick={() => {
              if (window.confirm('Discard unsaved edits and reload this mark?')) {
                allowLeave();
                window.location.reload();
              }
            }}
          >
            Reload mark
          </Button>
        )}
        <div className="flex flex-wrap gap-3">
          <Button type="submit" disabled={busy || !data.options.targets.length}>
            <MarksIcon kind="submit" />
            {busy ? 'Saving…' : mark ? 'Save mark' : 'Submit marks'}
          </Button>
          <Button variant="outline" disabled={busy} onClick={() => navigate('/new-members')}>
            Cancel
          </Button>
          {mark && canRevoke && mark.status !== 'denied' && (
            <Button variant="outline" disabled={busy} onClick={() => void save(true)}>
              Deny mark
            </Button>
          )}
        </div>
      </form>
    </Card>
  );
}
