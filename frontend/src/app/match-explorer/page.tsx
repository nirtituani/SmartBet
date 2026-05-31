import Header from '@/components/Header';
import MatchExplorerClient from './MatchExplorerClient';
import { fetchUpcomingMatches } from '@/lib/api';
import './match-explorer.css';

export const dynamic = 'force-dynamic';

export default async function MatchExplorerPage() {
  const matches = await fetchUpcomingMatches();
  return (
    <>
      <Header />
      <MatchExplorerClient matches={matches} />
    </>
  );
}
