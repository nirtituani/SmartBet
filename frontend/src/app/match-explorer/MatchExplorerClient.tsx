'use client';

import React from 'react';
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
type KOFixture = { id?: number; date: string; time: string; home: KOTeam; away: KOTeam; round: string };

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
  { id: 73, date: '2026-06-28', time: '19:00', round: 'Round of 32', home: { seed: '2A', name: 'South Africa',        flag: '🇿🇦' }, away: { seed: '2B',       name: 'Canada',               flag: '🇨🇦' } },
  { id: 74, date: '2026-06-29', time: '17:00', round: 'Round of 32', home: { seed: '1C', name: 'Brazil',              flag: '🇧🇷' }, away: { seed: '2F',       name: 'Japan',                flag: '🇯🇵' } },
  { id: 75, date: '2026-06-29', time: '20:30', round: 'Round of 32', home: { seed: '1E', name: 'Germany',             flag: '🇩🇪' }, away: { seed: '3rd',      name: 'Paraguay',             flag: '🇵🇾' } },
  { id: 76, date: '2026-06-30', time: '01:00', round: 'Round of 32', home: { seed: '1F', name: 'Netherlands',         flag: '🇳🇱' }, away: { seed: '2C',       name: 'Morocco',              flag: '🇲🇦' } },
  { id: 77, date: '2026-06-30', time: '17:00', round: 'Round of 32', home: { seed: '2E', name: 'Ivory Coast',         flag: '🇨🇮' }, away: { seed: '2I',       name: 'Norway',               flag: '🇳🇴' } },
  { id: 78, date: '2026-06-30', time: '21:00', round: 'Round of 32', home: { seed: '1I', name: 'France',              flag: '🇫🇷' }, away: { seed: '3rd',      name: 'Sweden',               flag: '🇸🇪' } },
  { id: 79, date: '2026-07-01', time: '01:00', round: 'Round of 32', home: { seed: '1A', name: 'Mexico',              flag: '🇲🇽' }, away: { seed: '3rd C/E',  name: 'Ecuador',              flag: '🇪🇨' } },
  { id: 80, date: '2026-07-01', time: '16:00', round: 'Round of 32', home: { seed: '1L', name: 'England',             flag: '🏴󠁧󠁢󠁥󠁮󠁧󠁿' }, away: { seed: '3rd I/J/K', name: 'DR Congo',             flag: '🇨🇩' } },
  { id: 81, date: '2026-07-01', time: '20:00', round: 'Round of 32', home: { seed: '1G', name: 'Belgium',             flag: '🇧🇪' }, away: { seed: '3rd A/I/J', name: 'Senegal',              flag: '🇸🇳' } },
  { id: 82, date: '2026-07-02', time: '00:00', round: 'Round of 32', home: { seed: '1D', name: 'USA',                 flag: '🇺🇸' }, away: { seed: '3rd',      name: 'Bosnia & Herzegovina', flag: '🇧🇦' } },
  { id: 83, date: '2026-07-02', time: '19:00', round: 'Round of 32', home: { seed: '1H', name: 'Spain',               flag: '🇪🇸' }, away: { seed: '2J',       name: 'Austria',              flag: '🇦🇹' } },
  { id: 84, date: '2026-07-02', time: '23:00', round: 'Round of 32', home: { seed: '2K', name: 'Portugal',            flag: '🇵🇹' }, away: { seed: '2L',       name: 'Croatia',              flag: '🇭🇷' } },
  { id: 85, date: '2026-07-03', time: '03:00', round: 'Round of 32', home: { seed: '1B', name: 'Switzerland',         flag: '🇨🇭' }, away: { seed: '3rd G/J',  name: 'Algeria',              flag: '🇩🇿' } },
  { id: 86, date: '2026-07-03', time: '18:00', round: 'Round of 32', home: { seed: '2D', name: 'Australia',           flag: '🇦🇺' }, away: { seed: '2G',       name: 'Egypt',                flag: '🇪🇬' } },
  { id: 87, date: '2026-07-03', time: '22:00', round: 'Round of 32', home: { seed: '1J', name: 'Argentina',           flag: '🇦🇷' }, away: { seed: '2H',       name: 'Cape Verde',           flag: '🇨🇻' } },
  { id: 88, date: '2026-07-04', time: '01:30', round: 'Round of 32', home: { seed: '1K', name: 'Colombia',            flag: '🇨🇴' }, away: { seed: '3rd E/I/L', name: 'Ghana',               flag: '🇬🇭' } },
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

// R16 matchups in LATER_FIXTURES order: each entry is [homeR32Id, awayR32Id]
// Mirrors the bracket structure (LEFT_SEEDS/RIGHT_SEEDS pairs feed alternating R16 slots)
const R16_PAIRINGS: [number, number][] = [
  [75, 78], // 07-04 17:00 — winner Germany/Paraguay vs winner France/Sweden
  [74, 77], // 07-04 21:00 — winner Brazil/Japan vs winner Ivory Coast/Norway
  [73, 76], // 07-05 20:00 — winner S.Africa/Canada vs winner Netherlands/Morocco
  [79, 80], // 07-06 00:00 — winner Mexico/Ecuador vs winner England/DR Congo
  [84, 83], // 07-06 19:00 — winner Portugal/Croatia vs winner Spain/Austria
  [87, 86], // 07-07 00:00 — winner Argentina/Cape Verde vs winner Australia/Egypt
  [82, 81], // 07-07 16:00 — winner USA/Bosnia vs winner Belgium/Senegal
  [85, 88], // 07-07 20:00 — winner Switzerland/Algeria vs winner Colombia/Ghana
];

// QF matchups in LATER_FIXTURES order: each entry is [homeR16Idx, awayR16Idx] (index into R16_PAIRINGS)
const QF_FROM_R16: [number, number][] = [
  [0, 2], // 07-09 20:00 — R16[0] winner vs R16[2] winner (left bracket)
  [1, 3], // 07-10 19:00 — R16[1] winner vs R16[3] winner (right bracket)
  [4, 6], // 07-11 21:00 — R16[4] winner vs R16[6] winner (left bracket)
  [5, 7], // 07-12 01:00 — R16[5] winner vs R16[7] winner (right bracket)
];

// SF matchups: each entry is [homeQFIdx, awayQFIdx]
const SF_FROM_QF: [number, number][] = [
  [0, 2], // 07-14 19:00 — QF[0] winner vs QF[2] winner (left SF)
  [1, 3], // 07-15 19:00 — QF[1] winner vs QF[3] winner (right SF)
];

function KnockoutSection({ isHe, lang, r32Scores, progressBar }: {
  isHe: boolean; lang: string; r32Scores: Record<number, Match>; progressBar?: React.ReactNode;
}) {
  // Derive R32 winners from live scores
  const r32ById: Record<number, KOFixture> = {};
  for (const f of R32) { if (f.id) r32ById[f.id] = f; }
  const r32Winners: Record<number, KOTeam | null> = {};
  for (const [idStr, m] of Object.entries(r32Scores)) {
    const id = Number(idStr);
    const f = r32ById[id];
    if (!f || m.status !== 'finished' || m.score_home === null || m.score_away === null) continue;
    if (m.score_home > m.score_away) r32Winners[id] = f.home;
    else if (m.score_away > m.score_home) r32Winners[id] = f.away;
    // Tied after AET — decided by penalties; ESPN sets winner field
    else if (m.winner === 'home') r32Winners[id] = f.home;
    else if (m.winner === 'away') r32Winners[id] = f.away;
    else r32Winners[id] = null;
  }

  // Build R16 team pairs keyed by "date-time" matching LATER_FIXTURES
  const r16Fixtures = LATER_FIXTURES.filter(f => f.label === 'Round of 16');
  const r16TeamsMap: Record<string, { home: KOTeam | null; away: KOTeam | null }> = {};
  R16_PAIRINGS.forEach(([homeId, awayId], i) => {
    const f = r16Fixtures[i];
    if (f) r16TeamsMap[`${f.date}-${f.time}`] = { home: r32Winners[homeId] ?? null, away: r32Winners[awayId] ?? null };
  });

  // Build QF team pairs — derive from R16 winners (will populate once R16 results exist)
  // r16Winners[i] = winner of R16 match i, derived from backend R16 fixture scores (future)
  const r16Winners: (KOTeam | null)[] = Array(8).fill(null); // populated when R16 scores available
  const qfFixtures = LATER_FIXTURES.filter(f => f.label === 'Quarter Final');
  const qfTeamsMap: Record<string, { home: KOTeam | null; away: KOTeam | null }> = {};
  QF_FROM_R16.forEach(([homeIdx, awayIdx], i) => {
    const f = qfFixtures[i];
    if (f) qfTeamsMap[`${f.date}-${f.time}`] = { home: r16Winners[homeIdx], away: r16Winners[awayIdx] };
  });

  // Build SF team pairs — derive from QF winners (future)
  const qfWinners: (KOTeam | null)[] = Array(4).fill(null);
  const sfFixtures = LATER_FIXTURES.filter(f => f.label === 'Semi Final');
  const sfTeamsMap: Record<string, { home: KOTeam | null; away: KOTeam | null }> = {};
  SF_FROM_QF.forEach(([homeIdx, awayIdx], i) => {
    const f = sfFixtures[i];
    if (f) sfTeamsMap[`${f.date}-${f.time}`] = { home: qfWinners[homeIdx], away: qfWinners[awayIdx] };
  });

  const teamsForRound: Record<string, Record<string, { home: KOTeam | null; away: KOTeam | null }>> = {
    'Round of 16':  r16TeamsMap,
    'Quarter Final': qfTeamsMap,
    'Semi Final':   sfTeamsMap,
  };

  // Group R32 fixtures by IDT date (some UTC times cross midnight into the next IDT day)
  const byDate = R32.reduce<Record<string, KOFixture[]>>((acc, f) => {
    const idtDate = toIDTDate(f.date, f.time);
    (acc[idtDate] ??= []).push(f);
    return acc;
  }, {});
  const r32Dates = Object.keys(byDate).sort();
  // A date group goes before the progress bar only if every match in it is finished
  const r32PastDates = r32Dates.filter(d =>
    byDate[d].every(f => f.id ? r32Scores[f.id]?.status === 'finished' : false)
  );
  const r32UpcomingDates = r32Dates.filter(d => !r32PastDates.includes(d));

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

      {/* Round of 32 — split into past and upcoming, with progress bar between */}
      <div className="ko-round-label">{isHe ? 'שלב 32' : 'Round of 32'}</div>
      {r32PastDates.map(date => (
        <section key={date} className="explorer__date-section">
          <div className="explorer__date-header">
            <span className={`explorer__date-label${isHe ? ' explorer__date-label--hebrew' : ''}`} dir={isHe ? 'rtl' : undefined}>
              {fmtDate(date)}
            </span>
          </div>
          {byDate[date].map((f, i) => {
            const live = f.id ? r32Scores[f.id] : undefined;
            const finished = live?.status === 'finished';
            const isLive = live?.status === 'live';
            const hasScore = live && live.score_home !== null && live.score_away !== null;
            const cardCls = `match-card glass-card${finished ? ' match-card--finished' : isLive ? ' match-card--live' : ' match-card--tbd'}`;
            const inner = (
              <>
                <KOTeamSlot team={f.home} />
                <div className="match-card__center">
                  {hasScore ? (
                    <span className={`match-card__score${isLive ? ' match-card__score--live' : ''}`}>
                      {live!.score_home} – {live!.score_away}
                    </span>
                  ) : (
                    <span className="match-card__kickoff match-card__kickoff--tbd">{toIDT(f.date, f.time)} IDT</span>
                  )}
                  <span className="match-card__meta">
                    {isLive && <span className="match-card__live-dot" />}
                    {isHe ? 'שלב 32' : 'Round of 32'}
                  </span>
                </div>
                <KOTeamSlotAway team={f.away} />
              </>
            );
            return f.id ? (
              <Link key={i} href={`/match/${f.id}`} id={`r32-${f.date}-${f.time.replace(':', '')}`} className={cardCls}>
                {inner}
              </Link>
            ) : (
              <div key={i} id={`r32-${f.date}-${f.time.replace(':', '')}`} className={cardCls}>
                {inner}
              </div>
            );
          })}
        </section>
      ))}

      {progressBar}

      {r32UpcomingDates.map(date => (
        <section key={date} className="explorer__date-section">
          <div className="explorer__date-header">
            <span className={`explorer__date-label${isHe ? ' explorer__date-label--hebrew' : ''}`} dir={isHe ? 'rtl' : undefined}>
              {fmtDate(date)}
            </span>
          </div>
          {byDate[date].map((f, i) => {
            const live = f.id ? r32Scores[f.id] : undefined;
            const finished = live?.status === 'finished';
            const isLive = live?.status === 'live';
            const hasScore = live && live.score_home !== null && live.score_away !== null;
            const cardCls = `match-card glass-card${finished ? ' match-card--finished' : isLive ? ' match-card--live' : ' match-card--tbd'}`;
            const inner = (
              <>
                <KOTeamSlot team={f.home} />
                <div className="match-card__center">
                  {hasScore ? (
                    <span className={`match-card__score${isLive ? ' match-card__score--live' : ''}`}>
                      {live!.score_home} – {live!.score_away}
                    </span>
                  ) : (
                    <span className="match-card__kickoff match-card__kickoff--tbd">{toIDT(f.date, f.time)} IDT</span>
                  )}
                  <span className="match-card__meta">
                    {isLive && <span className="match-card__live-dot" />}
                    {isHe ? 'שלב 32' : 'Round of 32'}
                  </span>
                </div>
                <KOTeamSlotAway team={f.away} />
              </>
            );
            return f.id ? (
              <Link key={i} href={`/match/${f.id}`} id={`r32-${f.date}-${f.time.replace(':', '')}`} className={cardCls}>
                {inner}
              </Link>
            ) : (
              <div key={i} id={`r32-${f.date}-${f.time.replace(':', '')}`} className={cardCls}>
                {inner}
              </div>
            );
          })}
        </section>
      ))}

      {/* Later rounds — TBD teams, exact times */}
      {roundOrder.map(round => {
        const fixtures = byRound[round] ?? [];
        const roundSlug = round.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
        const byDateLater = fixtures.reduce<Record<string, LaterFixture[]>>((acc, f) => {
          const idtDate = toIDTDate(f.date, f.time);
          (acc[idtDate] ??= []).push(f);
          return acc;
        }, {});
        const dates = Object.keys(byDateLater).sort();
        return (
          <div key={round}>
            <div id={`ko-${roundSlug}`} className="ko-round-label">{isHe ? roundLabelHe[round] : round}</div>
            {dates.map(date => (
              <section key={date} className="explorer__date-section">
                <div className="explorer__date-header">
                  <span className={`explorer__date-label${isHe ? ' explorer__date-label--hebrew' : ''}`} dir={isHe ? 'rtl' : undefined}>
                    {fmtDate(date)}
                  </span>
                </div>
                {byDateLater[date].map((f, i) => {
                  const teams = teamsForRound[round]?.[`${f.date}-${f.time}`];
                  const homeTeam: KOTeam = teams?.home ?? { seed: 'TBD' };
                  const awayTeam: KOTeam = teams?.away ?? { seed: 'TBD' };
                  return (
                    <div key={i} id={`ko-${roundSlug}-${f.date}-${f.time.replace(':', '')}`} className="match-card match-card--tbd glass-card">
                      <KOTeamSlot team={homeTeam} />
                      <div className="match-card__center">
                        <span className="match-card__kickoff match-card__kickoff--tbd">{toIDT(f.date, f.time)} IDT</span>
                        <span className="match-card__meta">{isHe ? f.labelHe : f.label}</span>
                      </div>
                      <KOTeamSlotAway team={awayTeam} />
                    </div>
                  );
                })}
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
  const knockoutRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchUpcomingMatches().then(setMatches).catch(() => {});
  }, []);

  // Only group stage matches in the main list — KO matches are shown in KnockoutSection
  const groupStageMatches = matches.filter(m => m.group.startsWith('Group '));
  const finishedMatches = groupStageMatches.filter(m => m.status === 'finished');
  const upcomingMatches = groupStageMatches.filter(m => m.status !== 'finished');

  useEffect(() => {
    const hash = window.location.hash.slice(1);
    if (hash) {
      const el = document.getElementById(hash);
      if (el) {
        const y = el.getBoundingClientRect().top + window.scrollY - 80;
        window.scrollTo({ top: y, behavior: 'smooth' });
      }
      return;
    }
    // R32 started June 28 — once knockout is underway, scroll there instead of group stage
    const knockoutStarted = new Date() >= new Date('2026-06-28T00:00:00Z');
    if (knockoutStarted && knockoutRef.current) {
      const y = knockoutRef.current.getBoundingClientRect().top + window.scrollY - 80;
      window.scrollTo({ top: y, behavior: 'smooth' });
    } else if (upcomingRef.current) {
      const y = upcomingRef.current.getBoundingClientRect().top + window.scrollY - 80;
      window.scrollTo({ top: y, behavior: 'smooth' });
    }
  }, []);

  const r32Scores: Record<number, Match> = {};
  for (const m of matches) {
    if (m.group === 'Round of 32') r32Scores[m.id] = m;
  }

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

      {futureDates.length > 0 && (
        <div ref={upcomingRef}>
          <TournamentProgress matches={matches} lang={lang} />
        </div>
      )}

      {futureDates.map(d => renderDateSection(d, groupedFuture))}

      <div ref={knockoutRef}>
        <KnockoutSection
          isHe={lang === 'he'}
          lang={lang}
          r32Scores={r32Scores}
          progressBar={
            futureDates.length === 0 ? (
              <div ref={upcomingRef}>
                <TournamentProgress matches={matches} lang={lang} />
              </div>
            ) : undefined
          }
        />
      </div>
    </main>
  );
}
