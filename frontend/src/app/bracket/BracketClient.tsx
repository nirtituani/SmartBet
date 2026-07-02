'use client';

import Link from 'next/link';
import { useEffect } from 'react';
import { useLanguage } from '@/contexts/LanguageContext';
import { translateTeam } from '@/lib/i18n';
import type { Lang } from '@/lib/i18n';

type TeamData = { name: string; flag: string };
type Slot = { label: string; team: TeamData | null };
type MatchResult = { topScore: number | null; bottomScore: number | null; status: string; winner?: string | null };
type BracketMatch = { top: Slot; bottom: Slot; result?: MatchResult };

export type ThirdPlaceTeam = {
  name: string; flag: string; group: string;
  pts: number; gd: number; gf: number; ga: number;
  mp: number; w: number; d: number; l: number;
  fifa_rank: number;
  fair_play: number;
};

export type R32Result = { homeScore: number | null; awayScore: number | null; status: string; winner: string | null };

interface Props {
  standings: Record<string, (TeamData | null)[]>;
  thirdPlace: ThirdPlaceTeam[];
  r32Results: Record<string, R32Result>;
}

// Layout constants
const SLOT_H = 71;
const CARD_W = 175;
const CARD_H = 58;
const CONN_W = 33;
const FINAL_CONN_W = 48;
const TOTAL_H = 8 * SLOT_H;
// bk-round-label height (16px) + margin-bottom (8px) — connectors must skip this
const LABEL_H = 24;

function cy(r: number, i: number) {
  const m = Math.pow(2, r);
  return i * SLOT_H * m + (SLOT_H * m) / 2;
}

const LEFT_SEEDS: [string, string][] = [
  ['1E', '3ABCDF'], ['1I', '3CDFGH'],
  ['2A', '2B'],     ['1F', '2C'],
  ['2K', '2L'],     ['1H', '2J'],
  ['1D', '3BEFIJ'], ['1G', '3AEHIJ'],
];
const RIGHT_SEEDS: [string, string][] = [
  ['1C', '2F'],      ['2E', '2I'],
  ['1A', '3CEFHI'],  ['1L', '3EHIJK'],
  ['1J', '2H'],      ['2D', '2G'],
  ['1B', '3EFGIJ'],  ['1K', '3DEIJL'],
];

// Hardcoded from the official FIFA WC 2026 bracket draw — not derivable from rankings
const THIRD_PLACE_SLOTS: Record<string, { name: string; flag: string } | null> = {
  '3ABCDF': { name: 'Paraguay',             flag: '🇵🇾' },
  '3CDFGH': { name: 'Sweden',               flag: '🇸🇪' },
  '3BEFIJ': { name: 'Bosnia & Herzegovina', flag: '🇧🇦' },
  '3AEHIJ': { name: 'Senegal',              flag: '🇸🇳' },
  '3CEFHI': { name: 'Ecuador',              flag: '🇪🇨' },
  '3EHIJK': { name: 'DR Congo',             flag: '🇨🇩' },
  '3EFGIJ': { name: 'Algeria',              flag: '🇩🇿' },
  '3DEIJL': { name: 'Ghana',                flag: '🇬🇭' },
};

const ROUND_LABELS = ['Round of 32', 'Round of 16', 'Quarter Finals', 'Semi Finals'];

// Maps "topSeed|bottomSeed" → exact match anchor id in match explorer
// IDs are r32-{utcDate}-{utcTime no colon}
const R32_ANCHOR: Record<string, string> = {
  '2A|2B':     'r32-2026-06-28-1900',
  '1C|2F':     'r32-2026-06-29-1700',
  '1E|3ABCDF': 'r32-2026-06-29-2030',
  '1F|2C':     'r32-2026-06-30-0100',
  '2E|2I':     'r32-2026-06-30-1700',
  '1I|3CDFGH': 'r32-2026-06-30-2100',
  '1A|3CEFHI': 'r32-2026-07-01-0100',
  '1L|3EHIJK': 'r32-2026-07-01-1600',
  '1G|3AEHIJ': 'r32-2026-07-01-2000',
  '1D|3BEFIJ': 'r32-2026-07-02-0000',
  '1H|2J':     'r32-2026-07-02-1900',
  '2K|2L':     'r32-2026-07-02-2300',
  '1B|3EFGIJ': 'r32-2026-07-03-0300',
  '2D|2G':     'r32-2026-07-03-1800',
  '1J|2H':     'r32-2026-07-03-2200',
  '1K|3DEIJL': 'r32-2026-07-04-0130',
};

// Maps "topSeed|bottomSeed" → fixture ID — used to assign ids to R32 bracket cards
const SEED_PAIR_TO_ID: Record<string, number> = {
  '1E|3ABCDF': 75, '1I|3CDFGH': 78, '2A|2B': 73,     '1F|2C': 76,
  '2K|2L':     84, '1H|2J':     83, '1D|3BEFIJ': 82, '1G|3AEHIJ': 81,
  '1C|2F':     74, '2E|2I':     77, '1A|3CEFHI': 79, '1L|3EHIJK': 80,
  '1J|2H':     87, '2D|2G':     86, '1B|3EFGIJ': 85, '1K|3DEIJL': 88,
};

// Per-slot hrefs for later rounds.
// Left side of bracket gets earlier fixtures; right side gets later ones.
// Anchor IDs match ko-{roundSlug}-{utcDate}-{utcTime no colon} in the explorer.
// FIFA schedules knockout rounds alternating left/right bracket halves each match.
// Matches 1,3,5,7 → left bracket; matches 2,4,6,8 → right bracket.
const LEFT_SLOT_HREFS: Record<number, string[]> = {
  1: [ // Round of 16 — left bracket slots: L0=Germany/France, L1=Canada/Morocco, L2=Portugal/Spain, L3=USA/Belgium
    '/match-explorer#ko-round-of-16-2026-07-04-2100',
    '/match-explorer#ko-round-of-16-2026-07-04-1700',
    '/match-explorer#ko-round-of-16-2026-07-06-1900',
    '/match-explorer#ko-round-of-16-2026-07-07-0000',
  ],
  2: [ // Quarter Finals — matches 1,3 go to left bracket
    '/match-explorer#ko-quarter-final-2026-07-09-2000',
    '/match-explorer#ko-quarter-final-2026-07-11-2100',
  ],
  3: [ // Semi Final — first SF → left bracket
    '/match-explorer#ko-semi-final-2026-07-14-1900',
  ],
};

const RIGHT_SLOT_HREFS: Record<number, string[]> = {
  1: [ // Round of 16 — right bracket slots: R0=Brazil/Norway, R1=Mexico/England, R2=Argentina, R3=Switzerland/Colombia
    '/match-explorer#ko-round-of-16-2026-07-05-2000',
    '/match-explorer#ko-round-of-16-2026-07-06-0000',
    '/match-explorer#ko-round-of-16-2026-07-07-1600',
    '/match-explorer#ko-round-of-16-2026-07-07-2000',
  ],
  2: [ // Quarter Finals — matches 2,4 go to right bracket
    '/match-explorer#ko-quarter-final-2026-07-10-1900',
    '/match-explorer#ko-quarter-final-2026-07-12-0100',
  ],
  3: [ // Semi Final — second SF → right bracket
    '/match-explorer#ko-semi-final-2026-07-15-1900',
  ],
};


function sortThirdPlace(teams: ThirdPlaceTeam[]): ThirdPlaceTeam[] {
  return [...teams].sort(
    (a, b) => b.pts - a.pts || b.gd - a.gd || b.gf - a.gf || b.fair_play - a.fair_play || a.fifa_rank - b.fifa_rank
  );
}

function makeSlot(label: string, standings: Record<string, (TeamData | null)[]>): Slot {
  if (!label.startsWith('3') && label.length === 2) {
    const pos = parseInt(label[0]) - 1;
    return { label, team: standings[label[1]]?.[pos] ?? null };
  }
  if (label.startsWith('3')) {
    return { label, team: THIRD_PLACE_SLOTS[label] ?? null };
  }
  return { label, team: null };
}

const TBD: BracketMatch = {
  top:    { label: 'TBD', team: null },
  bottom: { label: 'TBD', team: null },
};
const tbds = (n: number): BracketMatch[] => Array(n).fill(TBD);

function getWinner(m: BracketMatch): Slot {
  const r = m.result;
  if (!r || r.status !== 'finished') return { label: 'TBD', team: null };
  if (r.topScore != null && r.bottomScore != null) {
    if (r.topScore > r.bottomScore) return m.top;
    if (r.bottomScore > r.topScore) return m.bottom;
    // Scores level after 90/120 min — penalty winner from ESPN
    if (r.winner === 'home') return m.top;
    if (r.winner === 'away') return m.bottom;
  }
  return { label: 'TBD', team: null };
}

function buildNextRound(matches: BracketMatch[]): BracketMatch[] {
  const result: BracketMatch[] = [];
  for (let i = 0; i < matches.length; i += 2) {
    result.push({ top: getWinner(matches[i]), bottom: getWinner(matches[i + 1]) });
  }
  return result;
}

// ── Sub-components ─────────────────────────────────────────────────────────────

function TeamRow({ s, score, isWinner, hasResult, lang }: {
  s: Slot; score?: number | null; isWinner?: boolean; hasResult?: boolean; lang: Lang;
}) {
  if (s.team) {
    let cls = 'bk-team bk-team--qualified';
    if (hasResult) cls = isWinner ? 'bk-team bk-team--winner' : 'bk-team bk-team--loser';
    return (
      <div className={cls}>
        <span className="bk-flag">{s.team.flag}</span>
        <span className="bk-name">{translateTeam(s.team.name, lang)}</span>
        {score != null && <span className="bk-score">{score}</span>}
      </div>
    );
  }
  return (
    <div className="bk-team bk-team--tbd">
      <span className="bk-seed">{s.label}</span>
    </div>
  );
}

function MatchCard({ m, centerY, lang, href, id }: { m: BracketMatch; centerY: number; lang: Lang; href?: string; id?: string }) {
  const style = { top: centerY - CARD_H / 2, width: CARD_W };
  const r = m.result;
  const hasResult = r?.status === 'finished' || r?.status === 'live';
  const topWinner = hasResult && r!.topScore != null && r!.bottomScore != null && r!.topScore > r!.bottomScore;
  const bottomWinner = hasResult && r!.topScore != null && r!.bottomScore != null && r!.bottomScore > r!.topScore;
  const live = r?.status === 'live';
  const inner = (
    <>
      <TeamRow s={m.top} score={r?.topScore} isWinner={topWinner} hasResult={hasResult} lang={lang} />
      <div className="bk-sep" />
      <TeamRow s={m.bottom} score={r?.bottomScore} isWinner={bottomWinner} hasResult={hasResult} lang={lang} />
    </>
  );
  const extraCls = live ? ' bk-card--live' : '';
  if (href) {
    return <Link id={id} href={href} className={`bk-card bk-card--link${extraCls}`} style={style}>{inner}</Link>;
  }
  return <div id={id} className={`bk-card${extraCls}`} style={style}>{inner}</div>;
}

function RoundCol({ matches, round, lang, label, seeds, slotHrefs }: {
  matches: BracketMatch[]; round: number; lang: Lang; label?: string;
  seeds?: [string, string][]; slotHrefs?: string[];
}) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 0 }}>
      {label && <div className="bk-round-label">{label}</div>}
      <div style={{ width: CARD_W, height: TOTAL_H, position: 'relative', flexShrink: 0 }}>
        {matches.map((m, i) => {
          const pair = seeds?.[i];
          const href = pair
            ? `/match-explorer#${R32_ANCHOR[`${pair[0]}|${pair[1]}`]}`
            : slotHrefs?.[i];
          const fixtureId = pair ? SEED_PAIR_TO_ID[`${pair[0]}|${pair[1]}`] : undefined;
          const anchorFromHref = !pair && slotHrefs?.[i] ? slotHrefs[i].split('#')[1] : undefined;
          const cardId = fixtureId ? `bk-r32-${fixtureId}` : anchorFromHref ? `bk-${anchorFromHref}` : undefined;
          return <MatchCard key={i} m={m} centerY={cy(round, i)} lang={lang} href={href} id={cardId} />;
        })}
      </div>
    </div>
  );
}

function Connector({ fromRound, flip, color }: { fromRound: number; flip?: boolean; color?: string }) {
  const pairs = (8 / Math.pow(2, fromRound)) / 2;
  const mid = CONN_W / 2;
  const stroke = color ?? 'rgba(99,179,237,0.3)';
  const lines: { x1: number; y1: number; x2: number; y2: number; key: string }[] = [];
  for (let i = 0; i < pairs; i++) {
    const uY = cy(fromRound, i * 2);
    const lY = cy(fromRound, i * 2 + 1);
    const nY = cy(fromRound + 1, i);
    lines.push(
      { key: `u${i}`, x1: 0, y1: uY, x2: mid, y2: uY },
      { key: `l${i}`, x1: 0, y1: lY, x2: mid, y2: lY },
      { key: `v${i}`, x1: mid, y1: uY, x2: mid, y2: lY },
      { key: `e${i}`, x1: mid, y1: nY, x2: CONN_W, y2: nY },
    );
  }
  // paddingTop offsets the SVG by the label height so lines align with card centers
  return (
    <div style={{ paddingTop: LABEL_H, flexShrink: 0 }}>
      <svg
        width={CONN_W} height={TOTAL_H}
        style={{ display: 'block', transform: flip ? 'scaleX(-1)' : undefined }}
      >
        {lines.map(({ key, ...p }) => (
          <line key={key} stroke={stroke} strokeWidth={1} fill="none" {...p} />
        ))}
      </svg>
    </div>
  );
}

function FinalConnector({ flip }: { flip?: boolean }) {
  const sfY = cy(3, 0);
  return (
    <div style={{ paddingTop: LABEL_H, flexShrink: 0 }}>
      <svg
        width={FINAL_CONN_W} height={TOTAL_H}
        style={{ display: 'block', transform: flip ? 'scaleX(-1)' : undefined }}
      >
        <line
          x1={0} y1={sfY} x2={FINAL_CONN_W} y2={sfY}
          stroke="rgba(246,201,14,0.5)" strokeWidth={1.5} fill="none"
        />
      </svg>
    </div>
  );
}

function ThirdPlaceTable({ teams, lang }: { teams: ThirdPlaceTeam[]; lang: Lang }) {
  const sorted = sortThirdPlace(teams);
  const isHe = lang === 'he';
  const emptyCount = Math.max(0, 12 - sorted.length);

  return (
    <section className="tp-section">
      <h2 className="tp-title">
        {isHe ? 'דירוג מקומות שלישיים — 8 הטובים עוברים' : '3rd Place Rankings — Best 8 Advance'}
      </h2>
      <div className="glass-card tp-card">
        <table className="standings-table">
          <thead>
            <tr>
              <th className="standings-table__pos">#</th>
              <th className="standings-table__team">{isHe ? 'נבחרת' : 'Team'}</th>
              <th>Grp</th>
              <th>MP</th>
              <th>W</th>
              <th>D</th>
              <th>L</th>
              <th>GF</th>
              <th>GA</th>
              <th>GD</th>
              <th className="standings-table__pts">Pts</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((t, i) => (
              <tr
                key={t.group}
                className={[
                  i < 8 ? 'standings-table__qualify' : '',
                  i === 8 ? 'tp-row--cutoff' : '',
                ].filter(Boolean).join(' ') || undefined}
              >
                <td className="standings-table__pos">{i + 1}</td>
                <td className="standings-table__team">
                  <div className="standings-table__team-cell">
                    <span className="standings-table__flag">{t.flag}</span>
                    <span className="standings-table__name">{translateTeam(t.name, lang)}</span>
                  </div>
                </td>
                <td>{t.group}</td>
                <td>{t.mp}</td>
                <td>{t.w}</td>
                <td>{t.d}</td>
                <td>{t.l}</td>
                <td>{t.gf}</td>
                <td>{t.ga}</td>
                <td>{t.gd === 0 ? '0' : t.gd > 0 ? `+${t.gd}` : t.gd}</td>
                <td className="standings-table__pts">{t.pts}</td>
              </tr>
            ))}
            {Array.from({ length: emptyCount }, (_, i) => (
              <tr key={`empty-${i}`} className={sorted.length + i === 8 ? 'tp-row--cutoff' : undefined}>
                <td className="standings-table__pos">{sorted.length + i + 1}</td>
                <td colSpan={10} className="tp-tbd-cell">
                  {isHe ? 'ממתין לתוצאות' : 'Awaiting results'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

// ── Main component ──────────────────────────────────────────────────────────────

export default function BracketClient({ standings, thirdPlace, r32Results }: Props) {
  const { lang } = useLanguage();
  const l = lang as Lang;

  useEffect(() => {
    const hash = window.location.hash.slice(1);
    if (!hash.startsWith('bk-')) return;
    requestAnimationFrame(() => {
      const el = document.getElementById(hash);
      if (!el) return;
      el.classList.add('bk-card--highlight');
      setTimeout(() => el.classList.remove('bk-card--highlight'), 2000);
      const scrollContainer = el.closest('.bracket-scroll') as HTMLElement | null;
      if (scrollContainer) {
        const containerRect = scrollContainer.getBoundingClientRect();
        const elRect = el.getBoundingClientRect();
        const targetLeft = scrollContainer.scrollLeft + elRect.left - containerRect.left - containerRect.width / 2 + elRect.width / 2;
        scrollContainer.scrollLeft = Math.max(0, targetLeft);
      }
      const y = el.getBoundingClientRect().top + window.scrollY - 120;
      window.scrollTo({ top: Math.max(0, y), behavior: 'smooth' });
    });
  }, []);

  const leftR32 = LEFT_SEEDS.map(([a, b]) => {
    const top = makeSlot(a, standings);
    const bottom = makeSlot(b, standings);
    const key = top.team && bottom.team ? `${top.team.name}|${bottom.team.name}` : null;
    const r = key ? r32Results[key] : undefined;
    return { top, bottom, result: r ? { topScore: r.homeScore, bottomScore: r.awayScore, status: r.status, winner: r.winner } : undefined };
  });
  const rightR32 = RIGHT_SEEDS.map(([a, b]) => {
    const top = makeSlot(a, standings);
    const bottom = makeSlot(b, standings);
    const key = top.team && bottom.team ? `${top.team.name}|${bottom.team.name}` : null;
    const r = key ? r32Results[key] : undefined;
    return { top, bottom, result: r ? { topScore: r.homeScore, bottomScore: r.awayScore, status: r.status, winner: r.winner } : undefined };
  });

  const leftR16 = buildNextRound(leftR32);
  const leftQF  = buildNextRound(leftR16);
  const leftSF  = buildNextRound(leftQF);
  const rightR16 = buildNextRound(rightR32);
  const rightQF  = buildNextRound(rightR16);
  const rightSF  = buildNextRound(rightQF);

  const leftRounds  = [leftR32,  leftR16,  leftQF,  leftSF];
  const rightRounds = [rightR32, rightR16, rightQF, rightSF];

  const isHe = lang === 'he';

  return (
    <main className="bracket-page">
      <p className="bracket-page__breadcrumb">
        {isHe ? 'בית / עץ טורניר' : 'Home / Bracket'}
      </p>
      <h1 className="bracket-page__title">
        {isHe ? 'שלבי הנוקאאוט — גביע העולם 2026' : 'Knockout Stage — FIFA World Cup 2026'}
      </h1>

      <div className="bracket-scroll">
        <div className="bracket-track">

          {/* ── Left half (R32 → SF) ── */}
          {[0, 1, 2, 3].map(r => (
            <div key={`L${r}`} style={{ display: 'flex', alignItems: 'flex-start' }}>
              <RoundCol
                matches={leftRounds[r]}
                round={r}
                lang={l}
                label={ROUND_LABELS[r]}
                seeds={r === 0 ? LEFT_SEEDS : undefined}
                slotHrefs={r > 0 ? LEFT_SLOT_HREFS[r] : undefined}
              />
              {r < 3 && <Connector fromRound={r} />}
            </div>
          ))}

          {/* ── Final area ── */}
          <FinalConnector />
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <div className="bk-round-label bk-round-label--final">
              {isHe ? 'גמר' : 'Final'}
            </div>
            <div style={{ width: CARD_W, height: TOTAL_H, position: 'relative' }}>
              <MatchCard m={TBD} centerY={TOTAL_H / 2} lang={l} href="/match-explorer#ko-final" />
            </div>
          </div>
          <FinalConnector flip />

          {/* ── Right half (SF → R32) ── */}
          {[3, 2, 1, 0].map(r => (
            <div key={`R${r}`} style={{ display: 'flex', alignItems: 'flex-start' }}>
              {r < 3 && <Connector fromRound={r} flip />}
              <RoundCol
                matches={rightRounds[r]}
                round={r}
                lang={l}
                label={ROUND_LABELS[r]}
                seeds={r === 0 ? RIGHT_SEEDS : undefined}
                slotHrefs={r > 0 ? RIGHT_SLOT_HREFS[r] : undefined}
              />
            </div>
          ))}

        </div>
      </div>

      <ThirdPlaceTable teams={thirdPlace} lang={l} />
    </main>
  );
}
