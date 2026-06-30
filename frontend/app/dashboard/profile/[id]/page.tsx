"use client";

import { ArrowLeft, Mail, User, Shield } from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { useGetMyselfQuery } from "@/lib/api/user/user.api";
import { useRouter } from "next/navigation";

export default function ProfilePage() {
  const router = useRouter();

  const { data: user, isLoading } = useGetMyselfQuery();

  if (isLoading) {
    return (
      <div className="flex h-[70vh] items-center justify-center">
        Loading...
      </div>
    );
  }

  if (!user) return null;

  const initials = user.display_name
    ?.split(" ")
    .map((word) => word[0])
    .join("")
    .toUpperCase();

  return (
    <div className="mx-auto max-w-5xl p-6 font-quicksand">
      <Button variant="ghost" onClick={() => router.back()} className="mb-8">
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back
      </Button>

      <h1 className="mb-8 text-4xl font-bold ">My Profile</h1>

      {/* Profile Card */}

      <div className="rounded-2xl border bg-card p-8 shadow-sm">
        <div className="flex flex-col items-center gap-5">
          <Avatar className="h-28 w-28">
            <AvatarImage src="/avatar.png" />
            <AvatarFallback className="text-3xl">{initials}</AvatarFallback>
          </Avatar>

          <div className="text-center">
            <h2 className="text-3xl font-bold font-quicksand">{user.display_name}</h2>

            <p className="mt-1 text-muted-foreground">@{user.username}</p>
          </div>

          <div className="rounded-full bg-primary px-4 py-1 text-primary-foreground">
            {user.is_admin ? "Administrator" : ""}
          </div>
        </div>
      </div>

      {/* Information */}

      <div className="mt-8 rounded-2xl border bg-card p-8 shadow-sm">
        <h2 className="mb-6 text-2xl font-semibold font-quicksand">Personal Information</h2>

        <div className="space-y-6">
          <div className="flex items-center gap-4">
            <User className="h-5 w-5 text-primary" />

            <div>
              <p className="text-sm text-muted-foreground">Username</p>

              <p className="font-medium">{user.username}</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <User className="h-5 w-5 text-primary" />

            <div>
              <p className="text-sm text-muted-foreground">Display Name</p>

              <p className="font-medium">{user.display_name}</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <Mail className="h-5 w-5 text-primary" />

            <div>
              <p className="text-sm text-muted-foreground">Email</p>

              <p className="font-medium">{user.email}</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <Shield className="h-5 w-5 text-primary" />

            <div>
              <p className="text-sm text-muted-foreground">Role</p>

              <p className="font-medium">
                {user.is_admin ? "Administrator" : "Employee"}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
