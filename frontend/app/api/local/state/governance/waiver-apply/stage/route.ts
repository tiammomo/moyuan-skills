import { proxyLocalBackendJson } from '../../../../_utils';

export const dynamic = 'force-dynamic';

export async function POST(request: Request) {
  const body = await request.json();
  return proxyLocalBackendJson('/api/v1/local/state/governance/waiver-apply/stage', {
    method: 'POST',
    body,
  });
}
