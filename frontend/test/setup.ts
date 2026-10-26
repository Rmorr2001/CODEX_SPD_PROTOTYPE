import { request, type FullConfig } from '@playwright/test';

/** External Docker targets must be ready before the first domain scenario navigates. */
export default async function setup(config: FullConfig) {
  const api = await request.newContext({ baseURL: config.projects[0].use.baseURL });
  const deadline = Date.now() + 30000;
  try {
    while (Date.now() < deadline) {
      try {
        const response = await api.get('/api/v1/status/', { timeout: 1500 });
        if (response.ok()) {
          const data: unknown = await response.json();
          if (
            data &&
            typeof data === 'object' &&
            'status' in data &&
            data.status === 'ok' &&
            'api_version' in data &&
            data.api_version === 'v1'
          )
            return;
        }
      } catch {
        /* A container may still be running migrations and seeding. */
      }
      await new Promise((resolve) => setTimeout(resolve, 200));
    }
    throw new Error('The isolated application did not become ready within 30 seconds.');
  } finally {
    await api.dispose();
  }
}
