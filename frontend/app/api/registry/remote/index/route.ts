import { proxyLocalBackendJson } from '../../../local/_utils';

export const dynamic = 'force-dynamic';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const registryUrl = searchParams.get('registry_url');
  const pathname = registryUrl
    ? `/api/v1/registry/remote/index?registry_url=${encodeURIComponent(registryUrl)}`
    : '/api/v1/registry/remote/index';
  return proxyLocalBackendJson(pathname);
}
