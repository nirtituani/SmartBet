import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'SmartBet — AI Football Intelligence',
  description: 'AI-powered football betting predictions for World Cup 2026',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
