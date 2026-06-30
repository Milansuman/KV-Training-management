// components/calendar-sidebar.tsx

"use client";

import Link from "next/link";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { useGetMyselfQuery } from "@/lib/api/user/user.api";

import { CalendarClock, Users } from "lucide-react";
import { usePathname } from "next/navigation";

export default function DashboardSidebar({ programId}: { programId: string}) {
  const pathname = usePathname();
  const { data: user_details, isLoading: userLoading } = useGetMyselfQuery();

  return (
    <Sidebar>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem className="flex flex-col">
                <SidebarMenuButton
                  className="mb-3 h-12  rounded-lg px-3 data-[active=true]:bg-primary/70 data-[active=true]:text-primary-foreground"
                  isActive={pathname.endsWith(
                    `/dashboard/program/${programId}`,
                  )}
                >
                  <Link
                    href={`/dashboard/program/${programId}`}
                    className="flex w-full items-center gap-3"
                  >
                    <CalendarClock className="h-6 w-6 shrink-0" />
                    <span className="text-sm font-medium font-quicksand">
                      Sessions
                    </span>
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>

              {user_details?.is_admin && <SidebarMenuItem>
                <SidebarMenuButton
                  className="h-12 w-full rounded-lg px-3 data-[active=true]:bg-primary/70 data-[active=true]:text-primary-foreground"
                  isActive={pathname.endsWith("/users")}
                >
                  <Link
                    href={`/dashboard/program/${programId}/users`}
                    className="flex w-full items-center gap-3"
                  >
                    <Users className="h-6 w-6 shrink-0" />
                    <span className="text-sm font-medium font-quicksand">
                      Users
                    </span>
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
}
