'use client';

import { useEffect, useState } from 'react';
import { useLanguage } from '@/contexts/LanguageContext';
import { t } from '@/lib/i18n';
import { translateTeam } from '@/lib/i18n';
import { fetchWCWinnerOdds } from '@/lib/api';
import type { WCOddsEntry } from '@/lib/types';

interface Props {
  entries: WCOddsEntry[];
}

const MEDAL: Record<number, string> = { 1: '🥇', 2: '🥈', 3: '🥉' };

export default function OddsClient({ entries: initialEntries }: Props) {
  const { lang } = useLanguage();
  const tr = t[lang].odds;
  const [entries, setEntries] = useState<WCOddsEntry[]>(initialEntries);
  const [loading, setLoading] = useState(initialEntries.length === 0);

  useEffect(() => {
    fetchWCWinnerOdds()
      .then(setEntries)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const maxProb = entries[0]?.probability ?? 1;

  return (
    <main className="wc-odds" dir={lang === 'he' ? 'rtl' : 'ltr'}>
      <div className="wc-odds__header">
        <p className="wc-odds__breadcrumb">{tr.breadcrumb}</p>
        <h1 className="wc-odds__title">{tr.title}</h1>
        <p className="wc-odds__subtitle">{tr.subtitle}</p>
      </div>

      {loading ? (
        <div className="wc-odds__loading">
          <div className="wc-odds__spinner" />
        </div>
      ) : entries.length === 0 ? (
        <div className="wc-odds__empty">—</div>
      ) : (
        <div className="wc-odds__table-wrap">
          <table className="wc-odds__table">
            <thead>
              <tr>
                <th className="wc-odds__th wc-odds__th--rank">{tr.rank}</th>
                <th className="wc-odds__th wc-odds__th--team">{tr.team}</th>
                <th className="wc-odds__th wc-odds__th--prob">{tr.probability}</th>
                <th className="wc-odds__th wc-odds__th--odds">{tr.decimal_odds}</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((entry, i) => {
                const rank = i + 1;
                const barPct = (entry.probability / maxProb) * 100;
                return (
                  <tr key={entry.team} className={`wc-odds__row${rank <= 3 ? ' wc-odds__row--top' : ''}`}>
                    <td className="wc-odds__td wc-odds__td--rank">
                      {MEDAL[rank] ?? <span className="wc-odds__rank-num">{rank}</span>}
                    </td>
                    <td className="wc-odds__td wc-odds__td--team">
                      <span className="wc-odds__flag">{entry.flag}</span>
                      <span className="wc-odds__team-name">{translateTeam(entry.team, lang)}</span>
                    </td>
                    <td className="wc-odds__td wc-odds__td--prob">
                      <div className="wc-odds__prob-wrap">
                        <div
                          className={`wc-odds__prob-bar${rank === 1 ? ' wc-odds__prob-bar--gold' : rank === 2 ? ' wc-odds__prob-bar--silver' : rank === 3 ? ' wc-odds__prob-bar--bronze' : ''}`}
                          style={{ width: `${barPct}%` }}
                        />
                        <span className="wc-odds__prob-text">{entry.probability.toFixed(1)}%</span>
                      </div>
                    </td>
                    <td className="wc-odds__td wc-odds__td--odds">
                      <span className="wc-odds__odds-value">{entry.decimal_odds.toFixed(2)}</span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      <p className="wc-odds__source">{tr.source}</p>
    </main>
  );
}
