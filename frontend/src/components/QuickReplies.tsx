interface Props {
  suggestions: string[];
  onSelect: (text: string) => void;
}

export default function QuickReplies({ suggestions, onSelect }: Props) {
  if (!suggestions?.length) return null;

  return (
    <div className="flex gap-2 mt-2">
      {suggestions.slice(0, 3).map((s) => (
        <button
          key={s}
          className="px-3 py-1 border rounded-full text-sm hover:bg-gray-100"
          onClick={() => onSelect(s)}
        >
          {s}
        </button>
      ))}
    </div>
  );
}

