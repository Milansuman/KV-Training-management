"use client";

import { Loader2, Sparkles, User } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import { useGetFeedbackSubmissionsBySessionQuery } from "@/lib/api/feedback/feedback.api";

const formatDateTimeLong = (dateStr: string) =>
  new Date(dateStr).toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });

interface FeedbackSectionProps {
  sessionId: number;
}

export default function FeedbackSection({ sessionId }: FeedbackSectionProps) {
  const { data: feedbackList = [], isLoading: feedbackLoading } =
    useGetFeedbackSubmissionsBySessionQuery(sessionId);

  return (
    <div className="flex flex-col gap-6 mt-4">
      <div className="flex flex-col items-center gap-3 py-6 text-center">
        <div className="flex size-10 items-center justify-center rounded-full bg-primary/10">
          <Sparkles className="size-5 text-primary" />
        </div>
        <h3 className="text-lg font-semibold text-foreground">
          What are trainees saying about your session?
        </h3>
        {feedbackLoading ? (
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        ) : (
          <p className="max-w-2xl text-sm text-left leading-relaxed text-foreground/70">
            {feedbackList.length > 0
              ? `${feedbackList.length} feedback submission(s) received.`
              : "No feedback yet. Be the first to share your thoughts!"}
          </p>
        )}
      </div>

      {feedbackLoading ? (
        <div className="flex items-center justify-center py-16">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : feedbackList.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
          <p className="text-lg">No feedback yet.</p>
          <p className="text-sm">
            Feedback will appear here once users submit them.
          </p>
        </div>
      ) : (
        <div className="flex flex-col gap-4 lg:flex-row lg:max-w-[600px]">
          {feedbackList.map((fb) => (
            <Card key={fb.id} className="min-w-[300px]">
              <CardHeader>
                <div className="flex items-center gap-2.5">
                  <div className="flex size-9 items-center justify-center rounded-full bg-muted">
                    <User className="size-4 text-muted-foreground" />
                  </div>
                  <div className="flex flex-col">
                    <CardTitle className="text-sm font-medium">
                      User #{fb.user_id}
                    </CardTitle>
                    <CardDescription className="text-xs">
                      {formatDateTimeLong(fb.submitted_at)}
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm leading-relaxed text-foreground/80">
                  {fb.text}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
