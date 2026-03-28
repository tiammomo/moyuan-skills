'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import type {
  LocalInstalledDoctorSnapshot,
  LocalInstalledGovernanceState,
  LocalInstalledSkillRecord,
  LocalInstalledState,
} from '@/types/market';
import { InstalledBaselinePanel } from '@/components/market/InstalledBaselinePanel';
import { InstalledGovernancePanel } from '@/components/market/InstalledGovernancePanel';
import { InstalledWaiverApplyPanel } from '@/components/market/InstalledWaiverApplyPanel';
import { Card } from '@/components/ui/Card';
import { Chip } from '@/components/ui/Chip';
import { Button } from '@/components/ui/Button';
import { InstalledDoctorPanel } from '@/components/market/InstalledDoctorPanel';
import { LocalExecutionCard, type LocalExecutionCardProps } from '@/components/market/LocalExecutionCard';
import {
  LOCAL_TARGET_UPDATED_EVENT,
  type LocalTargetUpdatedDetail,
} from '@/lib/local-target-events';

interface InstalledStatePanelProps {
  panelTestId: string;
  title: string;
  description: string;
  targetRoot: string;
  skillId?: string;
  skillName?: string;
  bundleId?: string;
  actions: Array<LocalExecutionCardProps>;
}

function formatSources(sources: LocalInstalledSkillRecord['sources']): string {
  if (!Array.isArray(sources) || sources.length === 0) {
    return '-';
  }
  return sources.map((source) => `${source.kind}:${source.id}`).join(', ');
}

export function InstalledStatePanel({
  panelTestId,
  title,
  description,
  targetRoot,
  skillId,
  skillName,
  bundleId,
  actions,
}: InstalledStatePanelProps) {
  const [statePayload, setStatePayload] = useState<LocalInstalledState | null>(null);
  const [doctorSnapshot, setDoctorSnapshot] = useState<LocalInstalledDoctorSnapshot | null>(null);
  const [governanceState, setGovernanceState] = useState<LocalInstalledGovernanceState | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [refreshCounter, setRefreshCounter] = useState(0);
  const hasLoadedStateRef = useRef(false);

  const refreshState = useCallback(() => {
    setRefreshCounter((value) => value + 1);
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function loadState() {
      if (!hasLoadedStateRef.current) {
        setLoading(true);
      }
      setErrorMessage(null);
      try {
        const response = await fetch(`/api/local/state?target_root=${encodeURIComponent(targetRoot)}`, {
          cache: 'no-store',
        });
        const payload = (await response.json()) as LocalInstalledState | { detail?: string };
        if (!response.ok) {
          if (!cancelled) {
            setErrorMessage(
              payload && 'detail' in payload ? payload.detail ?? 'Unable to read installed state.' : 'Unable to read installed state.'
            );
            hasLoadedStateRef.current = true;
            setLoading(false);
          }
          return;
        }
        if (!cancelled) {
          setStatePayload(payload as LocalInstalledState);
          hasLoadedStateRef.current = true;
          setLoading(false);
        }
      } catch (error) {
        if (!cancelled) {
          setErrorMessage(
            `Unable to read installed state: ${error instanceof Error ? error.message : String(error)}`
          );
          hasLoadedStateRef.current = true;
          setLoading(false);
        }
      }
    }

    void loadState();

    return () => {
      cancelled = true;
    };
  }, [refreshCounter, targetRoot]);

  useEffect(() => {
    function handleLocalTargetUpdated(event: Event) {
      const customEvent = event as CustomEvent<LocalTargetUpdatedDetail>;
      if (customEvent.detail?.targetRoot !== targetRoot) {
        return;
      }
      refreshState();
    }

    window.addEventListener(LOCAL_TARGET_UPDATED_EVENT, handleLocalTargetUpdated as EventListener);
    return () => {
      window.removeEventListener(LOCAL_TARGET_UPDATED_EVENT, handleLocalTargetUpdated as EventListener);
    };
  }, [refreshState, targetRoot]);

  const installedSkill = useMemo(() => {
    if (!statePayload || !skillId) {
      return null;
    }
    return (
      statePayload.installed.find(
        (item) => item.skill_id === skillId || (skillName ? item.skill_name === skillName : false)
      ) ?? null
    );
  }, [skillId, skillName, statePayload]);

  const installedBundle = useMemo(() => {
    if (!statePayload || !bundleId) {
      return null;
    }
    return statePayload.bundles.find((item) => item.bundle_id === bundleId) ?? null;
  }, [bundleId, statePayload]);

  const installedStatusLabel = installedSkill || installedBundle ? 'Installed in target root' : 'Not installed yet';
  const installedStatusVariant = installedSkill || installedBundle ? 'keyword' : 'internal';

  return (
    <div className="space-y-5" data-testid={panelTestId}>
      <Card className="p-5">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2">
              <Chip variant={installedStatusVariant} data-testid={`${panelTestId}-status`}>
                {installedStatusLabel}
              </Chip>
              <Chip variant="tag">Installed-state lifecycle</Chip>
            </div>
            <div>
              <h3 className="text-sm font-semibold uppercase tracking-wider text-olive mb-2">{title}</h3>
              <p className="text-sm text-muted">{description}</p>
            </div>
          </div>
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={refreshState}
            data-testid={`${panelTestId}-refresh`}
          >
            Refresh state
          </Button>
        </div>

        <div className="mt-4 space-y-3">
          {loading && (
            <p className="text-xs text-muted" data-testid={`${panelTestId}-loading`}>
              Loading installed-state snapshot...
            </p>
          )}

          {errorMessage && (
            <div
              className="rounded-card border border-line bg-bg/70 px-3 py-3 text-xs text-ink"
              data-testid={`${panelTestId}-error`}
            >
              {errorMessage}
            </div>
          )}

          {statePayload && (
            <div
              className="rounded-card border border-line bg-bg/70 px-3 py-3"
              data-testid={`${panelTestId}-summary`}
            >
              <dl className="space-y-2 text-xs text-ink">
                <div className="flex justify-between gap-3">
                  <dt className="text-muted">Target root</dt>
                  <dd className="text-right break-all">{statePayload.target_root}</dd>
                </div>
                <div className="flex justify-between gap-3">
                  <dt className="text-muted">Installed skills</dt>
                  <dd>{statePayload.installed_count}</dd>
                </div>
                <div className="flex justify-between gap-3">
                  <dt className="text-muted">Installed bundles</dt>
                  <dd>{statePayload.bundle_count}</dd>
                </div>
                {installedSkill && (
                  <>
                    <div className="flex justify-between gap-3">
                      <dt className="text-muted">Skill id</dt>
                      <dd className="text-right break-all">{installedSkill.skill_id}</dd>
                    </div>
                    <div className="flex justify-between gap-3">
                      <dt className="text-muted">Installed version</dt>
                      <dd>{installedSkill.version}</dd>
                    </div>
                    <div className="flex justify-between gap-3">
                      <dt className="text-muted">Installed at</dt>
                      <dd className="text-right break-all">{installedSkill.installed_at}</dd>
                    </div>
                    <div className="flex justify-between gap-3">
                      <dt className="text-muted">Sources</dt>
                      <dd className="text-right break-all">{formatSources(installedSkill.sources)}</dd>
                    </div>
                  </>
                )}
                {installedBundle && (
                  <>
                    <div className="flex justify-between gap-3">
                      <dt className="text-muted">Bundle id</dt>
                      <dd className="text-right break-all">{installedBundle.bundle_id}</dd>
                    </div>
                    <div className="flex justify-between gap-3">
                      <dt className="text-muted">Active bundle skills</dt>
                      <dd>{installedBundle.skill_count}</dd>
                    </div>
                    <div className="flex justify-between gap-3">
                      <dt className="text-muted">Bundle report</dt>
                      <dd className="text-right break-all">{installedBundle.report_path}</dd>
                    </div>
                    <div className="flex justify-between gap-3">
                      <dt className="text-muted">Managed skill ids</dt>
                      <dd className="text-right break-all">
                        {installedBundle.active_skill_ids.length > 0 ? installedBundle.active_skill_ids.join(', ') : '-'}
                      </dd>
                    </div>
                  </>
                )}
              </dl>
            </div>
          )}
        </div>
      </Card>

      <InstalledDoctorPanel
        panelTestId={`${panelTestId}-doctor`}
        targetRoot={targetRoot}
        onDoctorSettled={setDoctorSnapshot}
        onRepairSettled={refreshState}
      />

      <InstalledBaselinePanel
        panelTestId={`${panelTestId}-baseline`}
        targetRoot={targetRoot}
        doctorSnapshot={doctorSnapshot}
        onBaselineSettled={refreshState}
      />

      <InstalledGovernancePanel
        panelTestId={`${panelTestId}-governance`}
        targetRoot={targetRoot}
        refreshToken={refreshCounter}
        onGovernanceStateChange={setGovernanceState}
      />

      <InstalledWaiverApplyPanel
        panelTestId={`${panelTestId}-waiver-apply`}
        targetRoot={targetRoot}
        governanceState={governanceState}
      />

      {actions.map((action) => (
        <LocalExecutionCard
          key={action.panelTestId}
          {...action}
          onJobSettled={(job) => {
            refreshState();
            action.onJobSettled?.(job);
          }}
        />
      ))}
    </div>
  );
}
