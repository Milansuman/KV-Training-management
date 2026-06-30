"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import {
  ExternalLink,
  File,
  Link,
  Plus,
  Trash2,
  User,
  Pencil,
  Clock,
  Eye,
  CalendarDays,
  Sparkles,
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
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

import { useGetSessionQuery } from "@/lib/api/sessions/sessions.api";
import { useGetMyselfQuery } from "@/lib/api/user/user.api";
import {
  useGetTrainingMaterialsBySessionQuery,
  useUploadTrainingMaterialMutation,
  useCreateMaterialFromUrlMutation,
  useUpdateTrainingMaterialMutation,
  useDeleteTrainingMaterialMutation,
} from "@/lib/api/training-materials/training-materials.api";
import { useGetFeedbackSubmissionsBySessionQuery } from "@/lib/api/feedback/feedback.api";
import { useCreateFeedbackSubmissionMutation } from "@/lib/api/feedback-submissions/feedback-submissions.api";
import {
  useGetAssignmentsBySessionIdQuery,
  useCreateAssignmentMutation,
  usePatchAssignmentMutation,
  useDeleteAssignmentMutation,
} from "@/lib/api/assignments/assignments.api";
import {
  useGetSubmissionsByAssignmentIdQuery,
} from "@/lib/api/assignment-submissions/assignment-submissions.api";
import type { TrainingMaterialResponse } from "@/lib/api/training-materials/training-materials.type";
import type { AssignmentResponse } from "@/lib/api/assignments/assignments.type";
import { toast } from "sonner";

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

  // ── Training Materials ────────────────────────────────────────────
  const { data: materials = [], isLoading: materialsLoading } =
    useGetTrainingMaterialsBySessionQuery(sessionId);
  const [uploadMaterial, { isLoading: isUploading }] =
    useUploadTrainingMaterialMutation();
  const [createFromUrl, { isLoading: isCreatingUrl }] =
    useCreateMaterialFromUrlMutation();
  const [updateMaterial, { isLoading: isUpdatingMaterial }] =
    useUpdateTrainingMaterialMutation();
  const [deleteMaterial] =
    useDeleteTrainingMaterialMutation();

  // ── Feedback ──────────────────────────────────────────────────────
  const { data: feedbackList = [], isLoading: feedbackLoading } =
    useGetFeedbackSubmissionsBySessionQuery(sessionId);
  const [submitFeedback, { isLoading: isSubmittingFeedback }] =
    useCreateFeedbackSubmissionMutation();

  // ── Assignments ────────────────────────────────────────────────────
  const { data: assignments = [], isLoading: assignmentsLoading } =
    useGetAssignmentsBySessionIdQuery(sessionId);
  const [createAssignment, { isLoading: isCreatingAssignment }] =
    useCreateAssignmentMutation();
  const [patchAssignment, { isLoading: isPatchingAssignment }] =
    usePatchAssignmentMutation();
  const [deleteAssignment] =
    useDeleteAssignmentMutation();

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

  // Submissions dialog
  const [isSubmissionsOpen, setIsSubmissionsOpen] = useState(false);
  const [viewingAssignmentId, setViewingAssignmentId] = useState<
    number | null
  >(null);
  const { data: viewingSubmissions = [] } =
    useGetSubmissionsByAssignmentIdQuery(viewingAssignmentId ?? 0, {
      skip: !viewingAssignmentId,
    });


  // Material add dialog
  const [isMaterialAddOpen, setIsMaterialAddOpen] = useState(false);
  const [materialTitle, setMaterialTitle] = useState("");
  const [materialUrl, setMaterialUrl] = useState("");
  const [materialFile, setMaterialFile] = useState<File | null>(null);
  const [materialTab, setMaterialTab] = useState<"url" | "file">("url");

  // Material update dialog
  const [isMaterialUpdateOpen, setIsMaterialUpdateOpen] = useState(false);
  const [editingMaterialId, setEditingMaterialId] = useState<number | null>(
    null,
  );
  const [updateMaterialTitle, setUpdateMaterialTitle] = useState("");
  const [updateMaterialUrl, setUpdateMaterialUrl] = useState("");

  // Feedback dialog
  const [isFeedbackOpen, setIsFeedbackOpen] = useState(false);
  const [feedbackText, setFeedbackText] = useState("");

  const [deletingMaterialId, setDeletingMaterialId] = useState<number | null>(
    null,
  );

  // ── Material handlers ─────────────────────────────────────────────

  function resetMaterialAddForm() {
    setMaterialTitle("");
    setMaterialUrl("");
    setMaterialFile(null);
    setMaterialTab("url");
  }

  async function handleAddMaterial(e: React.FormEvent) {
    e.preventDefault();
    if (!materialTitle || !user) return;

    try {
      if (materialTab === "url") {
        if (!materialUrl) {
          toast.error("Please enter a URL.");
          return;
        }
        await createFromUrl({
          title: materialTitle,
          url: materialUrl,
          session_id: sessionId,
          user_id: user.id,
        }).unwrap();
        toast.success("Material added successfully!");
      } else {
        if (!materialFile) {
          toast.error("Please select a file.");
          return;
        }
        await uploadMaterial({
          title: materialTitle,
          session_id: sessionId,
          user_id: user.id,
          file: materialFile,
        }).unwrap();
        toast.success("Material uploaded successfully!");
      }
      setIsMaterialAddOpen(false);
      resetMaterialAddForm();
    } catch (err) {
      toast.error(getErrorDetail(err));
    }
  }

  function handleEditMaterial(material: TrainingMaterialResponse) {
    setEditingMaterialId(material.id);
    setUpdateMaterialTitle(material.title);
    setUpdateMaterialUrl(material.material_type === "url" ? material.url : "");
    setIsMaterialUpdateOpen(true);
  }

  async function handleUpdateMaterial(e: React.FormEvent) {
    e.preventDefault();
    if (!editingMaterialId || !updateMaterialTitle) return;

    try {
      await updateMaterial({
        materialId: editingMaterialId,
        title: updateMaterialTitle,
        url: updateMaterialUrl || null,
      }).unwrap();
      toast.success("Material updated successfully!");
      setIsMaterialUpdateOpen(false);
      setEditingMaterialId(null);
      setUpdateMaterialTitle("");
      setUpdateMaterialUrl("");
    } catch (err) {
      toast.error(getErrorDetail(err));
    }
  }

  async function handleDeleteMaterial(materialId: number) {
    setDeletingMaterialId(materialId);
    try {
      await deleteMaterial(materialId).unwrap();
      toast.success("Material deleted successfully!");
    } catch (err) {
      toast.error(getErrorDetail(err));
    } finally {
      setDeletingMaterialId(null);
    }
  }

  // ── Feedback handlers ────────────────────────────────────────────

  function resetFeedbackForm() {
    setFeedbackText("");
  }

  async function handleSubmitFeedback(e: React.FormEvent) {
    e.preventDefault();
    if (!feedbackText.trim() || !user) return;

    try {
      await submitFeedback({
        user_id: user.id,
        recipient_id: null,
        feedback_id: sessionId,
        text: feedbackText,
      }).unwrap();
      toast.success("Feedback submitted successfully!");
      setIsFeedbackOpen(false);
      resetFeedbackForm();
    } catch (err) {
      toast.error(getErrorDetail(err));
    }
  }

  // ── Assignment handlers (placeholder) ─────────────────────────────

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

        {/* ── Training Materials Tab ────────────────────────── */}
        <TabsContent value="training_materials">
          <div className="flex flex-col gap-6 mt-4">
            <div className="flex items-center justify-between">
              <Dialog
                open={isMaterialAddOpen}
                onOpenChange={(open) => {
                  setIsMaterialAddOpen(open);
                  if (!open) resetMaterialAddForm();
                }}
              >
                <DialogTrigger
                  render={
                    <Button>
                      <Plus data-icon="inline-start" />
                      Add Material
                    </Button>
                  }
                />
                <DialogContent className="sm:max-w-md">
                  <form onSubmit={handleAddMaterial}>
                    <DialogHeader>
                      <DialogTitle>Add Training Material</DialogTitle>
                      <DialogDescription>
                        Provide a title and either a URL or upload a file.
                      </DialogDescription>
                    </DialogHeader>
                    <div className="flex flex-col gap-4 py-4">
                      <div className="flex flex-col gap-2">
                        <Label>
                          Title <span className="text-destructive">*</span>
                        </Label>
                        <Input
                          placeholder="e.g. Course Slides"
                          value={materialTitle}
                          onChange={(e) => setMaterialTitle(e.target.value)}
                          required
                        />
                      </div>
                      <Tabs
                        value={materialTab}
                        onValueChange={(v) =>
                          setMaterialTab(v as "url" | "file")
                        }
                      >
                        <TabsList className="w-full" variant="line">
                          <TabsTrigger className="flex-1" value="url">
                            URL
                          </TabsTrigger>
                          <TabsTrigger className="flex-1" value="file">
                            File Upload
                          </TabsTrigger>
                        </TabsList>
                        <TabsContent value="url">
                          <Input
                            placeholder="https://example.com/material"
                            value={materialUrl}
                            onChange={(e) => setMaterialUrl(e.target.value)}
                          />
                        </TabsContent>
                        <TabsContent value="file">
                          <Input
                            type="file"
                            onChange={(e) =>
                              setMaterialFile(e.target.files?.[0] ?? null)
                            }
                          />
                        </TabsContent>
                      </Tabs>
                    </div>
                    <DialogFooter>
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => setIsMaterialAddOpen(false)}
                      >
                        Cancel
                      </Button>
                      <Button
                        type="submit"
                        disabled={isUploading || isCreatingUrl}
                      >
                        {(isUploading || isCreatingUrl) && (
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        )}
                        {materialTab === "url" ? "Add URL" : "Upload File"}
                      </Button>
                    </DialogFooter>
                  </form>
                </DialogContent>
              </Dialog>
            </div>

            {materialsLoading ? (
              <div className="flex items-center justify-center py-16">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
              </div>
            ) : materials.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
                <p className="text-lg">No materials yet.</p>
                <p className="text-sm">Add one to get started.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {materials.map((material) => (
                  <div key={material.id}>
                    <Card>
                      <CardHeader>
                        <div className="flex items-center gap-2">
                          {material.material_type === "url" ? (
                            <Link className="size-4 shrink-0 text-muted-foreground" />
                          ) : (
                            <File className="size-4 shrink-0 text-muted-foreground" />
                          )}
                          <CardTitle>{material.title}</CardTitle>
                        </div>
                        <CardDescription>
                          {material.material_type === "url"
                            ? material.url
                            : material.url
                              ? material.url.split("/").pop()
                              : "File"}
                        </CardDescription>
                      </CardHeader>
                      <CardContent>
                        <span className="inline-flex items-center gap-1.5 rounded-md bg-muted px-2 py-0.5 text-xs font-medium text-muted-foreground">
                          {material.material_type === "url" ? (
                            <>
                              <Link className="size-3" />
                              URL
                            </>
                          ) : (
                            <>
                              <File className="size-3" />
                              File
                            </>
                          )}
                        </span>
                      </CardContent>
                      <CardFooter>
                        {material.material_type === "url" ? (
                          <a
                            href={material.url}
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            <Button size="sm" variant="ghost" type="button">
                              <ExternalLink data-icon="inline-start" />
                              Open
                            </Button>
                          </a>
                        ) : (
                          <a
                            href={material.url}
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            <Button size="sm" variant="ghost" type="button">
                              <File data-icon="inline-start" />
                              Download
                            </Button>
                          </a>
                        )}
                        {user?.is_admin && (
                          <div className="ml-auto flex items-center gap-1">
                            <button
                              type="button"
                              onClick={() => handleEditMaterial(material)}
                              className="rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-primary/10 hover:text-primary"
                            >
                              <Pencil className="size-4" />
                            </button>
                            <button
                              type="button"
                              onClick={() => handleDeleteMaterial(material.id)}
                              disabled={deletingMaterialId === material.id}
                              className="rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-destructive/10 hover:text-destructive disabled:opacity-50"
                            >
                              {deletingMaterialId === material.id ? (
                                <Loader2 className="size-4 animate-spin" />
                              ) : (
                                <Trash2 className="size-4" />
                              )}
                            </button>
                          </div>
                        )}
                      </CardFooter>
                    </Card>

                    {/* ── Update Material Dialog ────────────────── */}
                    <Dialog
                      open={
                        isMaterialUpdateOpen &&
                        editingMaterialId === material.id
                      }
                      onOpenChange={(open) => {
                        setIsMaterialUpdateOpen(open);
                        if (!open) {
                          setEditingMaterialId(null);
                          setUpdateMaterialTitle("");
                          setUpdateMaterialUrl("");
                        }
                      }}
                    >
                      <DialogContent className="sm:max-w-md">
                        <form onSubmit={handleUpdateMaterial}>
                          <DialogHeader>
                            <DialogTitle>Edit Material</DialogTitle>
                            <DialogDescription>
                              Update the details for this material.
                            </DialogDescription>
                          </DialogHeader>
                          <div className="flex flex-col gap-4 py-4">
                            <div className="flex flex-col gap-2">
                              <Label htmlFor="update-mat-title">
                                Title{" "}
                                <span className="text-destructive">*</span>
                              </Label>
                              <Input
                                id="update-mat-title"
                                placeholder="e.g. Course Slides"
                                value={updateMaterialTitle}
                                onChange={(e) =>
                                  setUpdateMaterialTitle(e.target.value)
                                }
                                required
                              />
                            </div>
                            <Tabs defaultValue="url">
                              <TabsList className="w-full" variant="line">
                                <TabsTrigger className="flex-1" value="url">
                                  URL
                                </TabsTrigger>
                                <TabsTrigger className="flex-1" value="file">
                                  File Upload
                                </TabsTrigger>
                              </TabsList>
                              <TabsContent value="url">
                                <Input
                                  placeholder="https://example.com/material"
                                  value={updateMaterialUrl}
                                  onChange={(e) =>
                                    setUpdateMaterialUrl(e.target.value)
                                  }
                                />
                              </TabsContent>
                              <TabsContent value="file">
                                <Input
                                  type="file"
                                  onChange={() => {
                                    // File update is handled separately
                                  }}
                                />
                              </TabsContent>
                            </Tabs>
                          </div>
                          <DialogFooter>
                            <Button
                              type="button"
                              variant="outline"
                              onClick={() => {
                                setIsMaterialUpdateOpen(false);
                                setEditingMaterialId(null);
                                setUpdateMaterialTitle("");
                                setUpdateMaterialUrl("");
                              }}
                            >
                              Cancel
                            </Button>
                            <Button
                              type="submit"
                              disabled={isUpdatingMaterial}
                            >
                              {isUpdatingMaterial && (
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                              )}
                              Update Material
                            </Button>
                          </DialogFooter>
                        </form>
                      </DialogContent>
                    </Dialog>
                  </div>
                ))}
              </div>
            )}
          </div>
        </TabsContent>

        {/* ── Assignments Tab (placeholder — no backend yet) ── */}
        <TabsContent value="assignments">
          <div className="flex flex-col gap-6 mt-4">
            <div className="flex items-center justify-between">
              <Dialog
                open={isCreateOpen}
                onOpenChange={(open) => {
                  setIsCreateOpen(open);
                  if (!open) resetCreateForm();
                }}
              >
                {user?.is_admin && (
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
                          {user?.is_admin && (
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
                      <CardFooter>
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
                  </div>
                ))}
              </div>
            )}

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
        </TabsContent>

        {/* ── Feedback Tab ──────────────────────────────────── */}
        <TabsContent value="feedback">
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
              <div className="flex flex-col gap-4 lg:flex-row lg:max-[600px]">
                {feedbackList.map((fb) => (
                  <Card key={fb.id}>
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
        </TabsContent>
      </Tabs>
    </div>
  );
}
