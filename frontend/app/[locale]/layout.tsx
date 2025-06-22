import type { Metadata, Viewport } from "next";
import localFont from "next/font/local";
import { Inter } from "next/font/google";
import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';
import { notFound } from 'next/navigation';
import "../globals.css";
import RootErrorBoundary from "@/components/error/RootErrorBoundary";
import { ThemeProvider } from "@/lib/theme/ThemeContext";
import { themeScript } from "@/lib/theme/theme-script";
import { routing } from '@/i18n/routing';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

const geistSans = localFont({
  src: "../fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
  display: 'swap',
});
const geistMono = localFont({
  src: "../fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
  display: 'swap',
});

export function generateStaticParams() {
  return routing.locales.map((locale) => ({locale}));
}

export async function generateMetadata({
  params: {locale}
}: {
  params: {locale: string};
}): Promise<Metadata> {
  
  return {
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
      locale: locale,
      alternateLocale: routing.locales.filter(l => l !== locale),
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
    alternates: {
      languages: Object.fromEntries(
        routing.locales.map((locale) => [locale, `/${locale}`])
      ),
    },
  };
}

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

export default async function LocaleLayout({
  children,
  params: {locale}
}: Readonly<{
  children: React.ReactNode;
  params: {locale: string};
}>) {
  // Ensure that the incoming locale is valid
  if (!routing.locales.includes(locale as (typeof routing.locales)[number])) {
    notFound();
  }

  // Providing all messages to the client
  // side is the easiest way to get started
  const messages = await getMessages();
  return (
    <html lang={locale} className="scroll-smooth" suppressHydrationWarning>
      <head>
        {/* Preconnect to potential external domains */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="dns-prefetch" href="https://fonts.googleapis.com" />
        
        {/* Prevent FOUC with theme */}
        <script
          dangerouslySetInnerHTML={{
            __html: themeScript,
          }}
        />
      </head>
      <body
        className={`${inter.variable} ${geistSans.variable} ${geistMono.variable} font-sans antialiased min-h-screen`}
        suppressHydrationWarning
      >
        {/* Skip to main content link for screen readers */}
        <a href="#main-content" className="skip-link">
          Skip to main content
        </a>
        
        <NextIntlClientProvider messages={messages}>
          {/* Theme provider wrapper */}
          <ThemeProvider>
            {/* Main application with error boundary */}
            <RootErrorBoundary>
              <div className="flex flex-col min-h-screen">
                {children}
              </div>
            </RootErrorBoundary>
          </ThemeProvider>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
