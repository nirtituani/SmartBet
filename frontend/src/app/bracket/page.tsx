export const dynamic = 'force-dynamic';

import Header from '@/components/Header';
import BracketClient from './BracketClient';
import type { ThirdPlaceTeam, R32Result } from './BracketClient';
import { fetchGroupStandings, fetchUpcomingMatches } from '@/lib/api';
import './bracket.css';

export default async function BracketPage() {
  const [raw, matchesRaw] = await Promise.all([
    fetchGroupStandings().catch(() => ({} as Record<string, import('@/lib/types').StandingRow[]>)),
    fetchUpcomingMatches().catch(() => [] as import('@/lib/types').Match[]),
  ]);
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

  const r32Results: Record<string, R32Result> = {};
  const r16Results: Record<string, R32Result> = {};
  const qfResults:  Record<string, R32Result> = {};
  for (const m of matchesRaw) {
    const entry = { homeScore: m.score_home, awayScore: m.score_away, status: m.status, winner: m.winner ?? null };
    const key = `${m.home_team.name}|${m.away_team.name}`;
    if (m.group === 'Round of 32')    r32Results[key] = entry;
    if (m.group === 'Round of 16')    r16Results[key] = entry;
    if (m.group === 'Quarter Final')  qfResults[key]  = entry;
  }

  return (
    <>
      <Header />
      <BracketClient standings={standings} thirdPlace={thirdPlace} r32Results={r32Results} r16Results={r16Results} qfResults={qfResults} />
    </>
  );
}
