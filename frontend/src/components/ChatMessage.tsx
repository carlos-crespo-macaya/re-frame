import diffMatchPatch from "diff-match-patch"; // run-time dependency – safe to import even if absent in unit tests
interface DiffMsg {
  type: "diff";
  prev: string;
  next: string;
}

interface SimpleMsg {
  type?: undefined;
  content: string;
}

type Msg = DiffMsg | SimpleMsg;

export default function ChatMessage({ msg }: { msg: Msg }) {
  // Render diff-highlighted message
  if ((msg as DiffMsg).type === "diff") {
    const { prev, next } = msg as DiffMsg;
    const dmp = new diffMatchPatch();
    const diff = dmp.diff_main(prev, next);
    dmp.diff_cleanupSemantic(diff);

    return (
      <p className="whitespace-pre-wrap">
        {diff.map(([op, txt], i) => {
          if (op === 1) {
            return (
              <span key={i} className="text-green-600">
                {txt}
              </span>
            );
          }
          if (op === -1) {
            return (
              <span key={i} className="line-through text-red-500">
                {txt}
              </span>
            );
          }
          return txt;
        })}
      </p>
    );
  }

  // Simple text
  const simple = msg as SimpleMsg;
  return <p className="whitespace-pre-wrap">{simple.content}</p>;
}

