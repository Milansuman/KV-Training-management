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
        <Button variant="outline" className="w-full h-full">
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
}

const sessionSchema = z.object({
  title: z.string().min(1, "Title is required"),
  description: z.string().min(1, "Description is required"),
  start_datetime: z.string().min(1, "Start time is required"),
  end_datetime: z.string().min(1, "End time is required"),
  topics: z.string().optional(),
});

type SessionFormValues = z.infer<typeof sessionSchema>;

export function EventCalendar({ className }: EventCalendarProps) {
  const [events, setEvents] = React.useState([
    {
      id: "1",
      title: "event 1",
      start: "2026-06-29T09:00:00",
      end: "2026-06-29T10:30:00",
      extendedProps: {
        description: "this is a description",
        topics: ["backend", "frontend"],
      },
    },
    {
      id: "2",
      title: "event 2",
      start: "2026-06-29T13:00:00",
      end: "2026-06-29T14:30:00",
      extendedProps: {
        description: "this is another description",
        topics: ["database", "design"],
      },
    },
  ]);

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
      program_id: "1",
      topics: "",
    });

    setIsOpen(true);
  };

  const onSubmit = (data: SessionFormValues) => {
    const newEvent = {
      id: String(Date.now()),
      title: data.title,
      start: data.start_datetime,
      end: data.end_datetime,
      extendedProps: {
        description: data.description,
        topics: data.topics
          ? data.topics
              .split(",")
              .map((t) => t.trim())
              .filter(Boolean)
          : [],
        program_id: Number(data.program_id),
      },
    };

    setEvents((prev) => [...prev, newEvent]);
    setIsOpen(false);
  };

  return (
    <div className={cn(className)}>
      <FullCalendar
        events={events}
        plugins={[dayGridPlugin, interactionPlugin, timeGridPlugin]}
        eventContent={(info) => <EventButton info={info} />}
        initialView="dayGridMonth"
        headerToolbar={{
          left: "prev,next",
          center: "title",
          right: "dayGridMonth,timeGridWeek", // user can switch between the two
        }}
        height="100%"
        handleWindowResize
        selectable={true}
        editable={true}
        selectMirror={true}
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

            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="topics">Topics (comma separated)</Label>
                <Input
                  id="topics"
                  placeholder="e.g., Python, SQL, Git"
                  {...register("topics")}
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
              <Button type="submit">Create Session</Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
