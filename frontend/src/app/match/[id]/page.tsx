import Header from '@/components/Header';
import MatchIntelClient from './MatchIntelClient';
import { fetchMatchDetail } from '@/lib/api';
import './match-intelligence.css';

export async function generateStaticParams() {
  return Array.from({ length: 72 }, (_, i) => ({ id: String(i + 1) }));
}

export default async function MatchIntelligencePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const detail = await fetchMatchDetail(id);
  return (
    <>
      <Header />
      <MatchIntelClient detail={detail} />
    </>
  );
}
