export const dynamic = 'force-dynamic';

import Header from '@/components/Header';
import OddsClient from './OddsClient';
import { fetchWCWinnerOdds } from '@/lib/api';
import type { WCOddsEntry } from '@/lib/types';
import './odds.css';

export { type WCOddsEntry };

export default async function OddsPage() {
  const entries = await fetchWCWinnerOdds().catch(() => [] as WCOddsEntry[]);
  return (
    <>
      <Header />
      <OddsClient entries={entries} />
    </>
  );
}
