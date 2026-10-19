export interface ServiceStatus {
  status: 'ok';
  api_version: 'v1';
}

/** Read the public service contract; reject unexpected payloads before rendering. */
export async function fetchStatus(signal: AbortSignal): Promise<ServiceStatus> {
  const response = await fetch('/api/v1/status/', {
    headers: { Accept: 'application/json' },
    credentials: 'same-origin',
    cache: 'no-store',
    signal,
  });
  if (!response.ok || !response.headers.get('content-type')?.includes('application/json')) {
    throw new Error('Service response unavailable');
  }
  const value: unknown = await response.json();
  if (
    typeof value !== 'object' ||
    value === null ||
    !('status' in value) ||
    value.status !== 'ok' ||
    !('api_version' in value) ||
    value.api_version !== 'v1'
  ) {
    throw new Error('Unexpected service response');
  }
  return { status: value.status, api_version: value.api_version };
}
