import type { Metadata, Viewport } from "next";
import localFont from "next/font/local";
import "./globals.css";
import RootErrorBoundary from "@/components/error/RootErrorBoundary";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
  display: 'swap',
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
  display: 'swap',
});

export const metadata: Metadata = {
  title: "re-frame.social - Cognitive Reframing Support",
  description: "A transparent, AI-assisted cognitive reframing tool designed for people with Avoidant Personality Disorder (AvPD) and social anxiety.",
  keywords: ["cognitive reframing", "CBT", "mental health", "AvPD", "social anxiety", "self-help"],
  authors: [{ name: "re-frame.social" }],
  openGraph: {
    title: "re-frame.social - Cognitive Reframing Support",
    description: "A transparent, AI-assisted cognitive reframing tool for mental health support.",
    url: "https://re-frame.social",
    siteName: "re-frame.social",
    type: "website",
  },
  twitter: {
    card: "summary",
    title: "re-frame.social",
    description: "Transparent AI-assisted cognitive reframing for mental health support.",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
  userScalable: true,
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#ffffff' },
    { media: '(prefers-color-scheme: dark)', color: '#0a0a0a' },
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="scroll-smooth">
      <head>
        {/* Preconnect to potential external domains */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="dns-prefetch" href="https://fonts.googleapis.com" />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} font-sans antialiased min-h-screen`}
      >
        {/* Skip to main content link for screen readers */}
        <a href="#main-content" className="skip-link">
          Skip to main content
        </a>
        
        {/* Main application with error boundary */}
        <RootErrorBoundary>
          <div className="flex flex-col min-h-screen">
            {children}
          </div>
        </RootErrorBoundary>
      </body>
    </html>
  );
}
