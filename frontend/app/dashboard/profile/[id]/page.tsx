"use client";

import { useState } from "react";
import { Loader2 } from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { UserResponse } from "@/lib/api/user/user.type";
import { useGetMyselfQuery, useUpdateUserMutation } from "@/lib/api/user/user.api";
import { useLogoutMutation } from "@/lib/api/auth/auth.api";
import { useRouter } from "next/navigation";

function ProfileForm({ user }: { user: UserResponse }) {
  const router = useRouter();
  const [updateUser, { isLoading: isUpdating }] = useUpdateUserMutation();
  const [logout, { isLoading: isLoggingOut }] = useLogoutMutation();

  const [displayName, setDisplayName] = useState(user.display_name);
  const [username, setUsername] = useState(user.username);
  const [email, setEmail] = useState(user.email);
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const initials = user.display_name
    .split(" ")
    .map((word: string) => word[0])
    .join("")
    .toUpperCase();

  const handleUpdate = async () => {
    if (password && password !== confirmPassword) return;

    await updateUser({
      id: user.id,
      body: {
        display_name: displayName || undefined,
        username: username || undefined,
        email: email || undefined,
        password: password || undefined,
      },
    });

    setPassword("");
    setConfirmPassword("");
  };

  const handleLogout = async () => {
    await logout();
    router.push("/login");
  };

  return (
    <div className="flex flex-col gap-8 lg:flex-row">
        {/* ── Left column – profile summary ── */}
        <div className="flex shrink-0 flex-col items-center gap-5 lg:w-72">
          <Avatar className="h-32 w-32">
            <AvatarImage src="/avatar.png" />
            <AvatarFallback className="text-4xl">{initials}</AvatarFallback>
          </Avatar>

          <div className="text-center">
            <h2 className="text-3xl font-bold">{user.display_name}</h2>
            <p className="mt-1 text-muted-foreground">@{user.username}</p>
          </div>

          {user.is_admin && (
            <div className="rounded-full bg-primary px-5 py-1.5 text-sm font-medium text-primary-foreground">
              Administrator
            </div>
          )}

          <Button
            variant="destructive"
            className=""
            onClick={handleLogout}
            disabled={isLoggingOut}
          >
            {isLoggingOut && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Logout
          </Button>
        </div>

        {/* ── Vertical divider ── */}
        <div className="hidden border-l lg:block" />

        {/* ── Right column – editable fields ── */}
        <div className="flex-1 space-y-6">
          <h2 className="mb-6 text-2xl font-semibold">Personal Information</h2>

          <div className="space-y-5">
            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="displayName">Display Name</Label>
              <Input
                id="displayName"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            <hr className="my-6" />

            <div className="space-y-2">
              <Label htmlFor="password">New Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Leave blank to keep current"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Confirm New Password</Label>
              <Input
                id="confirmPassword"
                type="password"
                placeholder="Re-enter new password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
            </div>
          </div>

          {password && password !== confirmPassword && confirmPassword && (
            <p className="text-sm text-destructive">Passwords do not match</p>
          )}

          <Button
            className="mt-4"
            onClick={handleUpdate}
            disabled={isUpdating}
          >
            {isUpdating && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Update Profile
          </Button>
        </div>
      </div>
  );
}

export default function ProfilePage() {
  const { data: user, isLoading } = useGetMyselfQuery();

  if (isLoading || !user) {
    return (
      <div className="flex h-[70vh] items-center justify-center">
        Loading...
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl p-6 font-quicksand">
      <ProfileForm user={user} />
    </div>
  );
}
