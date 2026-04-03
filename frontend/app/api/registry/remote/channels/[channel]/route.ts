import { proxyLocalBackendJson } from '../../../../local/_utils';

export const dynamic = 'force-dynamic';

interface Props {
  params: Promise<{ channel: string }>;
}

export async function GET(request: Request, { params }: Props) {
  const { channel } = await params;
  const { searchParams } = new URL(request.url);
  const registryUrl = searchParams.get('registry_url');
  const pathname = registryUrl
    ? `/api/v1/registry/remote/channels/${encodeURIComponent(channel)}?registry_url=${encodeURIComponent(registryUrl)}`
    : `/api/v1/registry/remote/channels/${encodeURIComponent(channel)}`;
  return proxyLocalBackendJson(pathname);
}
