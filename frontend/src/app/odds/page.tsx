export const dynamic = 'force-dynamic';

import Header from '@/components/Header';
import OddsClient from './OddsClient';
import { fetchWCWinnerOdds, fetchWCBookmakerOdds } from '@/lib/api';
import type { WCOddsEntry, WCBookmakerOdds } from '@/lib/types';
import './odds.css';

export { type WCOddsEntry, type WCBookmakerOdds };

export default async function OddsPage() {
  const [polymarket, bookmakers] = await Promise.all([
    fetchWCWinnerOdds().catch(() => [] as WCOddsEntry[]),
    fetchWCBookmakerOdds().catch(() => [] as WCBookmakerOdds[]),
  ]);
  return (
    <>
      <Header />
      <OddsClient polymarket={polymarket} bookmakers={bookmakers} />
    </>
  );
}
