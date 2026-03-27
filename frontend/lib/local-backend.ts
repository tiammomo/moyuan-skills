const LOCAL_BACKEND_TIMEOUT_MS = 5000;

function sanitizeBaseUrl(value: string | undefined): string | null {
  const trimmed = value?.trim();
  if (!trimmed) {
    return null;
  }

  return trimmed.replace(/\/+$/, '');
}

export function getLocalBackendBaseUrl(): string | null {
  return sanitizeBaseUrl(process.env.SKILLS_MARKET_API_BASE_URL);
}

export async function getLocalBackendAvailability(): Promise<{
  available: boolean;
  configured: boolean;
  message: string;
}> {
  const baseUrl = getLocalBackendBaseUrl();
  if (!baseUrl) {
    return {
      available: false,
      configured: false,
      message: 'Backend execution is available only when SKILLS_MARKET_API_BASE_URL is configured.',
    };
  }

  try {
    const response = await fetch(`${baseUrl}/health`, {
      cache: 'no-store',
      signal: AbortSignal.timeout(LOCAL_BACKEND_TIMEOUT_MS),
    });

    if (!response.ok) {
      return {
        available: false,
        configured: true,
        message: `Backend execution health check failed: ${response.status} ${response.statusText}`,
      };
    }

    return {
      available: true,
      configured: true,
      message: `Backend execution is ready at ${baseUrl}.`,
    };
  } catch (error) {
    return {
      available: false,
      configured: true,
      message: `Backend execution is configured but unreachable: ${
        error instanceof Error ? error.message : String(error)
      }`,
    };
  }
}

