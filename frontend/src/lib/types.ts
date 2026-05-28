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
}

export interface H2HResult {
  date: string;
  home_team: string;
  home_flag: string;
  away_team: string;
  away_flag: string;
  home_score: number;
  away_score: number;
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
  value_bet: { recommendation: string; target_odds: number; rational: string };
}

export interface MatchDetail {
  match: Match;
  home_form: FormResult[];
  away_form: FormResult[];
  h2h: H2HResult[];
  odds_comparison: BookmakerOdds[];
  prediction: AIPrediction | null;
}
