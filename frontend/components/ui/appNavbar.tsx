"use client";

import Link from "next/link";
import { Menu, X } from "lucide-react";
import { useState } from "react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { useGetMyselfQuery } from "@/lib/api/user/user.api";

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

  return (
    <header className="fixed top-0 left-0 z-50 w-full border-b border-border bg-background/80 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">

        {/* App Name */}
        <Link
          href="/"
          className="text-xl font-bold tracking-wide font-quicksand "
        >
          Train3
        </Link>

        {/* Desktop Profile */}
        <div className="hidden md:flex items-center gap-3">

          <span className="text-md font-medium font-quicksand ">
            {displayName}
          </span>

          <Avatar className="h-10 w-10 cursor-pointer font-quicksand ">
            <AvatarImage src="/avatar.png" />
            <AvatarFallback>{initials}</AvatarFallback>
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