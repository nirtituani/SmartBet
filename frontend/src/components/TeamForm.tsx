'use client';

import { useState } from 'react';
import { translateTeam } from '@/lib/i18n';
import type { Lang } from '@/lib/i18n';
import type { FormResult, TeamLineup } from '@/lib/types';
import PitchLineup from './PitchLineup';

const POSITION_ORDER: Record<string, number> = {
  GK: 0,
  RB: 1, CB: 1, LB: 1, RWB: 1, LWB: 1,
  CDM: 2, CM: 2, CAM: 2, RM: 2, LM: 2, DM: 2,
  RW: 3, LW: 3, ST: 3, CF: 3, SS: 3,
};

const POSITION_GROUP: Record<string, string> = {
  GK: 'GK',
  RB: 'DEF', CB: 'DEF', LB: 'DEF', RWB: 'DEF', LWB: 'DEF',
  CDM: 'MID', CM: 'MID', CAM: 'MID', RM: 'MID', LM: 'MID', DM: 'MID',
  RW: 'ATT', LW: 'ATT', ST: 'ATT', CF: 'ATT', SS: 'ATT',
};

interface Props {
  teamName: string;
  teamFlag: string;
  form: FormResult[];
  lang?: Lang;
  lineup?: TeamLineup;
}

export default function TeamForm({ teamName, teamFlag, form, lang = 'en', lineup }: Props) {
  const [tab, setTab] = useState<'form' | 'lineup'>('form');
  const formLabel = lang === 'he' ? 'פורמה' : 'Form';
  const lineupLabel = lang === 'he' ? 'הרכב' : 'Lineup';

  const sorted = lineup
    ? [...lineup.starters].sort(
        (a, b) => (POSITION_ORDER[a.position] ?? 9) - (POSITION_ORDER[b.position] ?? 9),
      )
    : [];

  const groups: { label: string; players: typeof sorted }[] = [];
  for (const p of sorted) {
    const label = POSITION_GROUP[p.position] ?? 'MID';
    const last = groups[groups.length - 1];
    if (last && last.label === label) {
      last.players.push(p);
    } else {
      groups.push({ label, players: [p] });
    }
  }

  return (
    <div className="info-card glass-card">
      <div className="info-card__header">
        <span className="info-card__flag">{teamFlag}</span>
        <span className="info-card__title">{teamName}</span>
      </div>

      {lineup && (
        <div className="team-card-tabs">
          <button
            className={`team-card-tab${tab === 'form' ? ' team-card-tab--active' : ''}`}
            onClick={() => setTab('form')}
          >
            {formLabel}
          </button>
          <button
            className={`team-card-tab${tab === 'lineup' ? ' team-card-tab--active' : ''}`}
            onClick={() => setTab('lineup')}
          >
            {lineupLabel}
          </button>
        </div>
      )}

      {tab === 'form' && (
        <div className="info-card__rows">
          {form.map((r, i) => (
            <div key={i} className="form-row" data-tooltip={r.tournament || undefined}>
              <span className={`badge badge-${r.result === 'W' ? 'win' : r.result === 'D' ? 'draw' : 'loss'}`}>
                {r.result}
              </span>
              <span className="form-row__score">
                {r.score_home}–{r.score_away}{r.score_home === r.score_away && r.result !== 'D' ? ' (p)' : ''}
              </span>
              <span className="form-row__opponent">
                {r.opponent_flag} {translateTeam(r.opponent, lang)}
              </span>
              <span className="form-row__date">{r.date.slice(8, 10)}/{r.date.slice(5, 7)}</span>
            </div>
          ))}
        </div>
      )}

      {tab === 'lineup' && lineup && (
        <PitchLineup lineup={lineup} teamFlag={teamFlag} teamName={teamName} />
      )}
    </div>
  );
}
