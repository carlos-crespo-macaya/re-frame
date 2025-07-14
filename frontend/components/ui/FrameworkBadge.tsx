import { Framework } from '@/types/api';

interface FrameworkBadgeProps {
  framework: Framework;
}

const frameworkColors: Record<Framework, { bg: string; text: string }> = {
  CBT: { bg: 'bg-blue-900/20', text: 'text-blue-400' },
  DBT: { bg: 'bg-purple-900/20', text: 'text-purple-400' },
  ACT: { bg: 'bg-green-900/20', text: 'text-green-400' },
  Stoicism: { bg: 'bg-amber-900/20', text: 'text-amber-400' }
};

export default function FrameworkBadge({ framework }: FrameworkBadgeProps) {
  const colors = frameworkColors[framework];

  return (
    <span
      className={`inline-flex items-center px-2 py-1 rounded-md text-xs font-medium ${colors.bg} ${colors.text} border border-current/20`}
    >
      {framework}
    </span>
  );
}