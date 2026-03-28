import { proxyLocalBackendJson } from '../../../_utils';

export const dynamic = 'force-dynamic';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const query = searchParams.toString();
  return proxyLocalBackendJson(`/api/v1/local/docs/actions/history${query ? `?${query}` : ''}`);
}
