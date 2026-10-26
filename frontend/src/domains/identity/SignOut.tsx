import { Button } from '@/components/ui/button';
import { chapterSite } from '../../app/links';
import { csrfToken } from '../../api/write';

/** Native POST keeps session invalidation behind Django's CSRF boundary. */
export function SignOut() {
  return (
    <form method="post" action={`${chapterSite}auth/logout/`}>
      <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken()} />
      <Button type="submit" variant="ghost" className="min-h-0 justify-start p-0 text-inherit">
        Sign out
      </Button>
    </form>
  );
}
