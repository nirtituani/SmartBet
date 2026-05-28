import type { BookmakerOdds } from '@/lib/types';
import { getBestOdds } from '@/lib/api';

interface Props {
  odds: BookmakerOdds[];
}

export default function OddsTable({ odds }: Props) {
  const { bestHome, bestDraw, bestAway } = getBestOdds(odds);

  return (
    <div className="info-card glass-card">
      <div className="info-card__header">
        <span className="info-card__title">Live Odds Comparison</span>
      </div>
      <table className="odds-table">
        <thead>
          <tr>
            <th className="odds-table__bookie-col">Bookmaker</th>
            <th>1</th>
            <th>X</th>
            <th>2</th>
          </tr>
        </thead>
        <tbody>
          {odds.map((o) => (
            <tr key={o.bookmaker}>
              <td className="odds-table__bookie">{o.bookmaker}</td>
              <td className={o.home === bestHome ? 'odds-table__best' : ''}>{o.home.toFixed(2)}</td>
              <td className={o.draw === bestDraw ? 'odds-table__best' : ''}>{o.draw.toFixed(2)}</td>
              <td className={o.away === bestAway ? 'odds-table__best' : ''}>{o.away.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
