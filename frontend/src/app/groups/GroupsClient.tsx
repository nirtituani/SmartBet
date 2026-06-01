'use client';

import { useState, useTransition } from 'react';
import { useRouter } from 'next/navigation';
import { useLanguage } from '@/contexts/LanguageContext';
import { t, translateTeam, translateGroup } from '@/lib/i18n';
import { refreshGroupStandings } from '@/lib/api';
import type { StandingRow } from '@/lib/types';

type GroupMap = Record<string, StandingRow[]>;

export default function GroupsClient({ groups: initialGroups }: { groups: GroupMap }) {
  const { lang } = useLanguage();
  const tr = t[lang].groups;
  const cols = tr.cols;
  const isRtl = lang === 'he';
  const router = useRouter();
  const [groups, setGroups] = useState(initialGroups);
  const [isPending, startTransition] = useTransition();

  function handleRefresh() {
    startTransition(async () => {
      try {
        const fresh = await refreshGroupStandings();
        setGroups(fresh);
        router.refresh();
      } catch {
        // ignore
      }
    });
  }

  const sortedGroupNames = Object.keys(groups).sort();

  return (
    <main className="groups-page" dir={isRtl ? 'rtl' : 'ltr'}>
      <p className="groups-page__breadcrumb">{tr.breadcrumb}</p>
      <div className="groups-page__header">
        <h1 className="groups-page__title">{tr.title}</h1>
        <button
          className="groups-page__refresh-btn"
          onClick={handleRefresh}
          disabled={isPending}
        >
          {isPending ? '⟳ Updating…' : '⟳ Refresh Standings'}
        </button>
      </div>
      <p className="groups-page__subtitle">{tr.subtitle}</p>

      <div className="groups-grid">
        {sortedGroupNames.map((groupName) => (
          <div key={groupName} className="group-card glass-card">
            <h2 className="group-card__title">{translateGroup(groupName, lang)}</h2>
            <table className="standings-table">
              <thead>
                <tr>
                  <th className="standings-table__pos">#</th>
                  <th className="standings-table__team">{cols.team}</th>
                  <th>{cols.mp}</th>
                  <th>{cols.w}</th>
                  <th>{cols.d}</th>
                  <th>{cols.l}</th>
                  <th className="col-gf">{cols.gf}</th>
                  <th className="col-ga">{cols.ga}</th>
                  <th>{cols.gd}</th>
                  <th className="standings-table__pts">{cols.pts}</th>
                </tr>
              </thead>
              <tbody>
                {groups[groupName].map((row, i) => (
                  <tr key={row.name} className={i < 2 ? 'standings-table__qualify' : ''}>
                    <td className="standings-table__pos">{i + 1}</td>
                    <td className="standings-table__team">
                      <div className="standings-table__team-cell">
                        <span className="standings-table__flag">{row.flag}</span>
                        <span className="standings-table__name">{translateTeam(row.name, lang)}</span>
                      </div>
                    </td>
                    <td>{row.mp}</td>
                    <td>{row.w}</td>
                    <td>{row.d}</td>
                    <td>{row.l}</td>
                    <td className="col-gf">{row.gf}</td>
                    <td className="col-ga">{row.ga}</td>
                    <td>{row.gd === 0 ? '0' : row.gd > 0 ? `+${row.gd}` : row.gd}</td>
                    <td className="standings-table__pts">{row.pts}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ))}
      </div>
    </main>
  );
}
