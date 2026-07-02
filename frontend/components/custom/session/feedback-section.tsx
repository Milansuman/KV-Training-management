"use client";

import { useMemo, useState } from "react";
import { Bot, GraduationCap, Loader2, Sparkles, User, UserCog } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

import { useGetFeedbackSubmissionsBySessionQuery } from "@/lib/api/feedback/feedback.api";
import { useGetAllUsersQuery } from "@/lib/api/user/user.api";
import { useGetFeedbackSummaryMutation } from "@/lib/api/ai/feedback.api";
import type { FeedbackSummaryResponse } from "@/lib/api/ai/feedback.type";
import type { SessionUserResponse } from "@/lib/api/session-permissions/session-permissions.type";

const formatDateTimeLong = (dateStr: string) =>
  new Date(dateStr).toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });

// Same role-visibility rules as backend ai/feedback/nodes.py
const VISIBLE_ROLES: Record<string, string[]> = {
  TRAINER: ["MODERATOR"],
  CANDIDATE: ["TRAINER", "MODERATOR"],
  MODERATOR: ["TRAINER", "CANDIDATE", "MODERATOR"],
};

const ROLE_ICONS: Record<string, React.ReactNode> = {
  TRAINER: <GraduationCap className="h-3 w-3" />,
  MODERATOR: <UserCog className="h-3 w-3" />,
  CANDIDATE: <User className="h-3 w-3" />,
};

interface FeedbackSectionProps {
  sessionId: number;
  user?: { id: number; is_admin?: boolean } | null;
  sessionUsers?: SessionUserResponse[];
}

export default function FeedbackSection({ sessionId, user, sessionUsers = [] }: FeedbackSectionProps) {
  const { data: feedbackList = [], isLoading: feedbackLoading } =
    useGetFeedbackSubmissionsBySessionQuery(sessionId);
  const { data: allUsers = [] } = useGetAllUsersQuery();
  const [getFeedbackSummary, { isLoading: summaryLoading }] =
    useGetFeedbackSummaryMutation();

  const [summaryResult, setSummaryResult] =
    useState<FeedbackSummaryResponse | null>(null);
  const [summaryError, setSummaryError] = useState<string | null>(null);

  const userMap = useMemo(() => {
    const map = new Map<number, string>();
    for (const u of allUsers) {
      map.set(u.id, u.display_name);
    }
    return map;
  }, [allUsers]);

  // Map of user_id → session role
  const userRoleMap = useMemo(() => {
    const map = new Map<number, string>();
    for (const su of sessionUsers) {
      map.set(su.user_id, su.role);
    }
    return map;
  }, [sessionUsers]);

  // Current user's role in this session
  const currentRole = useMemo(() => {
    if (!user) return null;
    return userRoleMap.get(user.id) ?? null;
  }, [user, userRoleMap]);

  // Filter feedback based on visibility rules (mirrors _VISIBLE_ROLES in backend nodes.py)
  const visibleFeedback = useMemo(() => {
    if (user?.is_admin) return feedbackList;

    const allowedSenderRoles = currentRole ? VISIBLE_ROLES[currentRole] : null;

    return feedbackList.filter((fb) => {
      // General feedback (no specific recipient) is visible to all
      if (fb.recipient_id === null) return true;

      // Users with no role see only general feedback
      if (!allowedSenderRoles) return false;

      // Sender's role must be in the visible set
      const senderRole = userRoleMap.get(fb.user_id);
      return senderRole ? allowedSenderRoles.includes(senderRole) : false;
    });
  }, [feedbackList, user?.is_admin, currentRole, userRoleMap]);

  async function handleGenerateSummary() {
    if (!user) return;
    setSummaryError(null);
    setSummaryResult(null);
    try {
      const result = await getFeedbackSummary({
        user_id: user.id,
        session_id: sessionId,
      }).unwrap();
      setSummaryResult(result);
      toast.success("AI summary generated!");
    } catch (err: unknown) {
      const detail =
        (err as { data?: { detail?: string } })?.data?.detail ??
        "Failed to generate summary";
      setSummaryError(detail);
      toast.error(detail);
    }
  }

  return (
    <div className="flex flex-col gap-6 mt-4">
      {/* ── Header ─────────────────────────────────── */}
      <div className="flex flex-col items-center gap-3 py-6 text-center">
        <div className="flex size-10 items-center justify-center rounded-full bg-primary/10">
          <Sparkles className="size-5 text-primary" />
        </div>
        <h3 className="text-lg font-semibold text-foreground">
          What are trainees saying about your session?
        </h3>

        {summaryResult ? (
          /* ── AI summary content ── */
          <div className="w-full max-w-2xl text-left space-y-3">
            {Object.entries(summaryResult.summaries).map(
              ([role, summary]) => (
                <div key={role}>
                  <h4 className="mb-1 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    From {role}s
                  </h4>
                  <p className="text-sm leading-relaxed text-foreground/80">
                    {summary}
                  </p>
                </div>
              ),
            )}
          </div>
        ) : summaryError ? (
          <p className="max-w-2xl text-sm text-left leading-relaxed text-destructive">
            {summaryError}
          </p>
        ) : user ? (
          <Button
            size="sm"
            variant="outline"
            disabled={summaryLoading}
            onClick={handleGenerateSummary}
          >
            {summaryLoading && (
              <Loader2 className="mr-1.5 h-3.5 w-3.5 animate-spin" />
            )}
            {summaryLoading ? (
              "Generating…"
            ) : (
              <>
                <Bot className="mr-1.5 h-4 w-4" />
                Generate Summary
              </>
            )}
          </Button>
        ) : feedbackLoading ? (
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        ) : (
          <p className="max-w-2xl text-sm text-left leading-relaxed text-foreground/70">
            {feedbackList.length > 0
              ? `${feedbackList.length} feedback submission(s) received.`
              : "No feedback yet. Be the first to share your thoughts!"}
          </p>
        )}
      </div>

      {/* ── Loading state ────────────────────────────── */}
      {feedbackLoading ? (
        <div className="flex items-center justify-center py-16">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : visibleFeedback.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
          <p className="text-lg">No feedback yet.</p>
          <p className="text-sm">
            Feedback will appear here once users submit them.
          </p>
        </div>
      ) : (
        <div className="flex flex-col gap-4 lg:flex-row lg:max-w-[600px]">
          {visibleFeedback.map((fb) => {
            const senderRole = userRoleMap.get(fb.user_id);
            return (
              <Card key={fb.id} className="min-w-[300px]">
                <CardHeader>
                  <div className="flex items-center gap-2.5">
                    <div className="flex size-9 items-center justify-center rounded-full bg-muted">
                      <User className="size-4 text-muted-foreground" />
                    </div>
                    <div className="flex flex-col">
                      <CardTitle className="text-sm font-medium">
                        {userMap.get(fb.user_id) ?? `User #${fb.user_id}`}
                      </CardTitle>
                      <div className="flex items-center gap-1.5">
                        {senderRole && (
                          <Badge
                            variant="secondary"
                            className="flex items-center gap-1 px-1.5 py-0 text-[10px] font-normal leading-none"
                          >
                            {ROLE_ICONS[senderRole]}
                            {senderRole.charAt(0) + senderRole.slice(1).toLowerCase()}
                          </Badge>
                        )}
                        <CardDescription className="text-xs">
                          {formatDateTimeLong(fb.submitted_at)}
                        </CardDescription>
                      </div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm leading-relaxed text-foreground/80">
                    {fb.text}
                  </p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
