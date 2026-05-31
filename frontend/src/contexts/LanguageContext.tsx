'use client';

import { createContext, useContext, useState, useEffect } from 'react';
import type { Lang } from '@/lib/i18n';

const LanguageContext = createContext<{
  lang: Lang;
  setLang: (l: Lang) => void;
}>({ lang: 'en', setLang: () => {} });

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLangState] = useState<Lang>('en');

  useEffect(() => {
    const saved = localStorage.getItem('smartbet-lang') as Lang | null;
    if (saved === 'he' || saved === 'en') setLangState(saved); // eslint-disable-line react-hooks/set-state-in-effect
  }, []);

  function setLang(l: Lang) {
    setLangState(l);
    localStorage.setItem('smartbet-lang', l);
  }

  return (
    <LanguageContext.Provider value={{ lang, setLang }}>
      <div dir={lang === 'he' ? 'rtl' : 'ltr'} style={{ minHeight: '100vh' }}>
        {children}
      </div>
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  return useContext(LanguageContext);
}
