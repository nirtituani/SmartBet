'use client';

import { useState } from 'react';
import Link from 'next/link';
import TeamForm from '@/components/TeamForm';
import H2HHistory from '@/components/H2HHistory';
import OddsTable from '@/components/OddsTable';
import ExactScores from '@/components/ExactScores';
import AIPrediction from '@/components/AIPrediction';
import { useLanguage } from '@/contexts/LanguageContext';
import { t, translateTeam } from '@/lib/i18n';
import type { MatchDetail } from '@/lib/types';

export default function MatchIntelClient({ detail }: { detail: MatchDetail }) {
  const { lang } = useLanguage();
  const tr = t[lang].intel;
  const { match, home_form, away_form, h2h, odds_comparison, exact_scores, prediction, lineup } = detail;
  const [rightTab, setRightTab] = useState<'prediction' | 'scores'>('prediction');

  return (
    <main className="intel">
      <Link href="/match-explorer" className="intel__back-btn">{tr.back}</Link>
      <h1 className="intel__title">{tr.title}</h1>

      <div className="matchup glass-card glass-card-blue">
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
          {rightTab === 'prediction' && prediction && <AIPrediction prediction={prediction} />}
          {rightTab === 'scores' && <ExactScores scores={exact_scores} lang={lang} />}
        </div>
      </div>
    </main>
  );
}
