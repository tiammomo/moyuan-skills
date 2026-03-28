import { proxyLocalBackendJson } from '../../../_utils';

export const dynamic = 'force-dynamic';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const targetRoot = searchParams.get('target_root');
  const pathname = targetRoot
    ? `/api/v1/local/state/governance/waiver-apply?target_root=${encodeURIComponent(targetRoot)}`
    : '/api/v1/local/state/governance/waiver-apply';
  return proxyLocalBackendJson(pathname);
}
