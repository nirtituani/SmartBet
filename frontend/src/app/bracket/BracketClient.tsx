'use client';

import { useLanguage } from '@/contexts/LanguageContext';
import { translateTeam } from '@/lib/i18n';
import type { Lang } from '@/lib/i18n';

type TeamData = { name: string; flag: string };
type Slot = { label: string; team: TeamData | null };
type BracketMatch = { top: Slot; bottom: Slot };

export type ThirdPlaceTeam = {
  name: string; flag: string; group: string;
  pts: number; gd: number; gf: number; ga: number;
  mp: number; w: number; d: number; l: number;
  fifa_rank: number;
  fair_play: number;
};

interface Props {
  standings: Record<string, (TeamData | null)[]>;
  thirdPlace: ThirdPlaceTeam[];
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

const ALL_THIRD_SLOTS = [
  '3ABCDF', '3CDFGH', '3BEFIJ', '3AEHIJ',
  '3CEFHI', '3EHIJK', '3EFGIJ', '3DEIJL',
];

const ROUND_LABELS = ['Round of 32', 'Round of 16', 'Quarter Finals', 'Semi Finals'];

// Teams that have already secured their knockout-stage spot
const QUALIFIED_TEAMS = new Set([
  'Mexico',
  'USA',
  'Germany',
  'Argentina',
]);

function sortThirdPlace(teams: ThirdPlaceTeam[]): ThirdPlaceTeam[] {
  return [...teams].sort(
    (a, b) => b.pts - a.pts || b.gd - a.gd || b.gf - a.gf || b.fair_play - a.fair_play || a.fifa_rank - b.fifa_rank
  );
}

// MCV (most-constrained-variable) greedy: process the slot with fewest eligible
// qualified teams first to avoid impossible assignments later.
function resolveThirdPlace(teams: ThirdPlaceTeam[]): Map<string, TeamData | null> {
  const sorted = sortThirdPlace(teams);
  const qualifiedGroups = new Set(sorted.slice(0, 8).map(t => t.group));
  const result = new Map<string, TeamData | null>();
  const assigned = new Set<string>();
  const remaining = new Set(ALL_THIRD_SLOTS);

  while (remaining.size > 0) {
    let bestSlot = '';
    let bestAvailable: string[] = [];
    let minCount = Infinity;

    for (const slot of remaining) {
      const eligible = slot.slice(1).split('').filter(g => qualifiedGroups.has(g) && !assigned.has(g));
      if (eligible.length < minCount) {
        minCount = eligible.length;
        bestSlot = slot;
        bestAvailable = eligible;
      }
    }

    remaining.delete(bestSlot);
    const pick = sorted.find(t => bestAvailable.includes(t.group) && !assigned.has(t.group));
    if (pick) {
      result.set(bestSlot, { name: pick.name, flag: pick.flag });
      assigned.add(pick.group);
    } else {
      result.set(bestSlot, null);
    }
  }

  return result;
}

function makeSlot(label: string, standings: Record<string, (TeamData | null)[]>, thirdMap: Map<string, TeamData | null>): Slot {
  if (!label.startsWith('3') && label.length === 2) {
    const pos = parseInt(label[0]) - 1;
    return { label, team: standings[label[1]]?.[pos] ?? null };
  }
  if (label.startsWith('3')) {
    return { label, team: thirdMap.get(label) ?? null };
  }
  return { label, team: null };
}

const TBD: BracketMatch = {
  top:    { label: 'TBD', team: null },
  bottom: { label: 'TBD', team: null },
};
const tbds = (n: number): BracketMatch[] => Array(n).fill(TBD);

// ── Sub-components ─────────────────────────────────────────────────────────────

function TeamRow({ s, lang }: { s: Slot; lang: Lang }) {
  if (s.team) {
    const qualified = QUALIFIED_TEAMS.has(s.team.name);
    return (
      <div className={`bk-team${qualified ? ' bk-team--qualified' : ''}`}>
        <span className="bk-flag">{s.team.flag}</span>
        <span className="bk-name">{translateTeam(s.team.name, lang)}</span>
      </div>
    );
  }
  return (
    <div className="bk-team bk-team--tbd">
      <span className="bk-seed">{s.label}</span>
    </div>
  );
}

function MatchCard({ m, centerY, lang }: { m: BracketMatch; centerY: number; lang: Lang }) {
  return (
    <div className="bk-card" style={{ top: centerY - CARD_H / 2, width: CARD_W }}>
      <TeamRow s={m.top} lang={lang} />
      <div className="bk-sep" />
      <TeamRow s={m.bottom} lang={lang} />
    </div>
  );
}

function RoundCol({ matches, round, lang, label }: {
  matches: BracketMatch[]; round: number; lang: Lang; label?: string;
}) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 0 }}>
      {label && <div className="bk-round-label">{label}</div>}
      <div style={{ width: CARD_W, height: TOTAL_H, position: 'relative', flexShrink: 0 }}>
        {matches.map((m, i) => (
          <MatchCard key={i} m={m} centerY={cy(round, i)} lang={lang} />
        ))}
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

export default function BracketClient({ standings, thirdPlace }: Props) {
  const { lang } = useLanguage();
  const l = lang as Lang;
  const thirdMap = resolveThirdPlace(thirdPlace);

  const leftR32 = LEFT_SEEDS.map(([a, b]) => ({
    top: makeSlot(a, standings, thirdMap), bottom: makeSlot(b, standings, thirdMap),
  }));
  const rightR32 = RIGHT_SEEDS.map(([a, b]) => ({
    top: makeSlot(a, standings, thirdMap), bottom: makeSlot(b, standings, thirdMap),
  }));

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
                matches={r === 0 ? leftR32 : tbds(8 / Math.pow(2, r))}
                round={r}
                lang={l}
                label={ROUND_LABELS[r]}
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
              <MatchCard m={TBD} centerY={TOTAL_H / 2} lang={l} />
            </div>
          </div>
          <FinalConnector flip />

          {/* ── Right half (SF → R32) ── */}
          {[3, 2, 1, 0].map(r => (
            <div key={`R${r}`} style={{ display: 'flex', alignItems: 'flex-start' }}>
              {r < 3 && <Connector fromRound={r} flip />}
              <RoundCol
                matches={r === 0 ? rightR32 : tbds(8 / Math.pow(2, r))}
                round={r}
                lang={l}
                label={ROUND_LABELS[r]}
              />
            </div>
          ))}

        </div>
      </div>

      <ThirdPlaceTable teams={thirdPlace} lang={l} />
    </main>
  );
}
