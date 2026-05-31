import type { ScoreOdd } from '@/lib/types';

interface Props {
  scores: ScoreOdd[];
  lang?: string;
}

export default function ExactScores({ scores, lang = 'en' }: Props) {
  const title = lang === 'he' ? 'תוצאה מדויקת' : 'Correct Score';
  if (!scores || scores.length === 0) return null;

  const best = Math.min(...scores.map(s => s.odds));

  return (
    <div className="info-card glass-card">
      <div className="info-card__header">
        <span className="info-card__title">{title}</span>
      </div>
      <div className="scores-grid">
        {scores.map((s, i) => (
          <div key={i} className={`score-cell${s.odds === best ? ' score-cell--best' : ''}`}>
            <span className="score-cell__score">{s.score}</span>
            <span className="score-cell__odds">{s.odds.toFixed(2)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
