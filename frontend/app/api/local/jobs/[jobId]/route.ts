import { proxyLocalBackendJson } from '../../_utils';

export const dynamic = 'force-dynamic';

interface Props {
  params: Promise<{ jobId: string }>;
}

export async function GET(_request: Request, { params }: Props) {
  const { jobId } = await params;
  return proxyLocalBackendJson(`/api/v1/local/jobs/${jobId}`);
}

