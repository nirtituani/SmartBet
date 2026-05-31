import type { TeamLineup, Player } from '@/lib/types';

const POSITION_ORDER: Record<string, number> = {
  GK: 0,
  RB: 1, CB: 1, LB: 1, RWB: 1, LWB: 1,
  CDM: 2, CM: 2, CAM: 2, RM: 2, LM: 2, DM: 2,
  RW: 3, LW: 3, ST: 3, CF: 3, SS: 3,
};

function parseRows(formation: string): number[] {
  return formation.split('-').map(Number).filter((n) => !isNaN(n) && n > 0);
}

function assignRows(starters: Player[], formation: string): Player[][] {
  const sorted = [...starters].sort(
    (a, b) => (POSITION_ORDER[a.position] ?? 9) - (POSITION_ORDER[b.position] ?? 9),
  );
  const rowCounts = [1, ...parseRows(formation)];
  const rows: Player[][] = [];
  let i = 0;
  for (const count of rowCounts) {
    rows.push(sorted.slice(i, i + count));
    i += count;
  }
  return rows;
}

function lastName(name: string) {
  const parts = name.trim().split(' ');
  return parts[parts.length - 1];
}

interface Props {
  lineup: TeamLineup;
  teamFlag: string;
  teamName: string;
}

export default function PitchLineup({ lineup, teamFlag, teamName }: Props) {
  const rows = assignRows(lineup.starters, lineup.formation);
  const numRows = rows.length;

  return (
    <div className="pitch-wrap">
      {/* Pitch SVG markings */}
      <svg
        className="pitch-svg"
        viewBox="0 0 100 138"
        preserveAspectRatio="none"
        aria-hidden="true"
      >
        {/* Grass */}
        <rect width="100" height="138" fill="#1a5c2a" />
        {/* Grass stripes */}
        {Array.from({ length: 7 }).map((_, i) => (
          <rect key={i} x="0" y={i * 20} width="100" height="10" fill="rgba(0,0,0,0.06)" />
        ))}
        {/* Pitch border */}
        <rect x="3" y="3" width="94" height="132" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.6" />
        {/* Center line */}
        <line x1="3" y1="69" x2="97" y2="69" stroke="rgba(255,255,255,0.4)" strokeWidth="0.5" />
        {/* Center circle */}
        <circle cx="50" cy="69" r="11" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.5" />
        {/* Center dot */}
        <circle cx="50" cy="69" r="0.8" fill="rgba(255,255,255,0.5)" />
        {/* Top penalty box */}
        <rect x="23" y="3" width="54" height="19" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.5" />
        {/* Top 6-yard box */}
        <rect x="36" y="3" width="28" height="8" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.5" />
        {/* Top goal */}
        <rect x="43" y="1" width="14" height="3" fill="none" stroke="rgba(255,255,255,0.5)" strokeWidth="0.5" />
        {/* Top penalty spot */}
        <circle cx="50" cy="15" r="0.8" fill="rgba(255,255,255,0.5)" />
        {/* Bottom penalty box */}
        <rect x="23" y="116" width="54" height="19" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.5" />
        {/* Bottom 6-yard box */}
        <rect x="36" y="127" width="28" height="8" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.5" />
        {/* Bottom goal */}
        <rect x="43" y="135" width="14" height="3" fill="none" stroke="rgba(255,255,255,0.5)" strokeWidth="0.5" />
        {/* Bottom penalty spot */}
        <circle cx="50" cy="123" r="0.8" fill="rgba(255,255,255,0.5)" />
      </svg>

      {/* Formation label */}
      <div className="pitch-formation-badge">
        <span className="pitch-formation-flag">{teamFlag}</span>
        <span className="pitch-formation-text">{teamName} · {lineup.formation}</span>
      </div>

      {/* Players */}
      <div className="pitch-players">
        {rows.map((row, rowIdx) => {
          // GK at top (rowIdx=0), attackers at bottom (rowIdx=numRows-1)
          const yPct = 8 + (rowIdx / (numRows - 1)) * 82;
          return row.map((player, colIdx) => {
            const xPct = ((colIdx + 1) / (row.length + 1)) * 100;
            return (
              <div
                key={`${player.position}-${player.name}`}
                className="pitch-player"
                style={{ left: `${xPct}%`, top: `${yPct}%` }}
              >
                <div className="pitch-player__circle">{teamFlag}</div>
                <span className="pitch-player__name">{lastName(player.name)}</span>
              </div>
            );
          });
        })}
      </div>
    </div>
  );
}
