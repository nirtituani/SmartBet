import Header from '@/components/Header';
import MatchIntelClient from './MatchIntelClient';
import { fetchMatchDetail } from '@/lib/api';
import './match-intelligence.css';

export const dynamic = 'force-dynamic';

export default async function MatchIntelligencePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const detail = await fetchMatchDetail(id).catch(() => null);
  return (
    <>
      <Header />
      <MatchIntelClient detail={detail} />
    </>
  );
}
