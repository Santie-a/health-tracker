import { SessionDetail } from "@/features/training/components/session-detail";

export default async function TrainingSessionPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <SessionDetail id={Number(id)} />;
}
