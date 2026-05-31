import type { AIPrediction as AIPredictionType } from '@/lib/types';

interface Props {
  prediction: AIPredictionType;
}

export default function AIPrediction({ prediction }: Props) {
  const { projected_score, confidence_percentage, tactical_analysis, key_factors, additional_context, value_bet } = prediction;

  return (
    <div className="ai-card glass-card glass-card-gold">
      <div className="ai-card__label">SmartBet AI Prediction</div>

      <div className="ai-card__score">
        {projected_score.home_goals} – {projected_score.away_goals}
      </div>
      <div className="ai-card__outcome">{projected_score.outcome_summary}</div>

      <div className="ai-card__confidence-label">
        <span>Confidence Score</span>
        <span>{confidence_percentage}%</span>
      </div>
      <div className="confidence-bar">
        <div className="confidence-bar__fill" style={{ width: `${confidence_percentage}%` }} />
      </div>

      <p className="ai-card__analysis">{tactical_analysis}</p>

      <div className="ai-card__factors">
        {key_factors.map((f, i) => (
          <p key={i} className="ai-card__factor">{f}</p>
        ))}
      </div>

      {additional_context && (
        <p className="ai-card__analysis ai-card__additional-context">{additional_context}</p>
      )}

      <div className="ai-card__value-bet">
        <div className="ai-card__value-bet-label">Value Bet Recommendation</div>
        <div className="ai-card__value-bet-rec">{value_bet.recommendation}</div>
        <div className="ai-card__value-bet-odds">@ {value_bet.target_odds.toFixed(2)}</div>
        <p className="ai-card__value-bet-rational">{value_bet.rational}</p>
      </div>
    </div>
  );
}
