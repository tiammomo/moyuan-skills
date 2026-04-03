import type { NextRequest } from 'next/server';
import { proxyLocalBackendJson } from '../../local/_utils';

export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const query = searchParams.toString();
  return proxyLocalBackendJson(`/api/v1/author/overview${query ? `?${query}` : ''}`);
}
