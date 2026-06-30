"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";

import { useGetSessionQuery } from "@/lib/api/sessions/sessions.api";
import { useGetMyselfQuery } from "@/lib/api/user/user.api";
import { useCreateFeedbackSubmissionMutation } from "@/lib/api/feedback-submissions/feedback-submissions.api";

import TrainingMaterialsSection from "@/components/custom/session/training-materials-section";
import AssignmentsSection from "@/components/custom/session/assignments-section";
import FeedbackSection from "@/components/custom/session/feedback-section";

function getErrorDetail(err: unknown): string {
  const data = (err as { data?: { detail?: string; message?: string } })?.data;
  return data?.detail || data?.message || "An error occurred";
}

const formatDateTime = (date: Date | string) =>
  new Date(date).toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });

export default function SessionPage() {
  const params = useParams<{ id: string; session_id: string }>();
  const sessionId = Number(params.session_id);

  // ── Session data ─────────────────────────────────────────────────
  const {
    data: session,
    isLoading: sessionLoading,
    isError: sessionError,
  } = useGetSessionQuery(sessionId);
  const { data: user } = useGetMyselfQuery();

  // ── Feedback submission dialog ────────────────────────────────────
  const [isFeedbackOpen, setIsFeedbackOpen] = useState(false);
  const [feedbackText, setFeedbackText] = useState("");
  const [submitFeedback, { isLoading: isSubmittingFeedback }] =
    useCreateFeedbackSubmissionMutation();

  function resetFeedbackForm() {
    setFeedbackText("");
  }

  async function handleSubmitFeedback(e: React.FormEvent) {
    e.preventDefault();
    if (!feedbackText.trim() || !user || !session?.feedback_id) return;

    try {
      await submitFeedback({
        user_id: user.id,
        recipient_id: null,
        feedback_id: session.feedback_id,
        text: feedbackText,
      }).unwrap();
      toast.success("Feedback submitted successfully!");
      setIsFeedbackOpen(false);
      resetFeedbackForm();
    } catch (err) {
      toast.error(getErrorDetail(err));
    }
  }

  // ── Loading / error states ────────────────────────────────────────

  if (sessionLoading) {
    return (
      <div className="flex h-[70vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (sessionError || !session) {
    return (
      <div className="flex h-[70vh] items-center justify-center">
        <p className="text-muted-foreground">Session not found.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-8 w-full h-full px-8 pb-8">
      {/* ── Header ───────────────────────────────────────── */}
      <div className="flex flex-col gap-4 lg:flex-row">
        <div className="flex flex-col gap-4 lg:max-w-2/3">
          <h1 className="text-4xl text-foreground">{session.title}</h1>
          <p className="text-muted-foreground">{session.description}</p>
          <p className="text-sm text-muted-foreground">
            {formatDateTime(session.start_datetime)} —{" "}
            {formatDateTime(session.end_datetime)}
          </p>
        </div>
        <div className="flex flex-col gap-2 lg:ml-auto">
          <div className="flex flex-col gap-2 lg:flex-row">
            <Popover>
              <PopoverTrigger render={<Button>Join Session</Button>} />
              <PopoverContent className="w-44" align="end">
                <div className="flex flex-col gap-1 p-1">
                  <Button variant="ghost" className="w-full justify-start">
                    as moderator
                  </Button>
                  <Button variant="ghost" className="w-full justify-start">
                    as trainer
                  </Button>
                </div>
              </PopoverContent>
            </Popover>
            <Dialog
              open={isFeedbackOpen}
              onOpenChange={(open) => {
                setIsFeedbackOpen(open);
                if (!open) resetFeedbackForm();
              }}
            >
              <DialogTrigger
                render={
                  <Button variant="outline">Submit Feedback</Button>
                }
              />
              <DialogContent className="sm:max-w-lg">
                <form onSubmit={handleSubmitFeedback}>
                  <DialogHeader>
                    <DialogTitle>Submit Feedback</DialogTitle>
                    <DialogDescription>
                      Share your thoughts about this session.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="py-4">
                    <Textarea
                      placeholder="What did you think of the session? Any suggestions?"
                      className="h-40"
                      value={feedbackText}
                      onChange={(e) => setFeedbackText(e.target.value)}
                      rows={10}
                      required
                    />
                  </div>
                  <DialogFooter>
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => {
                        setIsFeedbackOpen(false);
                        resetFeedbackForm();
                      }}
                    >
                      Cancel
                    </Button>
                    <Button
                      type="submit"
                      disabled={!feedbackText.trim() || isSubmittingFeedback}
                    >
                      {isSubmittingFeedback && (
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      )}
                      Submit
                    </Button>
                  </DialogFooter>
                </form>
              </DialogContent>
            </Dialog>
          </div>
        </div>
      </div>

      {/* ── Tabs ──────────────────────────────────────────── */}
      <Tabs defaultValue="training_materials">
        <TabsList variant="line">
          <TabsTrigger value="training_materials">
            Training Materials
          </TabsTrigger>
          <TabsTrigger value="assignments">Assignments</TabsTrigger>
          <TabsTrigger value="feedback">Feedback</TabsTrigger>
        </TabsList>

        <TabsContent value="training_materials">
          <TrainingMaterialsSection sessionId={sessionId} user={user} />
        </TabsContent>

        <TabsContent value="assignments">
          <AssignmentsSection sessionId={sessionId} user={user} />
        </TabsContent>

        <TabsContent value="feedback">
          <FeedbackSection sessionId={sessionId} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
