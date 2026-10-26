import { chapterSite } from '../../app/links';
import { csrfToken } from '../../api/write';

/** Native POST keeps session invalidation behind Django's CSRF boundary. */
export function SignOut() {
  return (
    <form method="post" action={`${chapterSite}auth/logout/`}>
      <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken()} />
      <button type="submit">Sign out</button>
    </form>
  );
}
