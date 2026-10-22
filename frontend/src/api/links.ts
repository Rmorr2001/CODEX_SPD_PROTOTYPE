/** Shared read-model URL guard; reject executable schemes and credential-bearing links. */
export function safePublicUrl(value: unknown): value is string | null {
  if (value === null) return true;
  if (typeof value !== 'string' || /[\s\\]/.test(value)) return false;
  if (/^\/(?!\/)/.test(value)) return true;
  try {
    const url = new URL(value);
    return (
      ['http:', 'https:'].includes(url.protocol) &&
      Boolean(url.hostname) &&
      !url.username &&
      !url.password
    );
  } catch {
    return false;
  }
}
