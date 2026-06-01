import Header from '@/components/Header';
import MatchIntelClient from './MatchIntelClient';
import './match-intelligence.css';

export const dynamic = 'force-dynamic';

export default async function MatchIntelligencePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <>
      <Header />
      <MatchIntelClient matchId={id} />
    </>
  );
}
