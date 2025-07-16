import { useEffect, useState } from "react";

/**
 * Lightweight browser-speech recognition hook.
 *
 * NOTE: This is a *very* trimmed-down implementation that relies on the
 * legacy `webkitSpeechRecognition` interface available in Chrome.  It is good
 * enough for local development; production-grade apps should polyfill or
 * replace it with a more robust solution.
 */
export default function useSpeechInput(onFinal: (text: string) => void) {
  const [partial, setPartial] = useState("");

  useEffect(() => {
    const SpeechRec = (window as any).webkitSpeechRecognition;
    if (!SpeechRec) {
      // Browser does not support the API – noop.
      return;
    }

    const rec: any = new SpeechRec();
    rec.interimResults = true;
    rec.continuous = false;

    rec.onresult = (e: any) => {
      const transcript = Array.from(e.results)
        .map((r: any) => r[0].transcript)
        .join(" ");

      if (e.results[0].isFinal) {
        // Optionally hit backend for ASR enhancement.
        fetch("/api/v1/enhance_asr", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ partial: transcript }),
        })
          .then((r) => r.json())
          .then((d) => onFinal(d.transcript || transcript))
          .catch(() => onFinal(transcript));

        setPartial("");
      } else {
        setPartial(transcript);
      }
    };

    rec.start();
    return () => rec.stop();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return partial;
}

