import type { LocalJobRecord } from '@/types/market';

export const LOCAL_TARGET_UPDATED_EVENT = 'moyuan:local-target-updated';

export interface LocalTargetUpdatedDetail {
  targetRoot: string;
  jobId: string;
  status: LocalJobRecord['status'];
}

function readStringValue(value: unknown): string | null {
  if (typeof value !== 'string') {
    return null;
  }
  const normalized = value.trim();
  return normalized.length > 0 ? normalized : null;
}

export function getLocalTargetRootForJob(
  job: LocalJobRecord,
  requestBody: Record<string, unknown>
): string | null {
  return (
    readStringValue(job.artifacts.target_root) ??
    readStringValue(job.summary.target_root) ??
    readStringValue(requestBody.target_root)
  );
}

export function dispatchLocalTargetUpdated(detail: LocalTargetUpdatedDetail) {
  if (typeof window === 'undefined') {
    return;
  }
  window.dispatchEvent(new CustomEvent<LocalTargetUpdatedDetail>(LOCAL_TARGET_UPDATED_EVENT, { detail }));
}
