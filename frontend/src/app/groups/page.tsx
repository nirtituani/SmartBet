export const dynamic = 'force-dynamic';

import Header from '@/components/Header';
import GroupsClient from './GroupsClient';
import { fetchGroupStandings } from '@/lib/api';
import type { StandingRow } from '@/lib/types';
import './groups.css';

export { type StandingRow };

export default async function GroupsPage() {
  const groups = await fetchGroupStandings();
  return (
    <>
      <Header />
      <GroupsClient groups={groups} />
    </>
  );
}
