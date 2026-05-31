import { translateTeam } from '@/lib/i18n';
import type { Lang } from '@/lib/i18n';
import type { H2HResult } from '@/lib/types';

interface Props {
  h2h: H2HResult[];
  lang?: Lang;
}

export default function H2HHistory({ h2h, lang = 'en' }: Props) {
  const title = lang === 'he' ? 'גברת על גברת' : 'Head-to-Head';
  return (
    <div className="info-card glass-card">
      <div className="info-card__header">
        <span className="info-card__title">{title}</span>
      </div>
      <div className="info-card__rows">
        {h2h.length === 0 ? (
          <p className="info-card__empty">
            {lang === 'he' ? 'אין עימותים קודמים' : 'No previous meetings'}
          </p>
        ) : h2h.map((r, i) => (
          <div key={i} className="h2h-row" data-tooltip={r.tournament || undefined}>
            <span className="h2h-row__team h2h-row__team--home">
              {r.home_flag} {translateTeam(r.home_team, lang)}
            </span>
            <span className="h2h-row__score">
              {r.home_score} – {r.away_score}
            </span>
            <span className="h2h-row__team h2h-row__team--away">
              {translateTeam(r.away_team, lang)} {r.away_flag}
            </span>
            <span className="h2h-row__date">{r.date.slice(8,10)}/{r.date.slice(5,7)}/{r.date.slice(0,4)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
