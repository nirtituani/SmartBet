'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useLanguage } from '@/contexts/LanguageContext';
import { t } from '@/lib/i18n';
import './Header.css';

export default function Header() {
  const pathname = usePathname();
  const { lang, setLang } = useLanguage();
  const tr = t[lang].nav;

  const NAV_LINKS = [
    { href: '/match-explorer', label: tr.matchExplorer },
    { href: '/groups',         label: tr.groups },
    { href: '/bracket',        label: tr.bracket },
  ];

  return (
    <header className="header">
      <div className="header__inner">
        <Link href="/match-explorer" className="header__logo">SmartBet</Link>
        <nav className="header__nav">
          {NAV_LINKS.map(({ href, label }) => (
            <Link
              key={href}
              href={href}
              className={`header__nav-link${pathname === href ? ' header__nav-link--active' : ''}`}
            >
              {label}
            </Link>
          ))}
        </nav>
        <div className="header__actions">
          <div className="header__lang-toggle">
            <button
              className={`header__lang-btn${lang === 'en' ? ' header__lang-btn--active' : ''}`}
              onClick={() => setLang('en')}
            >EN</button>
            <span className="header__lang-sep">|</span>
            <button
              className={`header__lang-btn${lang === 'he' ? ' header__lang-btn--active' : ''}`}
              onClick={() => setLang('he')}
            >HE</button>
          </div>
          <button className="header__icon-btn" aria-label="Search">🔍</button>
          <button className="header__icon-btn" aria-label="Notifications">🔔</button>
          <div className="header__avatar" aria-label="Profile">U</div>
        </div>
      </div>
    </header>
  );
}
