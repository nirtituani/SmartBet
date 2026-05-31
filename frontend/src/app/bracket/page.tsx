export const dynamic = 'force-dynamic';

import Header from '@/components/Header';
import BracketClient from './BracketClient';
import { fetchGroupStandings } from '@/lib/api';
import './bracket.css';

export default async function BracketPage() {
  const raw = await fetchGroupStandings().catch(() => ({} as Record<string, import('@/lib/types').StandingRow[]>));
  // Convert "Group A" → "A", keep top 2 per group
  const standings: Record<string, { name: string; flag: string }[]> = {};
  for (const [group, rows] of Object.entries(raw)) {
    standings[group.replace('Group ', '')] = rows.slice(0, 2).map(r => ({ name: r.name, flag: r.flag }));
  }
  return (
    <>
      <Header />
      <BracketClient standings={standings} />
    </>
  );
}
