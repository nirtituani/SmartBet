'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import TeamForm from '@/components/TeamForm';
import H2HHistory from '@/components/H2HHistory';
import OddsTable from '@/components/OddsTable';
import ExactScores from '@/components/ExactScores';
import AIPrediction from '@/components/AIPrediction';
import { useLanguage } from '@/contexts/LanguageContext';
import { fetchMatchDetail } from '@/lib/api';
import { t, translateTeam } from '@/lib/i18n';
import type { MatchDetail } from '@/lib/types';

export default function MatchIntelClient({ matchId }: { matchId: string }) {
  const { lang } = useLanguage();
  const tr = t[lang].intel;
  const [detail, setDetail] = useState<MatchDetail | null>(null);
  const [rightTab, setRightTab] = useState<'prediction' | 'scores'>('prediction');
  const [stickyProgress, setStickyProgress] = useState(0);
  const matchupRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchMatchDetail(matchId).then(setDetail).catch(() => {});
  }, [matchId]);

  useEffect(() => {
    if (!matchupRef.current) return;
    const HEADER_H = window.innerWidth <= 768 ? 56 : 64;
    const onScroll = () => {
      if (!matchupRef.current) return;
      const rect = matchupRef.current.getBoundingClientRect();
      const progress = Math.min(Math.max((HEADER_H - rect.top) / rect.height, 0), 1);
      setStickyProgress(progress);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
    return () => window.removeEventListener('scroll', onScroll);
  }, [detail]);

  if (!detail) return <main className="intel"><p style={{ color: 'white', padding: '2rem' }}>Loading...</p></main>;

  const { match, home_form, away_form, h2h, odds_comparison, exact_scores, prediction, lineup, prediction_updated_at } = detail;

  return (
    <main className="intel">
      <div
        className="matchup-sticky"
        style={{
          opacity: stickyProgress,
          transform: `translateY(${(1 - stickyProgress) * -100}%)`,
          pointerEvents: stickyProgress > 0.05 ? 'auto' : 'none',
        }}
      >
        <span className="matchup-sticky__team">
          <span className="matchup-sticky__flag">{match.home_team.flag}</span>
          <span className="matchup-sticky__name">{translateTeam(match.home_team.name, lang)}</span>
        </span>
        <span className="matchup-sticky__vs">VS</span>
        <span className="matchup-sticky__team">
          <span className="matchup-sticky__flag">{match.away_team.flag}</span>
          <span className="matchup-sticky__name">{translateTeam(match.away_team.name, lang)}</span>
        </span>
      </div>

      <Link href="/match-explorer" className="intel__back-btn">{tr.back}</Link>
      <h1 className="intel__title">{tr.title}</h1>

      <div ref={matchupRef} className="matchup glass-card glass-card-blue">
        <div className="matchup__team">
          <span className="matchup__flag">{match.home_team.flag}</span>
          <span className="matchup__name">{translateTeam(match.home_team.name, lang)}</span>
          <span className="matchup__rank">{tr.fifaRank} #{match.home_team.fifa_rank}</span>
        </div>
        <span className="matchup__vs">VS</span>
        <div className="matchup__team">
          <span className="matchup__flag">{match.away_team.flag}</span>
          <span className="matchup__name">{translateTeam(match.away_team.name, lang)}</span>
          <span className="matchup__rank">{tr.fifaRank} #{match.away_team.fifa_rank}</span>
        </div>
      </div>

      <div className="intel__top-row">
        <TeamForm teamName={translateTeam(match.home_team.name, lang)} teamFlag={match.home_team.flag} form={home_form} lang={lang} lineup={lineup?.home ?? undefined} />
        <H2HHistory h2h={h2h} lang={lang} />
        <TeamForm teamName={translateTeam(match.away_team.name, lang)} teamFlag={match.away_team.flag} form={away_form} lang={lang} lineup={lineup?.away ?? undefined} />
      </div>

      <div className="intel__bottom-row">
        <OddsTable odds={odds_comparison} />
        <div>
          <div className="tab-switcher">
            <button
              className={`tab-switcher__btn${rightTab === 'prediction' ? ' tab-switcher__btn--active-gold' : ''}`}
              onClick={() => setRightTab('prediction')}
            >
              {lang === 'he' ? 'תחזית AI' : 'AI Prediction'}
            </button>
            <button
              className={`tab-switcher__btn${rightTab === 'scores' ? ' tab-switcher__btn--active-blue' : ''}`}
              onClick={() => setRightTab('scores')}
            >
              {lang === 'he' ? 'תוצאה מדויקת' : 'Correct Score'}
            </button>
          </div>
          {rightTab === 'prediction' && prediction && (
            <>
              <AIPrediction prediction={prediction} />
              {prediction_updated_at && (
                <p className="intel__prediction-updated">
                  {lang === 'he' ? 'עודכן לאחרונה:' : 'Last updated:'}{' '}
                  {new Date(prediction_updated_at).toLocaleString(lang === 'he' ? 'he-IL' : 'en-GB', {
                    day: 'numeric', month: 'short', year: 'numeric',
                    hour: '2-digit', minute: '2-digit', timeZone: 'UTC', timeZoneName: 'short',
                  })}
                </p>
              )}
            </>
          )}
          {rightTab === 'scores' && <ExactScores scores={exact_scores} lang={lang} />}
        </div>
      </div>
    </main>
  );
}
