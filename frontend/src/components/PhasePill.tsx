type Phase = "GREETING" | "DISCOVERY" | "REFRAMING" | "SUMMARY";

const colours: Record<Phase, string> = {
  GREETING: "bg-emerald-200",
  DISCOVERY: "bg-blue-200",
  REFRAMING: "bg-violet-200",
  SUMMARY: "bg-amber-200",
};

export default function PhasePill({ phase }: { phase: Phase }) {
  return (
    <span
      className={`px-3 py-1 rounded-full text-xs font-medium ${colours[phase]} transition-colors`}
    >
      {phase}
    </span>
  );
}

