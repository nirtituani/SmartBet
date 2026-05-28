import type { FormResult } from '@/lib/types';

interface Props {
  teamName: string;
  teamFlag: string;
  form: FormResult[];
}

export default function TeamForm({ teamName, teamFlag, form }: Props) {
  return (
    <div className="info-card glass-card">
      <div className="info-card__header">
        <span className="info-card__flag">{teamFlag}</span>
        <span className="info-card__title">{teamName} Form</span>
      </div>
      <div className="info-card__rows">
        {form.map((r, i) => (
          <div key={i} className="form-row">
            <span className={`badge badge-${r.result === 'W' ? 'win' : r.result === 'D' ? 'draw' : 'loss'}`}>
              {r.result}
            </span>
            <span className="form-row__score">
              {r.score_home}–{r.score_away}
            </span>
            <span className="form-row__opponent">
              {r.opponent_flag} {r.opponent}
            </span>
            <span className="form-row__date">{r.date}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
