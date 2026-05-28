import type { H2HResult } from '@/lib/types';

interface Props {
  h2h: H2HResult[];
}

export default function H2HHistory({ h2h }: Props) {
  return (
    <div className="info-card glass-card">
      <div className="info-card__header">
        <span className="info-card__title">Head-to-Head</span>
      </div>
      <div className="info-card__rows">
        {h2h.map((r, i) => (
          <div key={i} className="h2h-row">
            <span className="h2h-row__team h2h-row__team--home">
              {r.home_flag} {r.home_team}
            </span>
            <span className="h2h-row__score">
              {r.home_score} – {r.away_score}
            </span>
            <span className="h2h-row__team h2h-row__team--away">
              {r.away_team} {r.away_flag}
            </span>
            <span className="h2h-row__date">{r.date}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
