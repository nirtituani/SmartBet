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

// Exact knockout schedule from ESPN (times in UTC)
type KOTeam = { name?: string; flag?: string; seed: string };
type KOFixture = { date: string; time: string; home: KOTeam; away: KOTeam; round: string };

function toIDT(date: string, utcTime: string): string {
  return new Date(`${date}T${utcTime}:00Z`).toLocaleTimeString('en-GB', {
    hour: '2-digit', minute: '2-digit', timeZone: 'Asia/Jerusalem',
  });
}

function toIDTDate(date: string, utcTime: string): string {
  return new Date(`${date}T${utcTime}:00Z`).toLocaleDateString('en-CA', {
    timeZone: 'Asia/Jerusalem',
  });
}

const R32: KOFixture[] = [
  { date: '2026-06-28', time: '19:00', round: 'Round of 32', home: { seed: '2A' },                                         away: { seed: '2B' } },
  { date: '2026-06-29', time: '17:00', round: 'Round of 32', home: { seed: '1C' },                                         away: { seed: '2F' } },
  { date: '2026-06-29', time: '20:30', round: 'Round of 32', home: { seed: '1E', name: 'Germany',   flag: '🇩🇪' },          away: { seed: '3rd A/B/C/D/F' } },
  { date: '2026-06-30', time: '01:00', round: 'Round of 32', home: { seed: '1F' },                                         away: { seed: '2C' } },
  { date: '2026-06-30', time: '17:00', round: 'Round of 32', home: { seed: '2E' },                                         away: { seed: '2I' } },
  { date: '2026-06-30', time: '21:00', round: 'Round of 32', home: { seed: '1I' },                                         away: { seed: '3rd C/D/F/G/H' } },
  { date: '2026-07-01', time: '01:00', round: 'Round of 32', home: { seed: '1A', name: 'Mexico',    flag: '🇲🇽' },          away: { seed: '3rd C/E/F/H/I' } },
  { date: '2026-07-01', time: '16:00', round: 'Round of 32', home: { seed: '1L' },                                         away: { seed: '3rd E/H/I/J/K' } },
  { date: '2026-07-01', time: '20:00', round: 'Round of 32', home: { seed: '1G' },                                         away: { seed: '3rd A/E/H/I/J' } },
  { date: '2026-07-02', time: '00:00', round: 'Round of 32', home: { seed: '1D', name: 'USA',       flag: '🇺🇸' },          away: { seed: '3rd B/E/F/I/J' } },
  { date: '2026-07-02', time: '19:00', round: 'Round of 32', home: { seed: '1H' },                                         away: { seed: '2J' } },
  { date: '2026-07-02', time: '23:00', round: 'Round of 32', home: { seed: '2K' },                                         away: { seed: '2L' } },
  { date: '2026-07-03', time: '03:00', round: 'Round of 32', home: { seed: '1B' },                                         away: { seed: '3rd E/F/G/I/J' } },
  { date: '2026-07-03', time: '18:00', round: 'Round of 32', home: { seed: '2D' },                                         away: { seed: '2G' } },
  { date: '2026-07-03', time: '22:00', round: 'Round of 32', home: { seed: '1J', name: 'Argentina', flag: '🇦🇷' },          away: { seed: '2H' } },
  { date: '2026-07-04', time: '01:30', round: 'Round of 32', home: { seed: '1K' },                                         away: { seed: '3rd D/E/I/J/L' } },
];

type LaterFixture = { date: string; time: string; label: string; labelHe: string };

const LATER_FIXTURES: LaterFixture[] = [
  // Round of 16
  { date: '2026-07-04', time: '17:00', label: 'Round of 16', labelHe: 'שמינית גמר' },
  { date: '2026-07-04', time: '21:00', label: 'Round of 16', labelHe: 'שמינית גמר' },
  { date: '2026-07-05', time: '20:00', label: 'Round of 16', labelHe: 'שמינית גמר' },
  { date: '2026-07-06', time: '00:00', label: 'Round of 16', labelHe: 'שמינית גמר' },
  { date: '2026-07-06', time: '19:00', label: 'Round of 16', labelHe: 'שמינית גמר' },
  { date: '2026-07-07', time: '00:00', label: 'Round of 16', labelHe: 'שמינית גמר' },
  { date: '2026-07-07', time: '16:00', label: 'Round of 16', labelHe: 'שמינית גמר' },
  { date: '2026-07-07', time: '20:00', label: 'Round of 16', labelHe: 'שמינית גמר' },
  // Quarter Finals
  { date: '2026-07-09', time: '20:00', label: 'Quarter Final', labelHe: 'רבע גמר' },
  { date: '2026-07-10', time: '19:00', label: 'Quarter Final', labelHe: 'רבע גמר' },
  { date: '2026-07-11', time: '21:00', label: 'Quarter Final', labelHe: 'רבע גמר' },
  { date: '2026-07-12', time: '01:00', label: 'Quarter Final', labelHe: 'רבע גמר' },
  // Semi Finals
  { date: '2026-07-14', time: '19:00', label: 'Semi Final', labelHe: 'חצי גמר' },
  { date: '2026-07-15', time: '19:00', label: 'Semi Final', labelHe: 'חצי גמר' },
  // 3rd Place
  { date: '2026-07-18', time: '21:00', label: '3rd Place', labelHe: 'מקום שלישי' },
  // Final
  { date: '2026-07-19', time: '19:00', label: 'Final', labelHe: 'גמר' },
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

function KOTeamSlot({ team }: { team: KOTeam }) {
  if (team.name) {
    return (
      <div className="match-card__team">
        <span className="match-card__flag">{team.flag}</span>
        <span className="match-card__team-name">{team.name}</span>
      </div>
    );
  }
  return (
    <div className="match-card__team">
      <span className="match-card__flag match-card__flag--tbd">?</span>
      <span className="match-card__team-name match-card__team-name--tbd">{team.seed}</span>
    </div>
  );
}

function KOTeamSlotAway({ team }: { team: KOTeam }) {
  if (team.name) {
    return (
      <div className="match-card__team match-card__team--away">
        <span className="match-card__flag">{team.flag}</span>
        <span className="match-card__team-name">{team.name}</span>
      </div>
    );
  }
  return (
    <div className="match-card__team match-card__team--away">
      <span className="match-card__flag match-card__flag--tbd">?</span>
      <span className="match-card__team-name match-card__team-name--tbd">{team.seed}</span>
    </div>
  );
}

function KnockoutSection({ isHe, lang }: { isHe: boolean; lang: string }) {
  // Group R32 fixtures by IDT date (some UTC times cross midnight into the next IDT day)
  const byDate = R32.reduce<Record<string, KOFixture[]>>((acc, f) => {
    const idtDate = toIDTDate(f.date, f.time);
    (acc[idtDate] ??= []).push(f);
    return acc;
  }, {});
  const r32Dates = Object.keys(byDate).sort();

  const fmtDate = (d: string) =>
    new Date(d + 'T12:00:00').toLocaleDateString(isHe ? 'he-IL' : 'en-US', {
      weekday: 'long', month: 'long', day: 'numeric',
    });

  // Group later fixtures by round label, preserving round order
  const roundOrder = ['Round of 16', 'Quarter Final', 'Semi Final', '3rd Place', 'Final'];
  const roundLabelHe: Record<string, string> = {
    'Round of 16': 'שמינית גמר',
    'Quarter Final': 'רבע גמר',
    'Semi Final': 'חצי גמר',
    '3rd Place': 'מקום שלישי',
    'Final': 'גמר',
  };
  const byRound = LATER_FIXTURES.reduce<Record<string, LaterFixture[]>>((acc, f) => {
    (acc[f.label] ??= []).push(f);
    return acc;
  }, {});

  return (
    <section className="knockout-section">
      <div className="knockout-section__header">
        <span className="knockout-section__title">{isHe ? 'שלבי הנוקאאוט' : 'Knockout Stage'}</span>
      </div>

      {/* Round of 32 — exact dates and matchups */}
      <div className="ko-round-label">{isHe ? 'שלב 32' : 'Round of 32'}</div>
      {r32Dates.map(date => (
        <section key={date} className="explorer__date-section">
          <div className="explorer__date-header">
            <span className={`explorer__date-label${isHe ? ' explorer__date-label--hebrew' : ''}`} dir={isHe ? 'rtl' : undefined}>
              {fmtDate(date)}
            </span>
          </div>
          {byDate[date].map((f, i) => (
            <div key={i} className="match-card match-card--tbd glass-card">
              <KOTeamSlot team={f.home} />
              <div className="match-card__center">
                <span className="match-card__kickoff match-card__kickoff--tbd">{toIDT(f.date, f.time)} IDT</span>
                <span className="match-card__meta">{isHe ? 'שלב 32' : 'Round of 32'}</span>
              </div>
              <KOTeamSlotAway team={f.away} />
            </div>
          ))}
        </section>
      ))}

      {/* Later rounds — TBD teams, exact times */}
      {roundOrder.map(round => {
        const fixtures = byRound[round] ?? [];
        const byDateLater = fixtures.reduce<Record<string, LaterFixture[]>>((acc, f) => {
          const idtDate = toIDTDate(f.date, f.time);
          (acc[idtDate] ??= []).push(f);
          return acc;
        }, {});
        const dates = Object.keys(byDateLater).sort();
        return (
          <div key={round}>
            <div className="ko-round-label">{isHe ? roundLabelHe[round] : round}</div>
            {dates.map(date => (
              <section key={date} className="explorer__date-section">
                <div className="explorer__date-header">
                  <span className={`explorer__date-label${isHe ? ' explorer__date-label--hebrew' : ''}`} dir={isHe ? 'rtl' : undefined}>
                    {fmtDate(date)}
                  </span>
                </div>
                {byDateLater[date].map((f, i) => (
                  <div key={i} className="match-card match-card--tbd glass-card">
                    <div className="match-card__team">
                      <span className="match-card__flag match-card__flag--tbd">?</span>
                      <span className="match-card__team-name match-card__team-name--tbd">TBD</span>
                    </div>
                    <div className="match-card__center">
                      <span className="match-card__kickoff match-card__kickoff--tbd">{toIDT(f.date, f.time)} IDT</span>
                      <span className="match-card__meta">{isHe ? f.labelHe : f.label}</span>
                    </div>
                    <div className="match-card__team match-card__team--away">
                      <span className="match-card__flag match-card__flag--tbd">?</span>
                      <span className="match-card__team-name match-card__team-name--tbd">TBD</span>
                    </div>
                  </div>
                ))}
              </section>
            ))}
          </div>
        );
      })}
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
