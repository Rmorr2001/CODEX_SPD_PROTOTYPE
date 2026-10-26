import { useNavigate, useParams } from 'react-router-dom';
import { useMember } from '../identity/MemberLayout';
import { Card } from '@/components/ui/card';
import { ServiceNavigation } from './ServiceNavigation';
import { ServiceEntryForm } from './ServiceEntryForm';

export function ServiceForm() {
  const { id } = useParams();
  const member = useMember();
  const navigate = useNavigate();
  const allowed = member.roles.some((role) => role.code === (id ? 'PHIL_CHAIR' : 'ACTIVE'));
  if (!allowed) return <p role="alert">Your role cannot perform this service action.</p>;
  return (
    <section>
      <ServiceNavigation />
      <h1 className="mt-4">{id ? 'Edit service entry' : 'Log service hours'}</h1>
      <Card className="max-w-2xl p-6 sm:p-8">
        <ServiceEntryForm
          key={id || 'create'}
          eventId={id}
          onSaved={({ year }) =>
            navigate(id ? '/service/review' : `/service?year=${year}&submitted=1`)
          }
        />
      </Card>
    </section>
  );
}
