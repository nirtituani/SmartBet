'use client';

import Link from 'next/link';
import { useEffect, useRef, useState } from 'react';
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

const KNOCKOUT_ROUNDS = [
  { label: 'Round of 32', labelHe: 'שלב 32',  dates: ['2026-06-28','2026-06-29','2026-06-30','2026-07-01','2026-07-02','2026-07-03','2026-07-04'], count: 16 },
  { label: 'Round of 16', labelHe: 'שמינית גמר', dates: ['2026-07-06','2026-07-07','2026-07-08','2026-07-09'], count: 8 },
  { label: 'Quarter Finals', labelHe: 'רבע גמר',   dates: ['2026-07-11','2026-07-12'], count: 4 },
  { label: 'Semi Finals',   labelHe: 'חצי גמר',   dates: ['2026-07-15','2026-07-16'], count: 2 },
  { label: '3rd Place',     labelHe: 'מקום שלישי', dates: ['2026-07-18'], count: 1 },
  { label: 'Final',         labelHe: 'גמר',        dates: ['2026-07-19'], count: 1 },
];

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

function KnockoutCard({ round, isHe }: { round: typeof KNOCKOUT_ROUNDS[0]; isHe: boolean }) {
  return (
    <div className="match-card match-card--tbd glass-card">
      <div className="match-card__team">
        <span className="match-card__flag match-card__flag--tbd">?</span>
        <span className="match-card__team-name match-card__team-name--tbd">TBD</span>
      </div>
      <div className="match-card__center">
        <span className="match-card__kickoff match-card__kickoff--tbd">VS</span>
        <span className="match-card__meta">{isHe ? round.labelHe : round.label}</span>
      </div>
      <div className="match-card__team match-card__team--away">
        <span className="match-card__flag match-card__flag--tbd">?</span>
        <span className="match-card__team-name match-card__team-name--tbd">TBD</span>
      </div>
    </div>
  );
}

function KnockoutSection({ isHe, lang }: { isHe: boolean; lang: string }) {
  return (
    <section className="knockout-section">
      <div className="knockout-section__header">
        <span className="knockout-section__title">{isHe ? 'שלבי הנוקאאוט' : 'Knockout Stage'}</span>
      </div>
      {KNOCKOUT_ROUNDS.map(round => (
        <div key={round.label} className="explorer__date-section">
          <div className="explorer__date-header">
            <span className="explorer__date-label">
              {isHe ? round.labelHe : round.label}
              {' · '}
              {round.dates[0] === round.dates[round.dates.length - 1]
                ? new Date(round.dates[0] + 'T12:00:00').toLocaleDateString(lang === 'he' ? 'he-IL' : 'en-US', { month: 'long', day: 'numeric' })
                : `${new Date(round.dates[0] + 'T12:00:00').toLocaleDateString(lang === 'he' ? 'he-IL' : 'en-US', { month: 'short', day: 'numeric' })} – ${new Date(round.dates[round.dates.length - 1] + 'T12:00:00').toLocaleDateString(lang === 'he' ? 'he-IL' : 'en-US', { month: 'short', day: 'numeric' })}`}
            </span>
          </div>
          {Array.from({ length: round.count }, (_, i) => (
            <KnockoutCard key={i} round={round} isHe={isHe} />
          ))}
        </div>
      ))}
    </section>
  );
}

export default function MatchExplorerClient({ matches: initialMatches }: { matches: Match[] }) {
  const { lang } = useLanguage();
  const tr = t[lang].matchExplorer;
  const [matches, setMatches] = useState<Match[]>(initialMatches);
  const upcomingRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchUpcomingMatches().then(setMatches).catch(() => {});
  }, []);

  useEffect(() => {
    if (upcomingRef.current) {
      const y = upcomingRef.current.getBoundingClientRect().top + window.scrollY - 80;
      window.scrollTo({ top: y, behavior: 'smooth' });
    }
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

      <div ref={upcomingRef}>
        <TournamentProgress matches={matches} lang={lang} />
      </div>

      {futureDates.map(d => renderDateSection(d, groupedFuture))}

      <KnockoutSection isHe={lang === 'he'} lang={lang} />
    </main>
  );
}
