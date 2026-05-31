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
  if (!detail) return <><Header /><p style={{ color: 'white', padding: '2rem' }}>Match not available.</p></>;
  return (
    <>
      <Header />
      <MatchIntelClient detail={detail} />
    </>
  );
}
