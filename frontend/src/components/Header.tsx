'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import './Header.css';

const NAV_LINKS = [
  { href: '/match-explorer', label: 'Match Explorer' },
  { href: '/live-odds',      label: 'Live Odds' },
  { href: '/stats',          label: 'Stats' },
];

export default function Header() {
  const pathname = usePathname();

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
          <button className="header__icon-btn" aria-label="Search">🔍</button>
          <button className="header__icon-btn" aria-label="Notifications">🔔</button>
          <div className="header__avatar" aria-label="Profile">U</div>
        </div>
      </div>
    </header>
  );
}
