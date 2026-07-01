"use client";

import * as React from "react";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import interactionPlugin from "@fullcalendar/interaction";
import timeGridPlugin from "@fullcalendar/timegrid";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import {
  Popover,
  PopoverContent,
  PopoverDescription,
  PopoverTitle,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import {
  InputGroup,
  InputGroupInput,
} from "@/components/ui/input-group";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";
import { EventContentArg } from "@fullcalendar/core/index.js";
import {
  useGetSessionsByProgramIdQuery,
  useCreateSessionMutation,
  useUpdateSessionMutation,
  useDeleteSessionMutation,
  useAssignTopicToSessionMutation,
  useRemoveTopicFromSessionMutation,
} from "@/lib/api/sessions/sessions.api";
import { useCreateTopicMutation } from "@/lib/api/topics/topics.api";
import { useGetMyselfQuery } from "@/lib/api/user/user.api";
import { toast } from "sonner";
import { Loader2, Pencil, Trash2, TriangleAlert, X } from "lucide-react";
import Link from "next/link";

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogMedia,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

const formatDateTime = (date: Date | null) => {
  if (!date) return "";
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
};

const toDatetimeLocalString = (date: Date) => {
  const pad = (num: number) => String(num).padStart(2, "0");
  const year = date.getFullYear();
  const month = pad(date.getMonth() + 1);
  const day = pad(date.getDate());
  const hours = pad(date.getHours());
  const minutes = pad(date.getMinutes());
  return `${year}-${month}-${day}T${hours}:${minutes}`;
};

// ── Topics input component ─────────────────────────────────────────
function TopicsInput({
  value = [],
  onChange,
  disabled,
  placeholder,
}: {
  value: string[];
  onChange: (topics: string[]) => void;
  disabled?: boolean;
  placeholder?: string;
}) {
  const [inputValue, setInputValue] = React.useState("");

  const addTopic = () => {
    const trimmed = inputValue.trim();
    if (trimmed && !value.includes(trimmed)) {
      onChange([...value, trimmed]);
    }
    setInputValue("");
  };

  const removeTopic = (index: number) => {
    onChange(value.filter((_, i) => i !== index));
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === " " || e.key === "Enter") {
      e.preventDefault();
      addTopic();
    }
    if (e.key === "Backspace" && !inputValue && value.length > 0) {
      removeTopic(value.length - 1);
    }
  };

  return (
    <div className="flex flex-col gap-1.5">
      <Label>Topics</Label>
      <InputGroup className="flex-wrap h-auto min-h-8 gap-1 px-1 py-1">
        {value.map((topic, i) => (
          <Badge key={i} variant="secondary" className="gap-1 shrink-0">
            {topic}
            <button
              type="button"
              onClick={() => removeTopic(i)}
              disabled={disabled}
              className="ml-0.5 rounded-full outline-none ring-offset-background transition-colors hover:bg-muted-foreground/20 focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1"
            >
              <X className="h-3 w-3" />
              <span className="sr-only">Remove {topic}</span>
            </button>
          </Badge>
        ))}
        <InputGroupInput
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            placeholder ??
            (value.length === 0 ? "Type a topic and press space..." : "")
          }
          disabled={disabled}
          className="min-w-20 flex-1"
        />
      </InputGroup>
    </div>
  );
}

const sessionSchema = z.object({
  title: z.string().min(1, "Title is required"),
  description: z.string().min(1, "Description is required"),
  start_datetime: z.string().min(1, "Start time is required"),
  end_datetime: z.string().min(1, "End time is required"),
});

type SessionFormValues = z.infer<typeof sessionSchema>;

interface EventCalendarProps {
  className?: string;
  programId: number;
}

// ── Session data shape from the API ─────────────────────────────────
interface TopicData {
  id: number;
  title: string;
}

interface SessionData {
  id: number;
  title: string;
  description: string;
  start_datetime: string;
  end_datetime: string;
  program_id: number;
  topics?: TopicData[];
}

export function EventCalendar({ className, programId }: EventCalendarProps) {
  const { data: user } = useGetMyselfQuery();
  const { data: dbSessions = [], isLoading: sessionsLoading } =
    useGetSessionsByProgramIdQuery(programId);

  const [createSession, { isLoading: isCreating }] = useCreateSessionMutation();
  const [updateSession, { isLoading: isUpdating }] = useUpdateSessionMutation();
  const [deleteSession, { isLoading: isDeleting }] = useDeleteSessionMutation();
  const [createTopic] = useCreateTopicMutation();
  const [assignTopicToSession] = useAssignTopicToSessionMutation();
  const [removeTopicFromSession] = useRemoveTopicFromSessionMutation();

  const events = React.useMemo(() => {
    return dbSessions.map((session) => ({
      id: String(session.id),
      title: session.title,
      start: session.start_datetime,
      end: session.end_datetime,
      extendedProps: {
        description: session.description,
        program_id: session.program_id,
        session_id: session.id,
        topics:
          "topics" in session && Array.isArray((session as any).topics)
            ? (session as any).topics.map((t: any) => t.title)
            : [],
      },
    }));
  }, [dbSessions]);

  const isAdmin = user?.is_admin ?? false;

  // ── Create dialog ────────────────────────────────────────────────
  const [isCreateOpen, setIsCreateOpen] = React.useState(false);
  const [createTopics, setCreateTopics] = React.useState<string[]>([]);

  const createForm = useForm<SessionFormValues>({
    resolver: zodResolver(sessionSchema),
    defaultValues: {
      title: "",
      description: "",
      start_datetime: "",
      end_datetime: "",
    },
  });

  const handleSelect = (selectInfo: any) => {
    if (!isAdmin) return;
    const start = new Date(selectInfo.start);
    const end = new Date(selectInfo.end);

    if (selectInfo.allDay) {
      start.setHours(9, 0, 0, 0);
      end.setTime(end.getTime() - 60 * 1000);
    }

    createForm.reset({
      title: "",
      description: "",
      start_datetime: toDatetimeLocalString(start),
      end_datetime: toDatetimeLocalString(end),
    });
    setCreateTopics([]);

    setIsCreateOpen(true);
  };

  const handleCreateSubmit = async (data: SessionFormValues) => {
    try {
      const session = await createSession({
        title: data.title,
        description: data.description,
        start_datetime: new Date(data.start_datetime).toISOString(),
        end_datetime: new Date(data.end_datetime).toISOString(),
        program_id: programId,
      }).unwrap();

      // Create topics and assign them to the session
      for (const topicTitle of createTopics) {
        const topic = await createTopic({ title: topicTitle }).unwrap();
        await assignTopicToSession({
          sessionId: session.id,
          topicId: topic.id,
        }).unwrap();
      }

      toast.success("Session scheduled successfully!");
      setIsCreateOpen(false);
      setCreateTopics([]);
    } catch (err: any) {
      toast.error(err?.data?.detail || "Failed to schedule session");
    }
  };

  // ── Edit dialog ──────────────────────────────────────────────────
  const [editingSession, setEditingSession] = React.useState<SessionData | null>(null);
  const isEditOpen = editingSession !== null;

  const [editTopics, setEditTopics] = React.useState<string[]>([]);

  const editForm = useForm<SessionFormValues>({
    resolver: zodResolver(sessionSchema),
    defaultValues: {
      title: "",
      description: "",
      start_datetime: "",
      end_datetime: "",
    },
  });

  function openEditDialog(session: SessionData) {
    setEditingSession(session);
    editForm.reset({
      title: session.title,
      description: session.description,
      start_datetime: toDatetimeLocalString(new Date(session.start_datetime)),
      end_datetime: toDatetimeLocalString(new Date(session.end_datetime)),
    });
    const sessionTopics: string[] =
      session.topics?.map((t: TopicData) => t.title) ?? [];
    setEditTopics(sessionTopics);
  }

  function closeEditDialog() {
    setEditingSession(null);
    editForm.reset();
    setEditTopics([]);
  }

  const handleEditSubmit = async (data: SessionFormValues) => {
    if (!editingSession) return;
    try {
      await updateSession({
        sessionId: editingSession.id,
        body: {
          title: data.title,
          description: data.description,
          start_datetime: new Date(data.start_datetime).toISOString(),
          end_datetime: new Date(data.end_datetime).toISOString(),
        },
      }).unwrap();

      // Diff existing topics with the new topic list
      const existingTopics: TopicData[] = editingSession.topics ?? [];
      const existingTitles = existingTopics.map((t) => t.title);

      // Remove topics the user deleted
      for (const existingTopic of existingTopics) {
        if (!editTopics.includes(existingTopic.title)) {
          await removeTopicFromSession({
            sessionId: editingSession.id,
            topicId: existingTopic.id,
          }).unwrap();
        }
      }

      // Create and assign new topics
      for (const newTitle of editTopics) {
        if (!existingTitles.includes(newTitle)) {
          const topic = await createTopic({ title: newTitle }).unwrap();
          await assignTopicToSession({
            sessionId: editingSession.id,
            topicId: topic.id,
          }).unwrap();
        }
      }

      toast.success("Session updated successfully!");
      closeEditDialog();
    } catch (err: any) {
      toast.error(err?.data?.detail || "Failed to update session");
    }
  };

  // ── Delete confirmation dialog state ────────────────────────────
  const [deletingSessionId, setDeletingSessionId] = React.useState<number | null>(
    null,
  );
  const isDeleteOpen = deletingSessionId !== null;

  async function handleConfirmDelete() {
    if (!deletingSessionId) return;
    try {
      await deleteSession(deletingSessionId).unwrap();
      toast.success("Session deleted successfully!");
      setDeletingSessionId(null);
    } catch (err: any) {
      toast.error(err?.data?.detail || "Failed to delete session");
    }
  }

  // ── Event popover with edit/delete buttons for admins ────────────
  function EventButton({
    info,
    programId,
  }: {
    info: EventContentArg;
    programId: number;
  }) {
    const rawSession = dbSessions.find(
      (s) => s.id === Number(info.event.id),
    );

    const now = new Date();
    const start = info.event.start;
    const end = info.event.end;

    let statusClass = "bg-muted text-muted-foreground";
    if (start && end) {
      if (now < start) {
        statusClass =
          "bg-blue-500/15 text-blue-700 dark:text-blue-400";
      } else if (now >= start && now <= end) {
        statusClass =
          "bg-green-500/15 text-green-700 dark:text-green-400";
      }
    }

    return (
      <Popover>
        <PopoverTrigger className="w-full h-full">
          <Badge className={`w-full h-full text-left justify-start truncate rounded-md ${statusClass}`}>
            {info.event.title}
          </Badge>
        </PopoverTrigger>
        <PopoverContent className="flex flex-col gap-3">
          <div>
            <PopoverTitle>{info.event.title}</PopoverTitle>
            <PopoverDescription>
              {info.event.extendedProps.description}
            </PopoverDescription>
          </div>
          <div className="flex flex-row gap-2 flex-wrap">
            {info.event.extendedProps.topics?.map((topic: string) => (
              <Badge key={topic}>{topic}</Badge>
            ))}
          </div>

          <div className="flex flex-col gap-1 text-xs text-muted-foreground border-t pt-2 border-border">
            {info.event.start && (
              <div>
                <span className="font-medium text-foreground">Starts: </span>
                {formatDateTime(info.event.start)}
              </div>
            )}
            {info.event.end && (
              <div>
                <span className="font-medium text-foreground">Ends: </span>
                {formatDateTime(info.event.end)}
              </div>
            )}
          </div>

          <Link
            href={`/dashboard/program/${programId}/session/${info.event.extendedProps.session_id}`}
          >
            <Button className="w-full mt-1">View Session</Button>
          </Link>

          {isAdmin && rawSession && (
            <div className="flex gap-2 mt-1">
              <Button
                variant="outline"
                size="sm"
                className="flex-1"
                onClick={() => openEditDialog(rawSession)}
              >
                <Pencil className="mr-1 h-4 w-4" />
                Edit
              </Button>
              <Button
                variant="destructive"
                size="sm"
                className="flex-1"
                disabled={isDeleting}
                onClick={() => setDeletingSessionId(rawSession.id)}
              >
                {isDeleting && deletingSessionId === rawSession.id ? (
                  <Loader2 className="mr-1 h-4 w-4 animate-spin" />
                ) : (
                  <Trash2 className="mr-1 h-4 w-4" />
                )}
                Delete
              </Button>
            </div>
          )}
        </PopoverContent>
      </Popover>
    );
  }

  // ── Loading state ──────────────────────────────────────────────
  if (sessionsLoading) {
    return (
      <div className="flex h-full w-full items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className={cn("h-full", className)}>
      <FullCalendar
        events={events}
        plugins={[dayGridPlugin, interactionPlugin, timeGridPlugin]}
        eventContent={(info) => (
          <EventButton info={info} programId={programId} />
        )}
        initialView="dayGridMonth"
        headerToolbar={{
          left: "prev,next",
          center: "title",
          right: "dayGridMonth,timeGridWeek",
        }}
        height="100%"
        handleWindowResize
        selectable={isAdmin}
        editable={isAdmin}
        selectMirror={isAdmin}
        select={handleSelect}
      />

      {/* ── Create Session Dialog ─────────────────────────────── */}
      <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
        <DialogContent className="sm:max-w-md animate-in fade-in zoom-in duration-200">
          <DialogHeader>
            <DialogTitle>Create New Session</DialogTitle>
            <DialogDescription>
              Enter the details to schedule a new training session.
            </DialogDescription>
          </DialogHeader>
          <form
            onSubmit={createForm.handleSubmit(handleCreateSubmit)}
            className="flex flex-col gap-4 py-2"
          >
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="title">Title</Label>
              <Input
                id="title"
                placeholder="e.g., Intro to Backend Development"
                {...createForm.register("title")}
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <Label htmlFor="description">Description</Label>
              <textarea
                id="description"
                placeholder="Brief summary of the session goals..."
                className="w-full min-h-[70px] rounded-lg border border-input bg-transparent px-2.5 py-1.5 text-base transition-colors outline-none placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 md:text-sm dark:bg-input/30"
                {...createForm.register("description")}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="start_datetime">Start Time</Label>
                <Input
                  id="start_datetime"
                  type="datetime-local"
                  {...createForm.register("start_datetime")}
                />
              </div>
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="end_datetime">End Time</Label>
                <Input
                  id="end_datetime"
                  type="datetime-local"
                  {...createForm.register("end_datetime")}
                />
              </div>
            </div>

            <TopicsInput
              value={createTopics}
              onChange={setCreateTopics}
              disabled={isCreating}
            />

            <div className="flex justify-end gap-2 mt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => setIsCreateOpen(false)}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isCreating}>
                {isCreating && (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                )}
                Create Session
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* ── Edit Session Dialog ───────────────────────────────── */}
      <Dialog open={isEditOpen} onOpenChange={closeEditDialog}>
        <DialogContent className="sm:max-w-md animate-in fade-in zoom-in duration-200">
          <DialogHeader>
            <DialogTitle>Edit Session</DialogTitle>
            <DialogDescription>
              Update the details for this training session.
            </DialogDescription>
          </DialogHeader>
          <form
            onSubmit={editForm.handleSubmit(handleEditSubmit)}
            className="flex flex-col gap-4 py-2"
          >
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="edit-title">Title</Label>
              <Input
                id="edit-title"
                placeholder="e.g., Intro to Backend Development"
                {...editForm.register("title")}
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <Label htmlFor="edit-description">Description</Label>
              <textarea
                id="edit-description"
                placeholder="Brief summary of the session goals..."
                className="w-full min-h-[70px] rounded-lg border border-input bg-transparent px-2.5 py-1.5 text-base transition-colors outline-none placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 md:text-sm dark:bg-input/30"
                {...editForm.register("description")}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="edit-start_datetime">Start Time</Label>
                <Input
                  id="edit-start_datetime"
                  type="datetime-local"
                  {...editForm.register("start_datetime")}
                />
              </div>
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="edit-end_datetime">End Time</Label>
                <Input
                  id="edit-end_datetime"
                  type="datetime-local"
                  {...editForm.register("end_datetime")}
                />
              </div>
            </div>

            <TopicsInput
              value={editTopics}
              onChange={setEditTopics}
              disabled={isUpdating}
            />

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={closeEditDialog}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isUpdating}>
                {isUpdating && (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                )}
                Update Session
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* ── Delete Confirmation Dialog ──────────────────────────── */}
      <AlertDialog
        open={isDeleteOpen}
        onOpenChange={(open) => {
          if (!open) setDeletingSessionId(null);
        }}
      >
        <AlertDialogContent size="sm">
          <AlertDialogHeader>
            <AlertDialogMedia>
              <TriangleAlert className="text-destructive" />
            </AlertDialogMedia>
            <AlertDialogTitle>Delete Session</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete this session? This action cannot be
              undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => setDeletingSessionId(null)}>
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction
              variant="destructive"
              disabled={isDeleting}
              onClick={handleConfirmDelete}
            >
              {isDeleting && (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              )}
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
