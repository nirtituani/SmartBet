export interface Team {
  id: number;
  name: string;
  flag: string;
  fifa_rank: number;
}

export interface Match {
  id: number;
  home_team: Team;
  away_team: Team;
  kickoff_time: string;
  kickoff_date: string;
  group: string;
  home_odds: number;
  draw_odds: number;
  away_odds: number;
}

export interface FormResult {
  opponent: string;
  opponent_flag: string;
  date: string;
  score_home: number;
  score_away: number;
  result: 'W' | 'D' | 'L';
  home_or_away: 'H' | 'A';
  tournament?: string;
}

export interface H2HResult {
  date: string;
  home_team: string;
  home_flag: string;
  away_team: string;
  away_flag: string;
  home_score: number;
  away_score: number;
  tournament?: string;
}

export interface BookmakerOdds {
  bookmaker: string;
  home: number;
  draw: number;
  away: number;
}

export interface AIPrediction {
  projected_score: { home_goals: number; away_goals: number; outcome_summary: string };
  confidence_percentage: number;
  tactical_analysis: string;
  key_factors: string[];
  additional_context?: string;
  value_bet: { recommendation: string; target_odds: number; rational: string };
}

export interface StandingRow {
  name: string;
  flag: string;
  fifa_rank: number;
  mp: number;
  w: number;
  d: number;
  l: number;
  gf: number;
  ga: number;
  gd: number;
  pts: number;
}

export interface ScoreOdd {
  score: string;
  odds: number;
}

export interface Player {
  name: string;
  position: string;
}

export interface TeamLineup {
  formation: string;
  starters: Player[];
}

export interface MatchLineup {
  home: TeamLineup;
  away: TeamLineup;
  is_predicted: boolean;
}

export interface WCOddsEntry {
  team: string;
  flag: string;
  probability: number;
  decimal_odds: number;
}

export interface WCBookmakerOdds {
  team: string;
  flag: string;
  best_odds: number;
  bookmaker: string;
}

export interface MatchDetail {
  match: Match;
  home_form: FormResult[];
  away_form: FormResult[];
  h2h: H2HResult[];
  odds_comparison: BookmakerOdds[];
  exact_scores: ScoreOdd[];
  prediction: AIPrediction | null;
  lineup: MatchLineup | null;
  prediction_updated_at: string | null;
}
