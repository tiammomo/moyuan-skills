import { proxyLocalBackendJson } from '../../../../local/_utils';

export const dynamic = 'force-dynamic';

interface Props {
  params: Promise<{ skillId: string }>;
}

export async function GET(request: Request, { params }: Props) {
  const { skillId } = await params;
  const { searchParams } = new URL(request.url);
  const registryUrl = searchParams.get('registry_url');
  const channel = searchParams.get('channel');
  const query = new URLSearchParams();
  if (registryUrl) {
    query.set('registry_url', registryUrl);
  }
  if (channel) {
    query.set('channel', channel);
  }
  const pathname = `/api/v1/registry/remote/skills/${encodeURIComponent(skillId)}${query.size ? `?${query.toString()}` : ''}`;
  return proxyLocalBackendJson(pathname);
}
