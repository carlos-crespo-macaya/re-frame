interface Props {
  phase: string;
  onWrap: () => void;
  onDig: () => void;
}

/**
 * CTA section rendered at the bottom of the chat that adapts wording to the
 * current *phase*.
 */
export default function PhaseAwareFinish({ phase, onWrap, onDig }: Props) {
  if (phase !== "SUMMARY") return null;

  return (
    <div className="flex items-center justify-center gap-4 mt-4">
      <button
        className="px-4 py-2 rounded bg-emerald-600 text-white hover:bg-emerald-700"
        onClick={onWrap}
      >
        I'm good – wrap up
      </button>
      <button
        className="px-4 py-2 rounded bg-white border hover:bg-gray-50"
        onClick={onDig}
      >
        Let's dig deeper
      </button>
    </div>
  );
}

