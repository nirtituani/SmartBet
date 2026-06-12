'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useLanguage } from '@/contexts/LanguageContext';
import { t, translateTeam, translateGroup } from '@/lib/i18n';
import { fetchUpcomingMatches, groupMatchesByDate, formatDate, formatDateHebrew } from '@/lib/api';
import type { Match } from '@/lib/types';

function MatchCard({ match }: { match: Match }) {
  const { lang } = useLanguage();
  const finished = match.status === 'finished';
  const live = match.status === 'live';
  const hasScore = match.score_home !== null && match.score_away !== null;

  return (
    <Link href={`/match/${match.id}`} className={`match-card glass-card${finished ? ' match-card--finished' : ''}${live ? ' match-card--live' : ''}`}>
      <div className="match-card__team">
        <span className="match-card__flag">{match.home_team.flag}</span>
        <span className="match-card__team-name">{translateTeam(match.home_team.name, lang)}</span>
      </div>
      <div className="match-card__center">
        {hasScore ? (
          <span className={`match-card__score${live ? ' match-card__score--live' : ''}`}>
            {match.score_home} – {match.score_away}
          </span>
        ) : (
          <span className="match-card__kickoff">{match.kickoff_time}</span>
        )}
        <span className="match-card__meta">
          {live && <span className="match-card__live-dot" />}
          {translateGroup(match.group, lang)}
        </span>
      </div>
      <div className="match-card__team match-card__team--away">
        <span className="match-card__flag">{match.away_team.flag}</span>
        <span className="match-card__team-name">{translateTeam(match.away_team.name, lang)}</span>
      </div>
    </Link>
  );
}

export default function MatchExplorerClient({ matches: initialMatches }: { matches: Match[] }) {
  const { lang } = useLanguage();
  const tr = t[lang].matchExplorer;
  const [matches, setMatches] = useState<Match[]>(initialMatches);

  useEffect(() => {
    fetchUpcomingMatches().then(setMatches).catch(() => {});
  }, []);

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
