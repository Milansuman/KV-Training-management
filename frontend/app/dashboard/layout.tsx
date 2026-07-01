"use client";

import AppNavbar from "../../components/custom/appNavbar";
import { useGetMyselfQuery } from "@/lib/api/user/user.api";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function MainLayout({
  children,
}: {
  children: React.ReactNode;
  }) {
  const router = useRouter();
  const {
    isError
  } = useGetMyselfQuery();

  useEffect(() => {
    if (isError) {
      router.replace("/login")
    }
  }, [isError, router]);

  return (
    <>
      <AppNavbar />
      <main className="pt-24 w-screen h-screen overflow-x-hidden overflow-y-auto">{children}</main>
    </>
  );
}
