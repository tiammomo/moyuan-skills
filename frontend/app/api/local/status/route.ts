import { localBackendStatusResponse } from '../_utils';

export const dynamic = 'force-dynamic';

export async function GET() {
  return localBackendStatusResponse();
}

