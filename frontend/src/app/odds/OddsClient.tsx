'use client';

import { useEffect, useState } from 'react';
import { useLanguage } from '@/contexts/LanguageContext';
import { t, translateTeam } from '@/lib/i18n';
import { fetchWCWinnerOdds, fetchWCBookmakerOdds } from '@/lib/api';
import type { WCOddsEntry, WCBookmakerOdds } from '@/lib/types';

interface Props {
  polymarket: WCOddsEntry[];
  bookmakers: WCBookmakerOdds[];
}

const MEDAL: Record<number, string> = { 1: '🥇', 2: '🥈', 3: '🥉' };

export default function OddsClient({ polymarket: initPolymarket, bookmakers: initBookmakers }: Props) {
  const { lang } = useLanguage();
  const tr = t[lang].odds;
  const [tab, setTab] = useState<'bookmakers' | 'polymarket'>('bookmakers');
  const [polymarket, setPolymarket] = useState<WCOddsEntry[]>(initPolymarket);
  const [bookmakers, setBookmakers] = useState<WCBookmakerOdds[]>(initBookmakers);

  useEffect(() => {
    fetchWCWinnerOdds().then(setPolymarket).catch(() => {});
    fetchWCBookmakerOdds().then(setBookmakers).catch(() => {});
  }, []);

  const isRtl = lang === 'he';

  return (
    <main className="wc-odds" dir={isRtl ? 'rtl' : 'ltr'}>
      <div className="wc-odds__header">
        <p className="wc-odds__breadcrumb">{tr.breadcrumb}</p>
        <h1 className="wc-odds__title">{tr.title}</h1>
        <p className="wc-odds__subtitle">{tr.subtitle}</p>
      </div>

      <div className="wc-odds__tabs">
        <button
          className={`wc-odds__tab${tab === 'bookmakers' ? ' wc-odds__tab--active' : ''}`}
          onClick={() => setTab('bookmakers')}
        >
          {tr.tabBookmakers}
        </button>
        <button
          className={`wc-odds__tab${tab === 'polymarket' ? ' wc-odds__tab--active' : ''}`}
          onClick={() => setTab('polymarket')}
        >
          {tr.tabMarket}
        </button>
      </div>

      {tab === 'bookmakers' ? (
        <BookmakersTable entries={bookmakers} lang={lang} tr={tr} />
      ) : (
        <PolymarketTable entries={polymarket} lang={lang} tr={tr} />
      )}
    </main>
  );
}

type OddsTr = typeof t['en']['odds'] | typeof t['he']['odds'];

function BookmakersTable({
  entries,
  lang,
  tr,
}: {
  entries: WCBookmakerOdds[];
  lang: string;
  tr: OddsTr;
}) {
  if (entries.length === 0) return <EmptyState />;

  return (
    <>
      <div className="wc-odds__table-wrap">
        <table className="wc-odds__table">
          <thead>
            <tr>
              <th className="wc-odds__th wc-odds__th--rank">{tr.rank}</th>
              <th className="wc-odds__th wc-odds__th--team">{tr.team}</th>
              <th className="wc-odds__th wc-odds__th--odds">{tr.bestOdds}</th>
              <th className="wc-odds__th wc-odds__th--bk">{tr.bookmaker}</th>
            </tr>
          </thead>
          <tbody>
            {entries.map((entry, i) => {
              const rank = i + 1;
              return (
                <tr key={entry.team} className={`wc-odds__row${rank <= 3 ? ' wc-odds__row--top' : ''}`}>
                  <td className="wc-odds__td wc-odds__td--rank">
                    {MEDAL[rank] ?? <span className="wc-odds__rank-num">{rank}</span>}
                  </td>
                  <td className="wc-odds__td wc-odds__td--team">
                    <span className="wc-odds__flag">{entry.flag}</span>
                    <span className="wc-odds__team-name">{translateTeam(entry.team, lang as 'en' | 'he')}</span>
                  </td>
                  <td className="wc-odds__td wc-odds__td--odds">
                    <span className="wc-odds__odds-value">{entry.best_odds.toFixed(2)}</span>
                  </td>
                  <td className="wc-odds__td wc-odds__td--bk">
                    <span className="wc-odds__bk-name">{entry.bookmaker}</span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <p className="wc-odds__source">{tr.sourceBookmakers}</p>
    </>
  );
}

function PolymarketTable({
  entries,
  lang,
  tr,
}: {
  entries: WCOddsEntry[];
  lang: string;
  tr: OddsTr;
}) {
  if (entries.length === 0) return <EmptyState />;
  const maxProb = entries[0]?.probability ?? 1;

  return (
    <>
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
                    <span className="wc-odds__team-name">{translateTeam(entry.team, lang as 'en' | 'he')}</span>
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
      <p className="wc-odds__source">{tr.sourcePolymarket}</p>
    </>
  );
}

function EmptyState() {
  return <div className="wc-odds__empty">—</div>;
}
