// app/dashboard/calendar/layout.tsx
"use client";
import { SidebarProvider, SidebarInset } from "@/components/ui/sidebar";

import DashboardSidebar from "@/components/custom/program-sidebar";
import { useGetMyselfQuery } from "@/lib/api/user/user.api";

export default function CalendarLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: { id: string };
}) {
  const { id } = params;
  const { data: user_details, isLoading: userLoading } = useGetMyselfQuery();

  // const programId = parseInt(id, 10);
  return (
    <SidebarProvider>
      <DashboardSidebar programId={id} is_admin={user_details?.is_admin ?? false} />

      <SidebarInset>{children}</SidebarInset>
    </SidebarProvider>
  );
}
