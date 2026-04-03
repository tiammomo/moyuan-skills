import { proxyLocalBackendJson } from '../../../../local/_utils';

export const dynamic = 'force-dynamic';

interface Props {
  params: Promise<{ bundleId: string }>;
}

export async function GET(request: Request, { params }: Props) {
  const { bundleId } = await params;
  const { searchParams } = new URL(request.url);
  const registryUrl = searchParams.get('registry_url');
  const pathname = registryUrl
    ? `/api/v1/registry/remote/bundles/${encodeURIComponent(bundleId)}?registry_url=${encodeURIComponent(registryUrl)}`
    : `/api/v1/registry/remote/bundles/${encodeURIComponent(bundleId)}`;
  return proxyLocalBackendJson(pathname);
}
