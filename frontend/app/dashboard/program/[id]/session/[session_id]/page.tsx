"use client";

import { useState, useMemo } from "react";
import { useParams } from "next/navigation";
import { GraduationCap, Loader2, UserCog, Users } from "lucide-react";
import { Badge } from "@/components/ui/badge";
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
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "sonner";

import {
  useGetSessionQuery,
  useGetSessionTopicsQuery,
} from "@/lib/api/sessions/sessions.api";
import { useGetMyselfQuery } from "@/lib/api/user/user.api";
import { useGetSessionUsersQuery, useAddSessionPermissionMutation } from "@/lib/api/session-permissions/session-permissions.api";
import { useCreateFeedbackSubmissionMutation } from "@/lib/api/feedback-submissions/feedback-submissions.api";
import type { SessionUserResponse } from "@/lib/api/session-permissions/session-permissions.type";
import { useProgramPermissions } from "@/hooks/use-program-permissions";

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
  const programId = Number(params.id);
  const sessionId = Number(params.session_id);
  const perms = useProgramPermissions(programId);

  // ── Session data ─────────────────────────────────────────────────
  const {
    data: session,
    isLoading: sessionLoading,
    isError: sessionError,
  } = useGetSessionQuery(sessionId);
  const { data: topics = [] } = useGetSessionTopicsQuery(sessionId);
  const { data: user } = useGetMyselfQuery();

  // ── Session users (trainers / moderators) ────────────────────────
  const { data: sessionUsers = [] } = useGetSessionUsersQuery(sessionId);

  const [addSessionPermission, { isLoading: isJoining }] =
    useAddSessionPermissionMutation();
  const [isUsersDialogOpen, setIsUsersDialogOpen] = useState(false);

  async function handleJoinSession(role: "TRAINER" | "MODERATOR") {
    if (!user) return;
    try {
      await addSessionPermission({
        user_id: user.id,
        session_id: sessionId,
        role,
      }).unwrap();
      toast.success(`You joined as ${role.toLowerCase()}!`);
    } catch (err) {
      toast.error(getErrorDetail(err));
    }
  }

  const { trainers, moderators, candidates } = useMemo(() => {
    const trainers: SessionUserResponse[] = [];
    const moderators: SessionUserResponse[] = [];
    const candidates: SessionUserResponse[] = [];
    for (const u of sessionUsers) {
      if (u.role === "TRAINER") trainers.push(u);
      else if (u.role === "MODERATOR") moderators.push(u);
      else if (u.role === "CANDIDATE") candidates.push(u);
    }
    return { trainers, moderators, candidates };
  }, [sessionUsers]);

  // ── Feedback submission dialog ────────────────────────────────────
  const [isFeedbackOpen, setIsFeedbackOpen] = useState(false);
  const [feedbackText, setFeedbackText] = useState("");
  const [selectedRecipientId, setSelectedRecipientId] = useState<
    number | null
  >(null);
  const [submitFeedback, { isLoading: isSubmittingFeedback }] =
    useCreateFeedbackSubmissionMutation();

  // Current user's role in this session
  const mySessionRole = useMemo(() => {
    if (!user) return null;
    const me = sessionUsers.find((u) => u.user_id === user.id);
    return me?.role ?? null;
  }, [sessionUsers, user]);

  // Available recipients based on role
  const availableRecipients = useMemo(() => {
    if (user?.is_admin || perms.isStaff) {
      return [...trainers, ...moderators, ...candidates];
    }
    if (mySessionRole === "MODERATOR") {
      return [...trainers, ...candidates];
    }
    if (mySessionRole === "TRAINER") {
      return [...candidates];
    }
    return [];
  }, [user, perms, mySessionRole, trainers, moderators, candidates]);

  // Whether the user can select a recipient (candidates cannot)
  const canSelectRecipient = availableRecipients.length > 0;

  // Display name for the selected recipient
  const selectedRecipientName =
    selectedRecipientId != null
      ? availableRecipients.find(
          (u) => u.user_id === selectedRecipientId,
        )?.display_name ?? null
      : null;

  function resetFeedbackForm() {
    setFeedbackText("");
    setSelectedRecipientId(null);
  }

  async function handleSubmitFeedback(e: React.FormEvent) {
    e.preventDefault();
    if (!feedbackText.trim() || !user || !session?.feedback_id) return;

    try {
      await submitFeedback({
        user_id: user.id,
        recipient_id: selectedRecipientId,
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

          {topics.length > 0 && (
            <div className="flex flex-wrap items-center gap-2">
              {topics.map((topic) => (
                <Badge key={topic.id} variant="secondary">
                  {topic.title}
                </Badge>
              ))}
            </div>
          )}

          <p className="text-sm text-muted-foreground">
            {formatDateTime(session.start_datetime)} —{" "}
            {formatDateTime(session.end_datetime)}
          </p>

          {/* ── Trainers & Moderators ──────────────────────── */}
          {(trainers.length > 0 || moderators.length > 0) && (
            <div className="flex flex-wrap items-center gap-2">
              {trainers.length > 0 && (
                <div className="flex items-center gap-1.5 rounded-full border bg-muted/50 px-3 py-1 text-xs font-medium text-muted-foreground">
                  <GraduationCap className="h-3.5 w-3.5" />
                  <span>
                    {trainers
                      .slice(0, 3)
                      .map((t) => t.display_name)
                      .join(", ")}
                    {trainers.length > 3 &&
                      ` +${trainers.length - 3} more`}
                  </span>
                </div>
              )}
              {moderators.length > 0 && (
                <div className="flex items-center gap-1.5 rounded-full border bg-muted/50 px-3 py-1 text-xs font-medium text-muted-foreground">
                  <UserCog className="h-3.5 w-3.5" />
                  <span>
                    {moderators
                      .slice(0, 3)
                      .map((m) => m.display_name)
                      .join(", ")}
                    {moderators.length > 3 &&
                      ` +${moderators.length - 3} more`}
                  </span>
                </div>
              )}
              <Button
                variant="ghost"
                size="sm"
                className="h-7 text-xs"
                onClick={() => setIsUsersDialogOpen(true)}
              >
                <Users className="mr-1 h-3.5 w-3.5" />
                Show More
              </Button>

              {/* ── Users dialog ────────────────────────── */}
              <Dialog
                open={isUsersDialogOpen}
                onOpenChange={setIsUsersDialogOpen}
              >
                <DialogContent className="sm:max-w-lg">
                  <DialogHeader>
                    <DialogTitle>
                      Session Users
                    </DialogTitle>
                    <DialogDescription>
                      All trainers and moderators assigned to
                      this session.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="max-h-80 space-y-4 overflow-y-auto">
                    {trainers.length > 0 && (
                      <div>
                        <h4 className="mb-2 flex items-center gap-1.5 text-sm font-semibold text-foreground">
                          <GraduationCap className="h-4 w-4" />
                          Trainers
                        </h4>
                        <div className="space-y-1">
                          {trainers.map((t) => (
                            <div
                              key={t.id}
                              className="flex items-center justify-between rounded-md bg-muted/50 px-3 py-2 text-sm"
                            >
                              <span className="font-medium">
                                {t.display_name}
                              </span>
                              <span className="text-xs text-muted-foreground">
                                {t.email}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    {moderators.length > 0 && (
                      <div>
                        <h4 className="mb-2 flex items-center gap-1.5 text-sm font-semibold text-foreground">
                          <UserCog className="h-4 w-4" />
                          Moderators
                        </h4>
                        <div className="space-y-1">
                          {moderators.map((m) => (
                            <div
                              key={m.id}
                              className="flex items-center justify-between rounded-md bg-muted/50 px-3 py-2 text-sm"
                            >
                              <span className="font-medium">
                                {m.display_name}
                              </span>
                              <span className="text-xs text-muted-foreground">
                                {m.email}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                  <DialogFooter>
                    <Button
                      variant="outline"
                      onClick={() =>
                        setIsUsersDialogOpen(false)
                      }
                    >
                      Close
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </div>
          )}
        </div>
        <div className="flex flex-col gap-2 lg:ml-auto">
          <div className="flex flex-col gap-2 lg:flex-row">
            {user?.is_admin || perms.isStaff ? (
              <Popover>
                <PopoverTrigger render={<Button>Join Session</Button>} />
                <PopoverContent className="w-44" align="end">
                  <div className="flex flex-col gap-1 p-1">
                    <Button
                      variant="ghost"
                      className="w-full justify-start"
                      disabled={isJoining}
                      onClick={() => handleJoinSession("MODERATOR")}
                    >
                      as moderator
                    </Button>
                    <Button
                      variant="ghost"
                      className="w-full justify-start"
                      disabled={isJoining}
                      onClick={() => handleJoinSession("TRAINER")}
                    >
                      as trainer
                    </Button>
                  </div>
                </PopoverContent>
              </Popover>
            ) : null}
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
              <div className="flex flex-col gap-4 py-4">
                <Textarea
                  placeholder="What did you think of the session? Any suggestions?"
                  className="h-40"
                  value={feedbackText}
                  onChange={(e) => setFeedbackText(e.target.value)}
                  rows={10}
                  required
                />

                {canSelectRecipient && (
                  <div className="flex flex-col gap-2">
                    <Label htmlFor="recipient">
                      Send feedback to
                    </Label>
                    <Select
                      value={selectedRecipientId?.toString() ?? ""}
                      onValueChange={(val) =>
                        setSelectedRecipientId(
                          val ? Number(val) : null,
                        )
                      }
                    >
                      <SelectTrigger
                        id="recipient"
                        className="w-full"
                      >
                        <SelectValue placeholder="Select a user…">
                          {selectedRecipientName ??
                            "Select a user…"}
                        </SelectValue>
                      </SelectTrigger>
                      <SelectContent>
                        {mySessionRole === "MODERATOR" &&
                          trainers.length > 0 && (
                            <SelectGroup>
                              <SelectLabel>
                                Trainers
                              </SelectLabel>
                              {trainers.map((t) => (
                                <SelectItem
                                  key={t.user_id}
                                  value={t.user_id.toString()}
                                >
                                  {t.display_name}
                                </SelectItem>
                              ))}
                            </SelectGroup>
                          )}
                        {candidates.length > 0 && (
                          <SelectGroup>
                            {(mySessionRole === "MODERATOR" ||
                              mySessionRole === "TRAINER" ||
                              user?.is_admin ||
                              perms.isStaff) && (
                              <SelectLabel>
                                Candidates
                              </SelectLabel>
                            )}
                            {candidates.map((c) => (
                              <SelectItem
                                key={c.user_id}
                                value={c.user_id.toString()}
                              >
                                {c.display_name}
                              </SelectItem>
                            ))}
                          </SelectGroup>
                        )}
                        {(user?.is_admin || perms.isStaff) &&
                          moderators.length > 0 && (
                            <SelectGroup>
                              <SelectLabel>
                                Moderators
                              </SelectLabel>
                              {moderators.map((m) => (
                                <SelectItem
                                  key={m.user_id}
                                  value={m.user_id.toString()}
                                >
                                  {m.display_name}
                                </SelectItem>
                              ))}
                            </SelectGroup>
                          )}
                        {(user?.is_admin || perms.isStaff) &&
                          trainers.length > 0 && (
                            <SelectGroup>
                              <SelectLabel>
                                Trainers
                              </SelectLabel>
                              {trainers.map((t) => (
                                <SelectItem
                                  key={t.user_id}
                                  value={t.user_id.toString()}
                                >
                                  {t.display_name}
                                </SelectItem>
                              ))}
                            </SelectGroup>
                          )}
                      </SelectContent>
                    </Select>
                  </div>
                )}
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
          <TrainingMaterialsSection
            sessionId={sessionId}
            user={user}
            canManage={perms.canManageSessionContent(sessionId)}
            topics={topics}
          />
        </TabsContent>

        <TabsContent value="assignments">
          <AssignmentsSection
            sessionId={sessionId}
            user={user}
            canManage={perms.canManageSessionContent(sessionId)}
            sessionRole={perms.getSessionRole(sessionId)}
          />
        </TabsContent>

        <TabsContent value="feedback">
          <FeedbackSection sessionId={sessionId} user={user} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
