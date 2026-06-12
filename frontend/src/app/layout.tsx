import type { Metadata } from 'next';
import { Analytics } from '@vercel/analytics/next';
import { LanguageProvider } from '@/contexts/LanguageContext';
import './globals.css';

export const metadata: Metadata = {
  title: 'SmartBet — AI Football Intelligence',
  description: 'AI-powered football betting predictions for World Cup 2026',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <LanguageProvider>{children}</LanguageProvider>
        <Analytics />
      </body>
    </html>
  );
}
