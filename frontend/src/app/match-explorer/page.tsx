import Link from 'next/link';
import Header from '@/components/Header';
import { fetchUpcomingMatches, groupMatchesByDate, formatDate } from '@/lib/api';
import type { Match } from '@/lib/types';
import './match-explorer.css';

function MatchCard({ match }: { match: Match }) {
  return (
    <Link href={`/match/${match.id}`} className="match-card glass-card">
      <div className="match-card__team">
        <span className="match-card__flag">{match.home_team.flag}</span>
        <span className="match-card__team-name">{match.home_team.name}</span>
      </div>

      <div className="match-card__center">
        <span className="match-card__kickoff">{match.kickoff_time}</span>
        <span className="match-card__meta">{match.group}</span>
      </div>

      <div className="match-card__team match-card__team--away">
        <span className="match-card__flag">{match.away_team.flag}</span>
        <span className="match-card__team-name">{match.away_team.name}</span>
      </div>

      <div className="match-card__odds">
        {match.home_odds} | {match.draw_odds} | {match.away_odds}
      </div>
    </Link>
  );
}

export default async function MatchExplorerPage() {
  const matches = await fetchUpcomingMatches();
  const grouped = groupMatchesByDate(matches);
  const sortedDates = Object.keys(grouped).sort();

  return (
    <>
      <Header />
      <main className="explorer">
        <p className="explorer__breadcrumb">Home / Matches</p>
        <h1 className="explorer__title">Match Explorer</h1>
        <p className="explorer__subtitle">FIFA World Cup 2026</p>

        {sortedDates.map((date) => (
          <section key={date} className="explorer__date-section">
            <p className="explorer__date-label">{formatDate(date)}</p>
            {grouped[date].map((match) => (
              <MatchCard key={match.id} match={match} />
            ))}
          </section>
        ))}
      </main>
    </>
  );
}
