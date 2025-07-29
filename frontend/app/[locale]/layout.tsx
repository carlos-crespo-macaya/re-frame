import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "CBT Reframing Assistant",
  description: "Cognitive Behavioral Therapy assistant powered by Google's ADK",
};

export default function LocaleLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: { locale: string };
}) {
  return children;
}