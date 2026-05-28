import type { Match, MatchDetail, BookmakerOdds } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

export async function fetchUpcomingMatches(): Promise<Match[]> {
  const res = await fetch(`${API_BASE}/api/v1/matches/upcoming`, {
    next: { revalidate: 300 },
  });
  if (!res.ok) throw new Error(`Failed to fetch matches: ${res.status}`);
  return res.json();
}

export async function fetchMatchDetail(id: string): Promise<MatchDetail> {
  const res = await fetch(`${API_BASE}/api/v1/matches/${id}/predictions`, {
    next: { revalidate: 60 },
  });
  if (!res.ok) throw new Error(`Failed to fetch match ${id}: ${res.status}`);
  return res.json();
}

export function groupMatchesByDate(matches: Match[]): Record<string, Match[]> {
  return matches.reduce<Record<string, Match[]>>((acc, m) => {
    (acc[m.kickoff_date] ??= []).push(m);
    return acc;
  }, {});
}

export function formatDate(isoDate: string): string {
  return new Date(isoDate).toLocaleDateString('en-US', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
  });
}

export function getBestOdds(odds: BookmakerOdds[]) {
  return {
    bestHome: Math.max(...odds.map((o) => o.home)),
    bestDraw: Math.max(...odds.map((o) => o.draw)),
    bestAway: Math.max(...odds.map((o) => o.away)),
  };
}
