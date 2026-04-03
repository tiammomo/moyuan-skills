import { proxyLocalBackendJson } from '../../../local/_utils';

export const dynamic = 'force-dynamic';

export async function POST(request: Request) {
  const body = await request.json();
  return proxyLocalBackendJson('/api/v1/author/submissions/upload', {
    method: 'POST',
    body,
  });
}
