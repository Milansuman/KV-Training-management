import { EventCalendar } from "@/components/custom/event-calendar"

export default async function DashboardProgram({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params;
  const programId = parseInt(id, 10);

  return (
    <main className="w-screen h-screen p-4">
      <EventCalendar className="w-full h-full" programId={programId} />
    </main>
  );
}
