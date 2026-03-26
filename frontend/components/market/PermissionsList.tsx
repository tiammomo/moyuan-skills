import type { Permissions } from '@/types/market';
import { Chip } from '@/components/ui/Chip';

interface PermissionsListProps {
  permissions: Permissions;
}

const labelMap: Record<string, string> = {
  Workspace: '工作区',
  Shell: '终端',
  Network: '网络',
  Secrets: '密钥',
};

const valueMap: Record<string, string> = {
  none: '无',
  read: '只读',
  write: '读写',
  limited: '受限',
  full: '完全',
};

export function PermissionsList({ permissions }: PermissionsListProps) {
  const items = [
    { label: 'Workspace', value: permissions.workspace },
    { label: 'Shell', value: permissions.shell },
    { label: 'Network', value: permissions.network },
    { label: 'Secrets', value: permissions.secrets },
  ];

  return (
    <div className="space-y-2">
      {items.map(({ label, value }) => (
        <div key={label} className="flex items-center justify-between">
          <span className="text-sm text-muted">{labelMap[label] || label}</span>
          <span
            className={`text-xs font-medium px-2 py-0.5 rounded-full ${
              value === 'none'
                ? 'bg-[#f3efe4] text-muted'
                : value === 'read' || value === 'limited'
                ? 'bg-[#fff4e8] text-accent'
                : 'bg-[#fff4e8] text-accent font-semibold'
            }`}
          >
            {valueMap[value] || value}
          </span>
        </div>
      ))}
      {permissions.human_review_required && (
        <div className="pt-2 mt-2 border-t border-line">
          <Chip variant="keyword" className="text-xs">
            需要人工审核
          </Chip>
        </div>
      )}
    </div>
  );
}
