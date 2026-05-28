import Link from 'next/link';
import Header from '@/components/Header';
import TeamForm from '@/components/TeamForm';
import H2HHistory from '@/components/H2HHistory';
import { fetchMatchDetail } from '@/lib/api';
import './match-intelligence.css';

export default async function MatchIntelligencePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const detail = await fetchMatchDetail(id);
  const { match, home_form, away_form, h2h } = detail;

  return (
    <>
      <Header />
      <main className="intel">
        <Link href="/match-explorer" className="intel__back-btn">← Explorer</Link>
        <h1 className="intel__title">Match Intelligence &amp; AI Score Predictor</h1>

        <div className="matchup glass-card glass-card-blue">
          <div className="matchup__team">
            <span className="matchup__flag">{match.home_team.flag}</span>
            <span className="matchup__name">{match.home_team.name}</span>
            <span className="matchup__rank">FIFA Rank #{match.home_team.fifa_rank}</span>
          </div>
          <span className="matchup__vs">VS</span>
          <div className="matchup__team">
            <span className="matchup__flag">{match.away_team.flag}</span>
            <span className="matchup__name">{match.away_team.name}</span>
            <span className="matchup__rank">FIFA Rank #{match.away_team.fifa_rank}</span>
          </div>
        </div>

        <div className="intel__top-row">
          <TeamForm teamName={match.home_team.name} teamFlag={match.home_team.flag} form={home_form} />
          <H2HHistory h2h={h2h} />
          <TeamForm teamName={match.away_team.name} teamFlag={match.away_team.flag} form={away_form} />
        </div>

        {/* Bottom row: filled in Task 12 */}
        <div className="intel__bottom-row">
          <div className="glass-card info-card" />
          <div className="glass-card info-card" />
        </div>
      </main>
    </>
  );
}
