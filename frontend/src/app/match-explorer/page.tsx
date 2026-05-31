export const dynamic = 'force-dynamic';

import Header from '@/components/Header';
import MatchExplorerClient from './MatchExplorerClient';
import { fetchUpcomingMatches } from '@/lib/api';
import './match-explorer.css';

export default async function MatchExplorerPage() {
  const matches = await fetchUpcomingMatches().catch(() => []);
  return (
    <>
      <Header />
      <MatchExplorerClient matches={matches} />
    </>
  );
}
