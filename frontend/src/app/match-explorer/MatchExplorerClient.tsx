'use client';

import Link from 'next/link';
import { useLanguage } from '@/contexts/LanguageContext';
import { t, translateTeam, translateGroup } from '@/lib/i18n';
import { groupMatchesByDate, formatDate, formatDateHebrew } from '@/lib/api';
import type { Match } from '@/lib/types';

function MatchCard({ match }: { match: Match }) {
  const { lang } = useLanguage();
  return (
    <Link href={`/match/${match.id}`} className="match-card glass-card">
      <div className="match-card__team">
        <span className="match-card__flag">{match.home_team.flag}</span>
        <span className="match-card__team-name">{translateTeam(match.home_team.name, lang)}</span>
      </div>
      <div className="match-card__center">
        <span className="match-card__kickoff">
          {match.kickoff_time}
        </span>
        <span className="match-card__meta">{translateGroup(match.group, lang)}</span>
      </div>
      <div className="match-card__team match-card__team--away">
        <span className="match-card__flag">{match.away_team.flag}</span>
        <span className="match-card__team-name">{translateTeam(match.away_team.name, lang)}</span>
      </div>
    </Link>
  );
}

export default function MatchExplorerClient({ matches }: { matches: Match[] }) {
  const { lang } = useLanguage();
  const tr = t[lang].matchExplorer;
  const grouped = groupMatchesByDate(matches);
  const sortedDates = Object.keys(grouped).sort();

  return (
    <main className="explorer">
      <p className="explorer__breadcrumb">{tr.breadcrumb}</p>
      <h1 className="explorer__title">{tr.title}</h1>
      <p className="explorer__subtitle">{tr.subtitle}</p>

      {sortedDates.map((date) => (
        <section key={date} className="explorer__date-section">
          <div className="explorer__date-header">
            {lang === 'he' ? (
              <span className="explorer__date-label explorer__date-label--hebrew" dir="rtl">
                {formatDateHebrew(date)}
              </span>
            ) : (
              <span className="explorer__date-label">{formatDate(date)}</span>
            )}
          </div>
          {grouped[date].map((match) => (
            <MatchCard key={match.id} match={match} />
          ))}
        </section>
      ))}
    </main>
  );
}
