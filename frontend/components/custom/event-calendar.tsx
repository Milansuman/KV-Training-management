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
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";
import { EventContentArg } from "@fullcalendar/core/index.js";
import {
  useGetSessionsByProgramIdQuery,
  useCreateSessionMutation,
} from "@/lib/api/sessions/sessions.api";
import { useGetMyselfQuery } from "@/lib/api/user/user.api";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";

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

function EventButton({ info }: { info: EventContentArg }) {
  return (
    <Popover>
      <PopoverTrigger className="w-full h-full">
        <Button variant="outline" className="w-full h-full text-left justify-start truncate">
          {info.event.title}
        </Button>
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

        <Button className="w-full mt-1">View Session</Button>
      </PopoverContent>
    </Popover>
  );
}

interface EventCalendarProps {
  className?: string;
  programId: number;
}

const sessionSchema = z.object({
  title: z.string().min(1, "Title is required"),
  description: z.string().min(1, "Description is required"),
  start_datetime: z.string().min(1, "Start time is required"),
  end_datetime: z.string().min(1, "End time is required"),
  topics: z.string().optional(),
});

type SessionFormValues = z.infer<typeof sessionSchema>;

export function EventCalendar({ className, programId }: EventCalendarProps) {
  const { data: user } = useGetMyselfQuery();
  const { data: dbSessions = [], isLoading: sessionsLoading } =
    useGetSessionsByProgramIdQuery(programId);

  const [createSession, { isLoading: isCreating }] = useCreateSessionMutation();

  const events = React.useMemo(() => {
    return dbSessions.map((session) => ({
      id: String(session.id),
      title: session.title,
      start: session.start_datetime,
      end: session.end_datetime,
      extendedProps: {
        description: session.description,
        program_id: session.program_id,
        topics: [], // backend does not store topics for sessions directly in create/update endpoint payload yet
      },
    }));
  }, [dbSessions]);

  const [isOpen, setIsOpen] = React.useState(false);

  const { register, handleSubmit, reset } = useForm<SessionFormValues>({
    resolver: zodResolver(sessionSchema),
    defaultValues: {
      title: "",
      description: "",
      start_datetime: "",
      end_datetime: "",
      topics: "",
    },
  });

  const handleSelect = (selectInfo: any) => {
    if (!user?.is_admin) {
      return;
    }
    const start = new Date(selectInfo.start);
    const end = new Date(selectInfo.end);

    if (selectInfo.allDay) {
      start.setHours(9, 0, 0, 0);
      end.setTime(start.getTime() + 60 * 60 * 1000);
    }

    reset({
      title: "",
      description: "",
      start_datetime: toDatetimeLocalString(start),
      end_datetime: toDatetimeLocalString(end),
      topics: "",
    });

    setIsOpen(true);
  };

  const onSubmit = async (data: SessionFormValues) => {
    try {
      await createSession({
        title: data.title,
        description: data.description,
        start_datetime: new Date(data.start_datetime).toISOString(),
        end_datetime: new Date(data.end_datetime).toISOString(),
        program_id: programId,
      }).unwrap();

      toast.success("Session scheduled successfully!");
      setIsOpen(false);
    } catch (err: any) {
      toast.error(err?.data?.detail || "Failed to schedule session");
    }
  };

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
        eventContent={(info) => <EventButton info={info} />}
        initialView="dayGridMonth"
        headerToolbar={{
          left: "prev,next",
          center: "title",
          right: "dayGridMonth,timeGridWeek",
        }}
        height="100%"
        handleWindowResize
        selectable={user?.is_admin || false}
        editable={user?.is_admin || false}
        selectMirror={user?.is_admin || false}
        select={handleSelect}
      />

      <Dialog open={isOpen} onOpenChange={setIsOpen}>
        <DialogContent className="sm:max-w-md animate-in fade-in zoom-in duration-200">
          <DialogHeader>
            <DialogTitle>Create New Session</DialogTitle>
            <DialogDescription>
              Enter the details to schedule a new training session.
            </DialogDescription>
          </DialogHeader>
          <form
            onSubmit={handleSubmit(onSubmit)}
            className="flex flex-col gap-4 py-2"
          >
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="title">Title</Label>
              <Input
                id="title"
                placeholder="e.g., Intro to Backend Development"
                {...register("title")}
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <Label htmlFor="description">Description</Label>
              <textarea
                id="description"
                placeholder="Brief summary of the session goals..."
                className="w-full min-h-[70px] rounded-lg border border-input bg-transparent px-2.5 py-1.5 text-base transition-colors outline-none placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 md:text-sm dark:bg-input/30"
                {...register("description")}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="start_datetime">Start Time</Label>
                <Input
                  id="start_datetime"
                  type="datetime-local"
                  {...register("start_datetime")}
                />
              </div>
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="end_datetime">End Time</Label>
                <Input
                  id="end_datetime"
                  type="datetime-local"
                  {...register("end_datetime")}
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 mt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => setIsOpen(false)}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isCreating}>
                {isCreating && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Create Session
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
