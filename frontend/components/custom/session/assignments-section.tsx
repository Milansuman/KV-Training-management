"use client";

import { useState } from "react";
import {
  CalendarDays,
  Clock,
  ExternalLink,
  Eye,
  Plus,
  Trash2,
  User,
  Pencil,
  Loader2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { toast } from "sonner";

import {
  useGetAssignmentsBySessionIdQuery,
  useCreateAssignmentMutation,
  usePatchAssignmentMutation,
  useDeleteAssignmentMutation,
} from "@/lib/api/assignments/assignments.api";
import {
  useGetSubmissionsByAssignmentIdQuery,
  useCreateSubmissionMutation,
} from "@/lib/api/assignment-submissions/assignment-submissions.api";
import type { AssignmentResponse } from "@/lib/api/assignments/assignments.type";
import type { UserResponse } from "@/lib/api/user/user.type";

function getErrorDetail(err: unknown): string {
  const data = (err as { data?: { detail?: string; message?: string } })?.data;
  return data?.detail || data?.message || "An error occurred";
}

const formatDate = (dateStr: string) =>
  new Date(dateStr).toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    year: "numeric",
  });

const formatDateTimeLong = (dateStr: string) =>
  new Date(dateStr).toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });

interface AssignmentsSectionProps {
  sessionId: number;
  user: UserResponse | undefined;
  canManage: boolean;
}

export default function AssignmentsSection({
  sessionId,
  user,
  canManage,
}: AssignmentsSectionProps) {
  const { data: assignments = [], isLoading: assignmentsLoading } =
    useGetAssignmentsBySessionIdQuery(sessionId);
  const [createAssignment, { isLoading: isCreatingAssignment }] =
    useCreateAssignmentMutation();
  const [patchAssignment, { isLoading: isPatchingAssignment }] =
    usePatchAssignmentMutation();
  const [deleteAssignment] = useDeleteAssignmentMutation();

  // Create dialog
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newDescription, setNewDescription] = useState("");
  const [newDueAt, setNewDueAt] = useState("");

  // Update dialog
  const [isUpdateOpen, setIsUpdateOpen] = useState(false);
  const [editingAssignmentId, setEditingAssignmentId] = useState<
    number | null
  >(null);
  const [updateTitle, setUpdateTitle] = useState("");
  const [updateDescription, setUpdateDescription] = useState("");
  const [updateDueAt, setUpdateDueAt] = useState("");

  // Submissions dialog (view)
  const [isSubmissionsOpen, setIsSubmissionsOpen] = useState(false);
  const [viewingAssignmentId, setViewingAssignmentId] = useState<
    number | null
  >(null);
  const { data: viewingSubmissions = [] } =
    useGetSubmissionsByAssignmentIdQuery(viewingAssignmentId ?? 0, {
      skip: !viewingAssignmentId,
    });

  // Create submission dialog
  const [isCreateSubmissionOpen, setIsCreateSubmissionOpen] = useState(false);
  const [submitAssignmentId, setSubmitAssignmentId] = useState<number | null>(
    null,
  );
  const [newSubmissionUrl, setNewSubmissionUrl] = useState("");
  const [createSubmission, { isLoading: isCreatingSubmission }] =
    useCreateSubmissionMutation();

  function resetCreateForm() {
    setNewTitle("");
    setNewDescription("");
    setNewDueAt("");
  }

  function resetUpdateForm() {
    setEditingAssignmentId(null);
    setUpdateTitle("");
    setUpdateDescription("");
    setUpdateDueAt("");
  }

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!newTitle || !newDescription || !newDueAt) return;

    try {
      await createAssignment({
        title: newTitle,
        description: newDescription,
        session_id: sessionId,
        due_at: new Date(newDueAt).toISOString(),
      }).unwrap();
      toast.success("Assignment created successfully!");
      setIsCreateOpen(false);
      resetCreateForm();
    } catch (err) {
      toast.error(getErrorDetail(err));
    }
  }

  function handleEdit(assignment: AssignmentResponse) {
    setEditingAssignmentId(assignment.id);
    setUpdateTitle(assignment.title);
    setUpdateDescription(assignment.description);
    setUpdateDueAt(assignment.due_at);
    setIsUpdateOpen(true);
  }

  async function handleUpdate(e: React.FormEvent) {
    e.preventDefault();
    if (
      !editingAssignmentId ||
      !updateTitle ||
      !updateDescription ||
      !updateDueAt
    )
      return;

    try {
      await patchAssignment({
        assignmentId: editingAssignmentId,
        body: {
          title: updateTitle,
          description: updateDescription,
          due_at: new Date(updateDueAt).toISOString(),
        },
      }).unwrap();
      toast.success("Assignment updated successfully!");
      setIsUpdateOpen(false);
      resetUpdateForm();
    } catch (err) {
      toast.error(getErrorDetail(err));
    }
  }

  async function handleDelete(id: number) {
    try {
      await deleteAssignment(id).unwrap();
      toast.success("Assignment deleted successfully!");
    } catch (err) {
      toast.error(getErrorDetail(err));
    }
  }

  function handleViewSubmissions(assignmentId: number) {
    setViewingAssignmentId(assignmentId);
    setIsSubmissionsOpen(true);
  }

  function resetCreateSubmissionForm() {
    setSubmitAssignmentId(null);
    setNewSubmissionUrl("");
  }

  function handleOpenCreateSubmission(assignmentId: number) {
    setSubmitAssignmentId(assignmentId);
    setIsCreateSubmissionOpen(true);
  }

  async function handleCreateSubmission(e: React.FormEvent) {
    e.preventDefault();
    if (!submitAssignmentId || !newSubmissionUrl || !user) return;

    try {
      await createSubmission({
        url: newSubmissionUrl,
        user_id: user.id,
        assignment_id: submitAssignmentId,
      }).unwrap();
      toast.success("Submission created successfully!");
      setIsCreateSubmissionOpen(false);
      resetCreateSubmissionForm();
    } catch (err) {
      toast.error(getErrorDetail(err));
    }
  }

  return (
    <div className="flex flex-col gap-6 mt-4">
      <div className="flex items-center justify-between">
        <Dialog
          open={isCreateOpen}
          onOpenChange={(open) => {
            setIsCreateOpen(open);
            if (!open) resetCreateForm();
          }}
        >
          {canManage && (
            <DialogTrigger
              render={
                <Button>
                  <Plus data-icon="inline-start" />
                  Create Assignment
                </Button>
              }
            />
          )}
          <DialogContent className="sm:max-w-lg">
            <form onSubmit={handleCreate}>
              <DialogHeader>
                <DialogTitle>Create Assignment</DialogTitle>
                <DialogDescription>
                  Fill in the details below to create a new assignment.
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-5 py-4">
                <div className="grid gap-2">
                  <Label htmlFor="new-title">
                    Title <span className="text-destructive">*</span>
                  </Label>
                  <Input
                    id="new-title"
                    placeholder="e.g. React Basics Exercise"
                    value={newTitle}
                    onChange={(e) => setNewTitle(e.target.value)}
                    required
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="new-description">
                    Description{" "}
                    <span className="text-destructive">*</span>
                  </Label>
                  <Textarea
                    id="new-description"
                    placeholder="Describe what students need to do…"
                    value={newDescription}
                    onChange={(e) => setNewDescription(e.target.value)}
                    required
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="new-due">
                    Due Date & Time{" "}
                    <span className="text-destructive">*</span>
                  </Label>
                  <Input
                    id="new-due"
                    type="datetime-local"
                    value={newDueAt}
                    onChange={(e) => setNewDueAt(e.target.value)}
                    required
                  />
                </div>
              </div>
              <DialogFooter>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setIsCreateOpen(false)}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={isCreatingAssignment}>
                  {isCreatingAssignment && (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  )}
                  Create Assignment
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {assignmentsLoading ? (
        <div className="flex items-center justify-center py-16">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : assignments.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
          <p className="text-lg">No assignments yet.</p>
          <p className="text-sm">Create one to get started.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {assignments.map((assignment) => (
            <div key={assignment.id}>
              <Card className="flex flex-col">
                <CardHeader>
                  <div className="flex items-start justify-between gap-3">
                    <CardTitle className="text-base">
                      {assignment.title}
                    </CardTitle>
                    {canManage && (
                      <div className="flex shrink-0 items-center gap-1">
                        <button
                          type="button"
                          onClick={() => handleEdit(assignment)}
                          className="rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-primary/10 hover:text-primary"
                        >
                          <Pencil className="size-4" />
                        </button>
                        <button
                          type="button"
                          onClick={() => handleDelete(assignment.id)}
                          className="rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-destructive/10 hover:text-destructive"
                        >
                          <Trash2 className="size-4" />
                        </button>
                      </div>
                    )}
                  </div>
                  <CardDescription className="line-clamp-3">
                    {assignment.description}
                  </CardDescription>
                </CardHeader>
                <CardContent className="mt-auto">
                  <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                    <CalendarDays className="size-3.5 shrink-0" />
                    <span>Due {formatDate(assignment.due_at)}</span>
                  </div>
                </CardContent>
                <CardFooter className="flex-col gap-2">
                  <Button
                    size="sm"
                    className="w-full"
                    onClick={() =>
                      handleOpenCreateSubmission(assignment.id)
                    }
                  >
                    <Plus data-icon="inline-start" />
                    Submit
                  </Button>
                  <Button
                    size="sm"
                    variant="secondary"
                    className="w-full"
                    onClick={() =>
                      handleViewSubmissions(assignment.id)
                    }
                  >
                    <Eye data-icon="inline-start" />
                    View Submissions
                  </Button>
                </CardFooter>
              </Card>

              {/* ── Update Assignment Dialog ──────────────── */}
              <Dialog
                open={
                  isUpdateOpen &&
                  editingAssignmentId === assignment.id
                }
                onOpenChange={(open) => {
                  setIsUpdateOpen(open);
                  if (!open) resetUpdateForm();
                }}
              >
                <DialogContent className="sm:max-w-lg">
                  <form onSubmit={handleUpdate}>
                    <DialogHeader>
                      <DialogTitle>Edit Assignment</DialogTitle>
                      <DialogDescription>
                        Update the details for this assignment.
                      </DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-5 py-4">
                      <div className="grid gap-2">
                        <Label htmlFor="update-title">
                          Title{" "}
                          <span className="text-destructive">*</span>
                        </Label>
                        <Input
                          id="update-title"
                          value={updateTitle}
                          onChange={(e) => setUpdateTitle(e.target.value)}
                          required
                        />
                      </div>
                      <div className="grid gap-2">
                        <Label htmlFor="update-description">
                          Description{" "}
                          <span className="text-destructive">*</span>
                        </Label>
                        <Textarea
                          id="update-description"
                          value={updateDescription}
                          onChange={(e) =>
                            setUpdateDescription(e.target.value)
                          }
                          required
                        />
                      </div>
                      <div className="grid gap-2">
                        <Label htmlFor="update-due">
                          Due Date & Time{" "}
                          <span className="text-destructive">*</span>
                        </Label>
                        <Input
                          id="update-due"
                          type="datetime-local"
                          value={updateDueAt}
                          onChange={(e) => setUpdateDueAt(e.target.value)}
                          required
                        />
                      </div>
                    </div>
                    <DialogFooter>
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => {
                          setIsUpdateOpen(false);
                          resetUpdateForm();
                        }}
                      >
                        Cancel
                      </Button>
                      <Button type="submit" disabled={isPatchingAssignment}>
                        {isPatchingAssignment && (
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        )}
                        Update Assignment
                      </Button>
                    </DialogFooter>
                  </form>
                </DialogContent>
              </Dialog>

              {/* ── Create Submission Dialog ──────────────── */}
              <Dialog
                open={
                  isCreateSubmissionOpen &&
                  submitAssignmentId === assignment.id
                }
                onOpenChange={(open) => {
                  setIsCreateSubmissionOpen(open);
                  if (!open) resetCreateSubmissionForm();
                }}
              >
                <DialogContent className="sm:max-w-md">
                  <form onSubmit={handleCreateSubmission}>
                    <DialogHeader>
                      <DialogTitle>Submit Assignment</DialogTitle>
                      <DialogDescription>
                        Provide the URL of your completed work to submit it.
                      </DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                      <div className="grid gap-2">
                        <Label htmlFor="sub-url">
                          Submission URL{" "}
                          <span className="text-destructive">*</span>
                        </Label>
                        <Input
                          id="sub-url"
                          type="url"
                          placeholder="https://github.com/user/repo"
                          value={newSubmissionUrl}
                          onChange={(e) =>
                            setNewSubmissionUrl(e.target.value)
                          }
                          required
                        />
                      </div>
                    </div>
                    <DialogFooter>
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => {
                          setIsCreateSubmissionOpen(false);
                          resetCreateSubmissionForm();
                        }}
                      >
                        Cancel
                      </Button>
                      <Button
                        type="submit"
                        disabled={isCreatingSubmission}
                      >
                        {isCreatingSubmission && (
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        )}
                        Submit
                      </Button>
                    </DialogFooter>
                  </form>
                </DialogContent>
              </Dialog>
            </div>
          ))}
        </div>
      )}

      {/* ── View Submissions Dialog (global, not per-card) ── */}
      <Dialog
        open={isSubmissionsOpen}
        onOpenChange={setIsSubmissionsOpen}
      >
        <DialogContent className="sm:max-w-2xl">
          <DialogHeader>
            <DialogTitle>Submissions</DialogTitle>
            <DialogDescription>
              View all student submissions for this assignment.
            </DialogDescription>
          </DialogHeader>
          {viewingSubmissions.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-10 text-muted-foreground">
              <p className="text-sm">No submissions yet.</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>User</TableHead>
                  <TableHead>Submission URL</TableHead>
                  <TableHead>Submitted At</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {viewingSubmissions.map((sub) => (
                  <TableRow key={sub.id}>
                    <TableCell className="font-medium">
                      <div className="flex items-center gap-2">
                        <User className="size-4 text-muted-foreground" />
                        User #{sub.user_id}
                      </div>
                    </TableCell>
                    <TableCell>
                      <a
                        href={sub.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 text-primary underline underline-offset-2 hover:text-primary/80"
                      >
                        <ExternalLink className="size-3.5" />
                        {sub.url.length > 40
                          ? sub.url.slice(0, 40) + "…"
                          : sub.url}
                      </a>
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      <div className="flex items-center gap-1.5">
                        <Clock className="size-3.5" />
                        {formatDateTimeLong(sub.created_at)}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
          <DialogFooter showCloseButton />
        </DialogContent>
      </Dialog>
    </div>
  );
}
