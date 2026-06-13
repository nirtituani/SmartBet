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

const TOTAL_MATCHES = 104;

function TournamentProgress({ matches, lang }: { matches: Match[]; lang: string }) {
  const played = matches.filter(m => m.status === 'finished').length;
  const remaining = TOTAL_MATCHES - played;
  const pct = Math.round((played / TOTAL_MATCHES) * 100);
  const isHe = lang === 'he';

  return (
    <div className="tournament-progress glass-card glass-card-blue">
      <div className="tournament-progress__header">
        <span className="tournament-progress__title">🏆 {isHe ? 'מונדיאל 2026' : 'FIFA World Cup 2026'}</span>
        <span className="tournament-progress__pct">{pct}%</span>
      </div>
      <div className="tournament-progress__bar">
        <div className="tournament-progress__fill" style={{ width: `${pct}%` }} />
      </div>
      <div className="tournament-progress__stats">
        <span className="tournament-progress__stat">
          <span className="tournament-progress__stat-num">{played}</span>
          <span className="tournament-progress__stat-label">{isHe ? 'שוחקו' : 'Played'}</span>
        </span>
        <span className="tournament-progress__divider">·</span>
        <span className="tournament-progress__stat">
          <span className="tournament-progress__stat-num">{remaining}</span>
          <span className="tournament-progress__stat-label">{isHe ? 'נותרו' : 'Remaining'}</span>
        </span>
      </div>
    </div>
  );
}

export default function MatchExplorerClient({ matches: initialMatches }: { matches: Match[] }) {
  const { lang } = useLanguage();
  const tr = t[lang].matchExplorer;
  const [matches, setMatches] = useState<Match[]>(initialMatches);

  useEffect(() => {
    fetchUpcomingMatches().then(setMatches).catch(() => {});
  }, []);

  const finishedMatches = matches.filter(m => m.status === 'finished');
  const upcomingMatches = matches.filter(m => m.status !== 'finished');

  const groupedPast = groupMatchesByDate(finishedMatches);
  const groupedFuture = groupMatchesByDate(upcomingMatches);
  const pastDates = Object.keys(groupedPast).sort();
  const futureDates = Object.keys(groupedFuture).sort();

  const renderDateSection = (date: string, group: Record<string, Match[]>) => (
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
      {group[date].map((match) => (
        <MatchCard key={match.id} match={match} />
      ))}
    </section>
  );

  return (
    <main className="explorer">
      <p className="explorer__breadcrumb">{tr.breadcrumb}</p>
      <h1 className="explorer__title">{tr.title}</h1>
      <p className="explorer__subtitle">{tr.subtitle}</p>

      {pastDates.map(d => renderDateSection(d, groupedPast))}

      <TournamentProgress matches={matches} lang={lang} />

      {futureDates.map(d => renderDateSection(d, groupedFuture))}
    </main>
  );
}
