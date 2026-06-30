"use client";

import { useState } from "react";
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
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
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

const users = [
  {
    is_admin: true,
    name: "user1",
  },
  {
    is_admin: true,
    name: "user2",
  },
  {
    is_admin: false,
    name: "user3",
  },
];

const startTime = new Date("2026-07-15T10:00:00");
const endTime = new Date("2026-07-15T11:30:00");

const formatDateTime = (date: Date) =>
  date.toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });

interface Assignment {
  id: number;
  title: string;
  description: string;
  due_at: string;
}

interface Submission {
  id: number;
  user_display_name: string;
  url: string;
  submitted_at: string;
}

const placeholderAssignments: Assignment[] = [
  {
    id: 1,
    title: "React Basics Exercise",
    description:
      "Build a simple counter application using React hooks. This will help you understand useState and useEffect. Make sure to handle all edge cases.",
    due_at: "2026-07-20T23:59",
  },
  {
    id: 2,
    title: "API Integration Task",
    description:
      "Create a component that fetches and displays data from a REST API. Handle loading, error, and empty states gracefully.",
    due_at: "2026-07-25T23:59",
  },
  {
    id: 3,
    title: "Final Project Proposal",
    description:
      "Write a brief proposal for your final project covering the tech stack, architecture, and features you plan to implement.",
    due_at: "2026-08-01T23:59",
  },
];

const placeholderSubmissions: Record<number, Submission[]> = {
  1: [
    {
      id: 1,
      user_display_name: "John Doe",
      url: "https://github.com/johndoe/react-counter",
      submitted_at: "2026-07-19T14:30:00",
    },
    {
      id: 2,
      user_display_name: "Jane Smith",
      url: "https://github.com/janesmith/react-counter-app",
      submitted_at: "2026-07-20T10:15:00",
    },
    {
      id: 3,
      user_display_name: "Alice Wang",
      url: "https://github.com/alicew/use-state-counter",
      submitted_at: "2026-07-20T18:45:00",
    },
  ],
  2: [
    {
      id: 4,
      user_display_name: "John Doe",
      url: "https://github.com/johndoe/api-dashboard",
      submitted_at: "2026-07-24T09:20:00",
    },
  ],
  3: [],
};

interface FeedbackItem {
  id: number;
  display_name: string;
  username: string;
  text: string;
}

const placeholderFeedback: FeedbackItem[] = [
  {
    id: 1,
    display_name: "John Doe",
    username: "johndoe",
    text: "The session was very informative. The trainer explained concepts clearly and the hands-on exercises were really helpful. I would have liked more time on the advanced topics though.",
  },
  {
    id: 2,
    display_name: "Jane Smith",
    username: "janesmith",
    text: "Great pacing and excellent examples. The training materials were well-prepared and easy to follow. The Q&A session at the end was particularly valuable.",
  },
  {
    id: 3,
    display_name: "Alice Wang",
    username: "alicew",
    text: "The practical exercises were engaging but the initial setup took too long. Maybe provide a pre-configured environment next time.",
  },
  {
    id: 4,
    display_name: "Bob Chen",
    username: "bobchen",
    text: "Really enjoyed the session! The trainer was knowledgeable and approachable. Would recommend adding more real-world examples.",
  },
];

const aiFeedbackSummary =
  "Overall, participants found the session well-structured and informative. The trainer's clarity and the hands-on exercises were consistently praised. Common suggestions include providing more advanced content, reducing initial setup friction, and incorporating additional real-world examples. The Q&A format was highly appreciated and should be retained.";

const placeholderMaterials = [
  {
    id: 1,
    title: "Course Slides",
    type: "url" as const,
    url: "https://example.com/course-slides",
  },
  {
    id: 2,
    title: "Reference Guide",
    type: "file" as const,
    filename: "reference-guide.pdf",
  },
  {
    id: 3,
    title: "Video Recording",
    type: "url" as const,
    url: "https://example.com/recording",
  },
  {
    id: 4,
    title: "Exercise Workbook",
    type: "file" as const,
    filename: "exercises.xlsx",
  },
  {
    id: 5,
    title: "Assessment Rubric",
    type: "file" as const,
    filename: "rubric.pdf",
  },
];

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
  // ── Assignments state ──────────────────────────────────────────────
  const [assignments, setAssignments] =
    useState<Assignment[]>(placeholderAssignments);

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
  const [viewingSubmissions, setViewingSubmissions] = useState<Submission[]>(
    [],
  );

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

  function resetFeedbackForm() {
    setFeedbackText("");
  }

  function handleSubmitFeedback(e: React.FormEvent) {
    e.preventDefault();
    if (!feedbackText.trim()) return;
    // Placeholder: feedback would be submitted to the backend here
    setIsFeedbackOpen(false);
    resetFeedbackForm();
  }

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

  function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!newTitle || !newDescription || !newDueAt) return;

    const newAssignment: Assignment = {
      id: Date.now(),
      title: newTitle,
      description: newDescription,
      due_at: newDueAt,
    };
    setAssignments((prev) => [...prev, newAssignment]);
    setIsCreateOpen(false);
    resetCreateForm();
  }

  function handleEdit(assignment: Assignment) {
    setEditingAssignmentId(assignment.id);
    setUpdateTitle(assignment.title);
    setUpdateDescription(assignment.description);
    setUpdateDueAt(assignment.due_at);
    setIsUpdateOpen(true);
  }

  function handleUpdate(e: React.FormEvent) {
    e.preventDefault();
    if (!editingAssignmentId || !updateTitle || !updateDescription || !updateDueAt) return;

    setAssignments((prev) =>
      prev.map((a) =>
        a.id === editingAssignmentId
          ? {
              ...a,
              title: updateTitle,
              description: updateDescription,
              due_at: updateDueAt,
            }
          : a,
      ),
    );
    setIsUpdateOpen(false);
    resetUpdateForm();
  }

  function handleDelete(id: number) {
    setAssignments((prev) => prev.filter((a) => a.id !== id));
  }

  function handleViewSubmissions(assignmentId: number) {
    setViewingSubmissions(placeholderSubmissions[assignmentId] ?? []);
    setIsSubmissionsOpen(true);
  }

  function handleEditMaterial(material: (typeof placeholderMaterials)[number]) {
    setEditingMaterialId(material.id);
    setUpdateMaterialTitle(material.title);
    setUpdateMaterialUrl(material.type === "url" ? material.url : "");
    setIsMaterialUpdateOpen(true);
  }

  function handleUpdateMaterial(e: React.FormEvent) {
    e.preventDefault();
    if (!editingMaterialId || !updateMaterialTitle) return;
    // Placeholder: material would be updated via backend here
    setIsMaterialUpdateOpen(false);
    setEditingMaterialId(null);
    setUpdateMaterialTitle("");
    setUpdateMaterialUrl("");
  }

  return (
    <div className="flex flex-col gap-8 w-full h-full px-8 pb-8">
      <div className="flex flex-col gap-4 lg:flex-row">
        <div className="flex flex-col gap-4 lg:max-w-2/3">
          <h1 className="text-4xl text-foreground">Session Title</h1>
          <p className="text-muted-foreground">
            Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
            eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad
            minim veniam, quis nostrud exercitation ullamco laboris nisi ut
            aliquip ex ea commodo consequat. Duis aute irure dolor in
            reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
            pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
            culpa qui officia deserunt mollit anim id est laborum.
          </p>
          <p className="text-sm text-muted-foreground">
            {formatDateTime(startTime)} — {formatDateTime(endTime)}
          </p>
          <div className="flex flex-row gap-2 items-center flex-wrap">
            {users.map((user) => (
              <Badge
                variant={user.is_admin ? "destructive" : "default"}
                key={user.name}
                className="text-md p-3"
              >
                <User size={20} />
                {user.name}
              </Badge>
            ))}
          </div>
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
                render={<Button variant="outline" />}
              >
                Submit Feedback
              </DialogTrigger>
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
                    <Button type="submit" disabled={!feedbackText.trim()}>
                      Submit
                    </Button>
                  </DialogFooter>
                </form>
              </DialogContent>
            </Dialog>
          </div>
        </div>
      </div>
      <Tabs defaultValue="training_materials">
        <TabsList variant="line">
          <TabsTrigger value="training_materials">Training Materials</TabsTrigger>
          <TabsTrigger value="assignments">Assignments</TabsTrigger>
          <TabsTrigger value="feedback">Feedback</TabsTrigger>
        </TabsList>
        <TabsContent value="training_materials">
          <div className="flex flex-col gap-6 mt-4">
            <div className="flex items-center justify-between">
              <Dialog>
                <DialogTrigger
                  render={
                    <Button>
                      <Plus data-icon="inline-start" />
                      Add Material
                    </Button>
                  }
                />
                <DialogContent className="sm:max-w-md">
                  <DialogHeader>
                    <DialogTitle>Add Training Material</DialogTitle>
                    <DialogDescription>
                      Provide a title and either a URL or upload a file.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="flex flex-col gap-4">
                    <div className="flex flex-col gap-2">
                      <Label>
                        Title{" "}
                        <span className="text-destructive">*</span>
                      </Label>
                      <Input placeholder="e.g. Course Slides" />
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
                        <Input placeholder="https://example.com/material" />
                      </TabsContent>
                      <TabsContent value="file">
                        <Input type="file" />
                      </TabsContent>
                    </Tabs>
                  </div>
                  <DialogFooter>
                    <Button>Add Material</Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </div>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {placeholderMaterials.map((material) => (
                <div key={material.id}>
                  <Card>
                  <CardHeader>
                    <div className="flex items-center gap-2">
                      {material.type === "url" ? (
                        <Link className="size-4 shrink-0 text-muted-foreground" />
                      ) : (
                        <File className="size-4 shrink-0 text-muted-foreground" />
                      )}
                      <CardTitle>{material.title}</CardTitle>
                    </div>
                    <CardDescription>
                      {material.type === "url"
                        ? material.url
                        : material.filename}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <span className="inline-flex items-center gap-1.5 rounded-md bg-muted px-2 py-0.5 text-xs font-medium text-muted-foreground">
                      {material.type === "url" ? (
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
                    {material.type === "url" ? (
                      <Button size="sm" variant="ghost">
                        <ExternalLink data-icon="inline-start" />
                        Open
                      </Button>
                    ) : (
                      <Button size="sm" variant="ghost">
                        <File data-icon="inline-start" />
                        Download
                      </Button>
                    )}
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
                        className="rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-destructive/10 hover:text-destructive"
                      >
                        <Trash2 className="size-4" />
                      </button>
                    </div>
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
                            <Input type="file" />
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
                        <Button type="submit">
                          Update Material
                        </Button>
                      </DialogFooter>
                    </form>
                  </DialogContent>
                </Dialog>
              </div>
            ))}
            </div>
          </div>
        </TabsContent>
        <TabsContent value="assignments">
          <div className="flex flex-col gap-6 mt-4">
            {/* ── Header ─────────────────────────────────────────── */}
            <div className="flex items-center justify-between">
              <Dialog
                open={isCreateOpen}
                onOpenChange={(open) => {
                  setIsCreateOpen(open);
                  if (!open) resetCreateForm();
                }}
              >
                <DialogTrigger
                  render={
                    <Button>
                      <Plus data-icon="inline-start" />
                      Create Assignment
                    </Button>
                  }
                />
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
                      <Button type="submit">Create Assignment</Button>
                    </DialogFooter>
                  </form>
                </DialogContent>
              </Dialog>
            </div>

            {/* ── Assignment Cards ────────────────────────────────── */}
            {assignments.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
                <p className="text-lg">No assignments yet.</p>
                <p className="text-sm">
                  Create one to get started.
                </p>
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

                    {/* ── Update Dialog ───────────────────────────── */}
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
                                onChange={(e) =>
                                  setUpdateTitle(e.target.value)
                                }
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
                                onChange={(e) =>
                                  setUpdateDueAt(e.target.value)
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
                                setIsUpdateOpen(false);
                                resetUpdateForm();
                              }}
                            >
                              Cancel
                            </Button>
                            <Button type="submit">
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

            {/* ── Submissions Dialog ───────────────────────────── */}
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
                              {sub.user_display_name}
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
                              {formatDateTimeLong(sub.submitted_at)}
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
        <TabsContent value="feedback">
          <div className="flex flex-col gap-6 mt-4">
            {/* ── AI Summary Region ──────────────────────────── */}
            <div className="flex flex-col items-center gap-3 py-6 text-center">
              <div className="flex size-10 items-center justify-center rounded-full bg-primary/10">
                <Sparkles className="size-5 text-primary" />
              </div>
              <h3 className="text-lg font-semibold text-foreground">
                What are trainees saying about your session?
              </h3>
              <p className="max-w-2xl text-sm text-left leading-relaxed text-foreground/70">
                {aiFeedbackSummary}
              </p>
            </div>

            {/* ── Feedback Cards ───────────────────────────────── */}
            {placeholderFeedback.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
                <p className="text-lg">No feedback yet.</p>
                <p className="text-sm">
                  Feedback will appear here once users submit them.
                </p>
              </div>
            ) : (
              <div className="flex flex-col gap-4 lg:flex-row lg:max-[600px]">
                {placeholderFeedback.map((fb) => (
                  <Card key={fb.id}>
                    <CardHeader>
                      <div className="flex items-center gap-2.5">
                        <div className="flex size-9 items-center justify-center rounded-full bg-muted">
                          <User className="size-4 text-muted-foreground" />
                        </div>
                        <div className="flex flex-col">
                          <CardTitle className="text-sm font-medium">
                            {fb.display_name}
                          </CardTitle>
                          <CardDescription className="text-xs">
                            @{fb.username}
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
