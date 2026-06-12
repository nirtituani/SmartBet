import type { Metadata } from 'next';
import Script from 'next/script';
import { LanguageProvider } from '@/contexts/LanguageContext';
import './globals.css';

const GA_ID = 'G-ZDC13PNTKJ';

export const metadata: Metadata = {
  title: 'SmartBet — AI Football Intelligence',
  description: 'AI-powered football betting predictions for World Cup 2026',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <Script src={`https://www.googletagmanager.com/gtag/js?id=${GA_ID}`} strategy="afterInteractive" />
        <Script id="ga-init" strategy="afterInteractive">{`
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
          gtag('config', '${GA_ID}');
        `}</Script>
      </head>
      <body>
        <LanguageProvider>{children}</LanguageProvider>
      </body>
    </html>
  );
}
