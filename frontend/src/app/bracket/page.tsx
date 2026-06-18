export const dynamic = 'force-dynamic';

import Header from '@/components/Header';
import BracketClient from './BracketClient';
import type { ThirdPlaceTeam } from './BracketClient';
import { fetchGroupStandings } from '@/lib/api';
import './bracket.css';

export default async function BracketPage() {
  const raw = await fetchGroupStandings().catch(() => ({} as Record<string, import('@/lib/types').StandingRow[]>));
  const standings: Record<string, { name: string; flag: string }[]> = {};
  const thirdPlace: ThirdPlaceTeam[] = [];

  for (const [group, rows] of Object.entries(raw)) {
    const letter = group.replace('Group ', '');
    standings[letter] = rows.slice(0, 2).map(r => ({ name: r.name, flag: r.flag }));
    const r = rows[2];
    if (r) {
      thirdPlace.push({
        name: r.name, flag: r.flag, group: letter,
        pts: r.pts, gd: r.gd, gf: r.gf, ga: r.ga,
        mp: r.mp, w: r.w, d: r.d, l: r.l,
        fifa_rank: r.fifa_rank,
        fair_play: r.fair_play ?? 0,
      });
    }
  }

  return (
    <>
      <Header />
      <BracketClient standings={standings} thirdPlace={thirdPlace} />
    </>
  );
}
