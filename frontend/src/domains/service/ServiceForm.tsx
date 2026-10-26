import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { useMember } from '../identity/MemberLayout';
import { memberJson } from '../../api/read';
import { command } from '../../api/write';
import { serviceRecord } from './transactions';

export function ServiceForm() {
  const { id } = useParams();
  const member = useMember();
  const allowed = member.roles.some((role) => role.code === (id ? 'PHIL_CHAIR' : 'ACTIVE'));
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [hours, setHours] = useState('');
  const [date, setDate] = useState('');
  const [loading, setLoading] = useState(Boolean(id));
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  useEffect(() => {
    if (!id) return;
    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), 15000);
    setLoading(true);
    void memberJson(`/api/v1/service/${id}/`, controller.signal)
      .then((result) => {
        if (!serviceRecord(result)) throw new Error('Invalid service entry');
        setTitle(result.title);
        setHours(String(result.hours));
        setDate(result.date);
      })
      .catch(() =>
        setError('Unable to load this service entry. Return to service hours and try again.'),
      )
      .finally(() => {
        setLoading(false);
        window.clearTimeout(timer);
      });
    return () => {
      controller.abort();
      window.clearTimeout(timer);
    };
  }, [id]);
  if (!allowed) return <p role="alert">Your role cannot perform this service action.</p>;
  return (
    <section>
      <Link to="/service">Service hours</Link>
      <h1>{id ? 'Edit service entry' : 'Log service hours'}</h1>
      <p>Minimum 0.5 hours.</p>
      {loading ? (
        <p role="status">Loading entry…</p>
      ) : (
        <form
          className="transaction-panel"
          onSubmit={async (event) => {
            event.preventDefault();
            setBusy(true);
            setError('');
            try {
              await command(
                id ? `/api/v1/service/${id}/` : '/api/v1/service/',
                id ? 'PATCH' : 'POST',
                { event_title: title, hours, event_date: date },
              );
              const year = Number(date.slice(0, 4)) - (Number(date.slice(5, 7)) <= 6 ? 1 : 0);
              navigate(id ? '/service/review' : `/service?year=${year}&submitted=1`);
            } catch (e) {
              setError(e instanceof Error ? e.message : 'Unable to save service entry.');
            } finally {
              setBusy(false);
            }
          }}
        >
          <label htmlFor="service-title">Event title</label>
          <input
            id="service-title"
            required
            maxLength={100}
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
          <label htmlFor="service-hours">Hours</label>
          <input
            id="service-hours"
            type="number"
            min="0.5"
            step="0.01"
            max="99999999.99"
            required
            value={hours}
            onChange={(e) => setHours(e.target.value)}
          />
          <label htmlFor="service-date">Event date</label>
          <input
            id="service-date"
            type="date"
            required
            value={date}
            onChange={(e) => setDate(e.target.value)}
          />
          <button disabled={busy || (Boolean(id) && !title)}>
            {busy ? 'Saving…' : id ? 'Save service entry' : 'Submit hours'}
          </button>
        </form>
      )}
      {error && <p role="alert">{error}</p>}
    </section>
  );
}
