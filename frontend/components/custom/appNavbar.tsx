"use client";

import Link from "next/link";
import { Menu, X } from "lucide-react";
import { useState } from "react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { useGetMyselfQuery } from "@/lib/api/user/user.api";
import { useRouter } from "next/navigation";

export default function AppNavbar() {
  const [open, setOpen] = useState(false);
  const { data: user_details } = useGetMyselfQuery();

  const getInitials = (name: string) => {
    const parts = name.trim().split(/\s+/).filter(Boolean);
    if (parts.length === 0) return "U";
    if (parts.length === 1) return parts[0][0].toUpperCase();
    return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
  };

  const displayName = user_details?.display_name || user_details?.username || "Loading...";
  const initials = getInitials(displayName);
  const router = useRouter();

  function handleAvatarClick()
  {
    router.push(`/dashboard/profile/${user_details?.id}`)
  }
  return (
    <header className="fixed top-0 left-0 z-50 w-full border-b border-border bg-background/80 backdrop-blur-md">
      <div className="flex h-16 w-full  items-center justify-between px-6">

        {/* App Name */}
        <p className="shrink-0 text-xl font-bold tracking-wide font-quicksand">Train3</p>

        {/* Desktop Profile */}
        <div className=" hidden items-center gap-3 md:flex">

          <span className="text-md font-medium font-quicksand">
            {displayName}
          </span>

          <Avatar className="h-10 w-10 cursor-pointer font-quicksand" onClick={handleAvatarClick}>
            <AvatarImage src="/avatar.png" />
            <AvatarFallback >{initials}</AvatarFallback>
          </Avatar>

        </div>

        {/* Mobile Menu Button */}
        <button
          className="md:hidden"
          onClick={() => setOpen(!open)}
        >
          {open ? <X size={22} /> : <Menu size={22} />}
        </button>
      </div>

      {/* Mobile Menu */}
      {open && (
        <div className="border-t border-border bg-background md:hidden">

          <div className="flex items-center gap-3 p-4">

            <Avatar>
              <AvatarImage src="/avatar.png" />
              <AvatarFallback>{initials}</AvatarFallback>
            </Avatar>

            <div>
              <p className="font-semibold font-quicksand ">
                {displayName}
              </p>

              <p className="text-sm text-muted-foreground">
                View Profile
              </p>
            </div>

          </div>

        </div>
      )}
    </header>
  );
}