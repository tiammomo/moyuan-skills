import { NextResponse } from 'next/server';
import { getLocalBackendAvailability, getLocalBackendBaseUrl } from '@/lib/local-backend';

type ProxyOptions = {
  method?: string;
  body?: unknown;
};

export async function localBackendStatusResponse() {
  const status = await getLocalBackendAvailability();
  return NextResponse.json(status, {
    status: status.available ? 200 : 503,
  });
}

export async function proxyLocalBackendJson(pathname: string, options?: ProxyOptions) {
  const baseUrl = getLocalBackendBaseUrl();
  if (!baseUrl) {
    return NextResponse.json(
      {
        detail: 'SKILLS_MARKET_API_BASE_URL is not configured for frontend local execution.',
      },
      { status: 503 }
    );
  }

  try {
    const headers = new Headers({
      accept: 'application/json',
    });

    let body: string | undefined;
    if (options?.body !== undefined) {
      headers.set('content-type', 'application/json');
      body = JSON.stringify(options.body);
    }

    const response = await fetch(`${baseUrl}${pathname}`, {
      method: options?.method ?? 'GET',
      headers,
      body,
      cache: 'no-store',
      signal: AbortSignal.timeout(5000),
    });

    const responseText = await response.text();
    return new NextResponse(responseText, {
      status: response.status,
      headers: {
        'content-type': response.headers.get('content-type') ?? 'application/json',
      },
    });
  } catch (error) {
    return NextResponse.json(
      {
        detail: `Local backend request failed: ${error instanceof Error ? error.message : String(error)}`,
      },
      { status: 502 }
    );
  }
}

