// app/dashboard/calendar/layout.tsx
import { SidebarProvider, SidebarInset } from "@/components/ui/sidebar";

import DashboardSidebar from "@/components/custom/program-sidebar";

export default async function CalendarLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  // const programId = parseInt(id, 10);
  return (
    <SidebarProvider>
      <DashboardSidebar programId={id} />

      <SidebarInset>{children}</SidebarInset>
    </SidebarProvider>
  );
}
