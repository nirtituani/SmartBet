import type { Match, MatchDetail, BookmakerOdds, StandingRow, WCOddsEntry } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

export async function fetchUpcomingMatches(): Promise<Match[]> {
  const res = await fetch(`${API_BASE}/api/v1/matches/upcoming`, {
    cache: 'no-store',
  });
  if (!res.ok) throw new Error(`Failed to fetch matches: ${res.status}`);
  return res.json();
}

export async function fetchGroupStandings(): Promise<Record<string, StandingRow[]>> {
  const res = await fetch(`${API_BASE}/api/v1/groups/standings`, {
    cache: 'no-store',
  });
  if (!res.ok) throw new Error(`Failed to fetch standings: ${res.status}`);
  return res.json();
}

export async function refreshGroupStandings(): Promise<Record<string, StandingRow[]>> {
  const res = await fetch(`${API_BASE}/api/v1/groups/standings/refresh`, {
    method: 'POST',
    cache: 'no-store',
  });
  if (!res.ok) throw new Error(`Failed to refresh standings: ${res.status}`);
  return res.json();
}

export async function fetchMatchDetail(id: string): Promise<MatchDetail> {
  const res = await fetch(`${API_BASE}/api/v1/matches/${id}/predictions`, {
    next: { revalidate: 43200 },  // revalidate twice a day, matching backend prediction cache
  });
  if (!res.ok) throw new Error(`Failed to fetch match ${id}: ${res.status}`);
  return res.json();
}

export async function fetchWCWinnerOdds(): Promise<WCOddsEntry[]> {
  const res = await fetch(`${API_BASE}/api/v1/odds/wc-winner`, {
    next: { revalidate: 3600 },
  });
  if (!res.ok) throw new Error(`Failed to fetch WC winner odds: ${res.status}`);
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

export function formatDateHebrew(isoDate: string): string {
  const d = new Date(isoDate + 'T12:00:00');
  return d.toLocaleDateString('he-IL', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
}

export function getBestOdds(odds: BookmakerOdds[]) {
  return {
    bestHome: Math.max(...odds.map((o) => o.home)),
    bestDraw: Math.max(...odds.map((o) => o.draw)),
    bestAway: Math.max(...odds.map((o) => o.away)),
  };
}
