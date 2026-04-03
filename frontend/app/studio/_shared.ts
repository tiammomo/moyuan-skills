export interface StudioWorkspaceSearchParams {
  submissions_root?: string;
  inbox_root?: string;
}

export interface StudioWorkspaceOptions {
  submissionsRoot?: string;
  inboxRoot?: string;
}

function normalizeQueryValue(value: string | undefined): string | undefined {
  const trimmed = value?.trim();
  return trimmed ? trimmed : undefined;
}

export function getStudioWorkspaceOptions(
  searchParams: StudioWorkspaceSearchParams
): StudioWorkspaceOptions {
  return {
    submissionsRoot: normalizeQueryValue(searchParams.submissions_root),
    inboxRoot: normalizeQueryValue(searchParams.inbox_root),
  };
}

export function buildStudioHref(
  pathname: string,
  workspace: StudioWorkspaceSearchParams,
  extras: Record<string, string | undefined> = {}
): string {
  const params = new URLSearchParams();
  const submissionsRoot = normalizeQueryValue(workspace.submissions_root);
  const inboxRoot = normalizeQueryValue(workspace.inbox_root);

  if (submissionsRoot) {
    params.set('submissions_root', submissionsRoot);
  }
  if (inboxRoot) {
    params.set('inbox_root', inboxRoot);
  }

  for (const [key, value] of Object.entries(extras)) {
    const normalized = normalizeQueryValue(value);
    if (normalized) {
      params.set(key, normalized);
    }
  }

  const query = params.toString();
  return query ? `${pathname}?${query}` : pathname;
}
