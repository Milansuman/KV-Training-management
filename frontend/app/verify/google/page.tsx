"use client";

import { Suspense, useEffect, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useGoogleHandshakeMutation } from "@/lib/api/auth/auth.api";
import { toast } from "sonner";

function GoogleVerifyContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [googleHandshake] = useGoogleHandshakeMutation();
  // Guard against React strict-mode double-invocation in development.
  const attempted = useRef(false);

  useEffect(() => {
    if (attempted.current) return;
    attempted.current = true;

    const nonce = searchParams.get("nonce");

    if (!nonce) {
      toast.error("Invalid verification link. Please try signing in again.");
      router.replace("/login");
      return;
    }

    googleHandshake({ nonce })
      .unwrap()
      .then(() => {
        router.replace("/dashboard");
      })
      .catch(() => {
        toast.error("Google sign-in failed. Please try again.");
        router.replace("/login");
      });
  }, [googleHandshake, router, searchParams]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="flex flex-col items-center gap-4">
        <div
          className="h-10 w-10 animate-spin rounded-full border-4 border-muted border-t-primary"
          aria-label="Loading"
        />
        <p className="text-muted-foreground text-sm">
          Completing Google sign-in…
        </p>
      </div>
    </div>
  );
}

export default function GoogleVerifyPage() {
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center min-h-screen">
          <div className="flex flex-col items-center gap-4">
            <div
              className="h-10 w-10 animate-spin rounded-full border-4 border-muted border-t-primary"
              aria-label="Loading"
            />
            <p className="text-muted-foreground text-sm">Loading…</p>
          </div>
        </div>
      }
    >
      <GoogleVerifyContent />
    </Suspense>
  );
}
