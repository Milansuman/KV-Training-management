"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { NumberTicker } from "@/components/ui/number-ticker";
import { Plus, Loader2, ChevronDown, ChevronUp } from "lucide-react";
import { useRouter } from "next/navigation";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  GlowingStarsBackgroundCard,
  GlowingStarsDescription,
  GlowingStarsTitle,
} from "@/components/ui/glowing-stars";
import { Pencil, Trash } from "lucide-react";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { useGetMyselfQuery } from "@/lib/api/user/user.api";
import {
  useGetProgramProgressQuery,
  useCreateProgramMutation,
  useUpdateProgramMutation,
  useDeleteProgramMutation,
} from "@/lib/api/programs/programs.api";
import { useGetUserSessionsQuery } from "@/lib/api/sessions/sessions.api";
import type { UserSessionResponse } from "@/lib/api/sessions/sessions.type";
import { toast } from "sonner";
import AnimatedContent from "@/components/ui/AnimatedContent";
import { ProgramProgressItem } from "@/lib/api/programs/programs.type";
import { Pie, PieChart } from "recharts";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
  type ChartConfig,
} from "@/components/ui/chart";

// ─────────────────────────────────────────────────────────────────────────────
// Session item with computed status
// ─────────────────────────────────────────────────────────────────────────────
interface SessionItem {
  session_name: string;
  program_name: string;
  status: "done" | "live" | "todo";
}

function computeSessionStatus(
  startDatetime: string,
  endDatetime: string
): SessionItem["status"] {
  const now = new Date();
  const start = new Date(startDatetime);
  const end = new Date(endDatetime);
  if (now < start) return "todo";
  if (now > end) return "done";
  return "live";
}

function toSessionItem(s: UserSessionResponse): SessionItem {
  return {
    session_name: s.session_name,
    program_name: s.program_name,
    status: computeSessionStatus(s.start_datetime, s.end_datetime),
  };
}

// ─────────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────────

function getProgramCounts(program_details: ProgramProgressItem[]) {
  const today = new Date();
  let upcoming = 0, ongoing = 0, completed = 0;
  program_details.forEach((p) => {
    const start = new Date(p.start_date);
    const end   = new Date(p.end_date);
    if (today < start)     upcoming++;
    else if (today > end)  completed++;
    else                   ongoing++;
  });
  return { upcoming, ongoing, completed };
}

// ─────────────────────────────────────────────────────────────────────────────
// Sub-components
// ─────────────────────────────────────────────────────────────────────────────

// Segmented session rail (no extra deps)
const SESSION_BG: Record<SessionItem["status"], string> = {
  done: "bg-primary",
  live: "bg-sky-400",
  todo: "bg-muted",
};
const SESSION_CHIP: Record<SessionItem["status"], string> = {
  done: "bg-primary/20 text-primary",
  live: "bg-sky-400/15 text-sky-400",
  todo: "bg-muted text-muted-foreground",
};
const SESSION_LABEL: Record<SessionItem["status"], string> = {
  done: "Completed",
  live: "Live now",
  todo: "Upcoming",
};

function SessionRail({
  sessions,
  programTitle,
}: {
  sessions: SessionItem[];
  programTitle: string;
}) {
  const done  = sessions.filter((s) => s.status === "done").length;
  const live  = sessions.filter((s) => s.status === "live").length;
  const pct   = sessions.length > 0 ? Math.round((done / sessions.length) * 100) : 0;
  const [tip, setTip] = useState<number | null>(null);

  return (
    <div>
      {/* header */}
      <div className="mb-2 flex items-center justify-between">
        <div className="flex items-center gap-2 min-w-0">
          <span className="truncate text-sm font-medium text-foreground font-quicksand">
            {programTitle}
          </span>
          {live > 0 && (
            <span className="inline-flex shrink-0 items-center gap-1 rounded-full bg-sky-400/15 px-2 py-0.5 text-[10px] text-sky-400">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-sky-400" />
              {live} live
            </span>
          )}
        </div>
        <span className="ml-3 shrink-0 text-xs font-semibold text-primary">{pct}%</span>
      </div>

      {/* rail */}
      <div
        className="relative flex h-4 overflow-visible rounded-md border border-border"
        onMouseLeave={() => setTip(null)}
      >
        <div className="flex h-full w-full overflow-hidden rounded-md">
          {sessions.map((s, i) => (
            <div
              key={i}
              className={`flex-1 cursor-pointer border-r border-background/40 last:border-r-0 transition-opacity hover:opacity-70 ${SESSION_BG[s.status]}`}
              onMouseEnter={(e) => {
                setTip(i);
              }}
            />
          ))}
        </div>
        {/* tooltip */}
        {tip !== null && (
          <div
            className="pointer-events-none absolute bottom-[calc(100%+6px)] left-1/2 z-20 -translate-x-1/2 whitespace-nowrap rounded-lg border border-border bg-popover px-3 py-1.5 text-xs text-popover-foreground shadow-xl"
          >
            <p className="font-medium">{sessions[tip].session_name}</p>
            <p className="text-muted-foreground">{SESSION_LABEL[sessions[tip].status]}</p>
          </div>
        )}
      </div>

      {/* chips */}
      <div className="mt-2 flex flex-wrap gap-1">
        {sessions.map((s, i) => (
          <span key={i} className={`rounded-full px-2 py-0.5 text-[10px] font-medium ${SESSION_CHIP[s.status]}`}>
            {s.session_name}
          </span>
        ))}
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Dashboard
// ─────────────────────────────────────────────────────────────────────────────

// How many items to show before "Show more"
const PROGRESS_VISIBLE  = 3;
const SESSION_VISIBLE   = 3;

export default function Dashboard() {
  const router = useRouter();

  const { data: user_details, isLoading: userLoading }   = useGetMyselfQuery();
  const {
    data: program_details = [],
    isLoading: programsLoading,
    refetch: refetchProgramProgress,
  } = useGetProgramProgressQuery(user_details?.id ?? 0, { skip: !user_details });

  const [createProgram, { isLoading: isCreating }] = useCreateProgramMutation();
  const [updateProgram, { isLoading: isUpdating }] = useUpdateProgramMutation();
  const [deleteProgram, { isLoading: isDeleting }] = useDeleteProgramMutation();

  const [isCreateOpen,    setIsCreateOpen]    = useState(false);
  const [isUpdateOpen,    setIsUpdateOpen]    = useState(false);
  const [editingProgramId, setEditingProgramId] = useState<number | null>(null);

  // create form
  const [title,       setTitle]       = useState("");
  const [description, setDescription] = useState("");
  const [startDate,   setStartDate]   = useState("");
  const [endDate,     setEndDate]     = useState("");

  // update form
  const [updateTitle,       setUpdateTitle]       = useState("");
  const [updateDescription, setUpdateDescription] = useState("");
  const [updateStartDate,   setUpdateStartDate]   = useState("");
  const [updateEndDate,     setUpdateEndDate]     = useState("");

  // show-more state
  const [showAllProgress, setShowAllProgress] = useState(false);
  const [showAllSessions, setShowAllSessions] = useState(false);

  // ── derived ────────────────────────────────────────────────────────────────
  const program_count = program_details.length;
  const { upcoming, ongoing, completed } = getProgramCounts(program_details);

  const chartData = [
    { status: "Completed", count: completed, fill: "var(--chart-1)" },
    { status: "Ongoing",   count: ongoing,   fill: "var(--chart-2)" },
    { status: "Upcoming",  count: upcoming,  fill: "var(--chart-3)" },
  ];
  const chartConfig = {
    count:     { label: "Programs" },
    Completed: { label: "Completed", color: "var(--chart-1)" },
    Ongoing:   { label: "Ongoing",   color: "var(--chart-2)" },
    Upcoming:  { label: "Upcoming",  color: "var(--chart-3)" },
  } satisfies ChartConfig;

  // ── sessions for the rail ──────────────────────────────────────────────
  const { data: userSessions = [] } = useGetUserSessionsQuery(
    user_details?.id ?? 0,
    { skip: !user_details }
  );

  // group sessions by program for the rail
  const sessionsByProgram = userSessions.reduce<Record<string, SessionItem[]>>((acc, s) => {
    const item = toSessionItem(s);
    if (!acc[item.program_name]) acc[item.program_name] = [];
    acc[item.program_name].push(item);
    return acc;
  }, {});
  const sessionGroups = Object.entries(sessionsByProgram); // [ [programName, sessions[]] ]

  // sliced lists
  const visibleProgress = showAllProgress
    ? program_details
    : program_details.slice(0, PROGRESS_VISIBLE);

  const visibleSessions = showAllSessions
    ? sessionGroups
    : sessionGroups.slice(0, SESSION_VISIBLE);

  // ── handlers ───────────────────────────────────────────────────────────────
  function handleClickProgram(id: number) { router.push(`/dashboard/program/${id}`); }

  function resetUpdateForm() {
    setEditingProgramId(null);
    setUpdateTitle(""); setUpdateDescription("");
    setUpdateStartDate(""); setUpdateEndDate("");
  }

  function handleEdit(e: React.MouseEvent, program: {
    id: number; title: string; description: string;
    start_date: string; end_date: string;
  }) {
    e.preventDefault(); e.stopPropagation();
    setEditingProgramId(program.id);
    setUpdateTitle(program.title); setUpdateDescription(program.description);
    setUpdateStartDate(program.start_date); setUpdateEndDate(program.end_date);
    setIsUpdateOpen(true);
  }

  async function handleDelete(e: React.MouseEvent, programId: number) {
    e.preventDefault(); e.stopPropagation();
    try {
      await deleteProgram(programId).unwrap();
      toast.success("Program deleted successfully!");
      await refetchProgramProgress();
    } catch (err: any) {
      toast.error(err?.data?.detail || err?.data?.message || "Failed to delete program");
    }
  }

  async function handleCreateProgram(e: React.FormEvent) {
    e.preventDefault();
    if (!title || !description || !startDate || !endDate) { toast.error("Please fill in all fields."); return; }
    try {
      await createProgram({ title, description, start_date: startDate, end_date: endDate }).unwrap();
      toast.success("Program created successfully!");
      setIsCreateOpen(false);
      setTitle(""); setDescription(""); setStartDate(""); setEndDate("");
      await refetchProgramProgress();
    } catch (err: any) {
      toast.error(err?.data?.detail || err?.data?.message || "Failed to create program");
    }
  }

  async function handleUpdateProgram(e: React.FormEvent) {
    e.preventDefault();
    if (!editingProgramId || !updateTitle || !updateDescription) { toast.error("Please fill in all fields."); return; }
    try {
      await updateProgram({
        programId: editingProgramId,
        body: {
          title: updateTitle, description: updateDescription,
          ...(updateStartDate ? { start_date: updateStartDate } : {}),
          ...(updateEndDate   ? { end_date:   updateEndDate   } : {}),
        },
      }).unwrap();
      toast.success("Program updated successfully!");
      setIsUpdateOpen(false); resetUpdateForm();
      await refetchProgramProgress();
    } catch (err: any) {
      toast.error(err?.data?.detail || err?.data?.message || "Failed to update program");
    }
    router.push("/dashboard");
  }

  // ── loading / guard ────────────────────────────────────────────────────────
  if (userLoading || programsLoading) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }
  if (!user_details) return null;

  // ── render ─────────────────────────────────────────────────────────────────
  return (
    <>
      {/* ── TOP BENTO ROW ─────────────────────────────────────────────────── */}
      <div className="flex flex-col gap-4 p-6 lg:flex-row lg:items-stretch">

        {/* 1 ── NUMBER TICKER */}
        <AnimatedContent delay={0}>
          <div className="flex w-full lg:w-44 shrink-0 flex-col items-center justify-center rounded-2xl border bg-card p-6 shadow-sm gap-3 h-full">
            <p className="text-center text-sm font-semibold text-muted-foreground font-quicksand uppercase tracking-wider">
              Programs Enrolled
            </p>
            <NumberTicker
              value={program_count}
              className="text-8xl font-bold text-primary font-quicksand leading-none"
            />
    
          </div>
        </AnimatedContent>

        {/* 2 ── LEARNING PROGRESS */}
        <AnimatedContent delay={0.15} className="flex-1 min-w-0">
          <div className="flex flex-col rounded-2xl border bg-card shadow-sm font-quicksand h-full">
            <div className="p-5 pb-3">
              <h2 className="text-2xl font-semibold text-foreground font-quicksand ">Learning Progress</h2>
              <p className="mt-0.5 text-lg text-muted-foreground font-quicksand">
                Track your progress across enrolled programs.
              </p>
            </div>

            {/* scrollable / collapsible list */}
            <div className="flex-1 overflow-hidden px-5">
              <div className="space-y-5 pb-2">
                {visibleProgress.map((program) => {
                  const totalSessions     = Number(program.total_sessions) || 0;
                  const completedSessions = Number(program.completed_sessions) || 0;
                  const progress = totalSessions === 0
                    ? 0
                    : Math.min(100, Math.max(0, (completedSessions / totalSessions) * 100));

                  return (
                    <div key={program.id}>
                      <div className="mb-2 flex items-center justify-between gap-2">
                        <h3 className="truncate text-md font-medium text-foreground font-quicksand">
                          {program.title}
                        </h3>
                        <span className="shrink-0 text-xs text-muted-foreground font-quicksand">
                          {program.completed_sessions}/{program.total_sessions}
                        </span>
                      </div>
                      {/* shadcn Progress is a simple bar — replace inner with segments */}
                      <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
                        <div
                          className="h-full rounded-full bg-primary transition-all duration-700"
                          style={{ width: `${progress}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* show more / less */}
            {program_details.length > PROGRESS_VISIBLE && (
              <div className="border-t border-border px-5 py-2">
                <button
                  onClick={() => setShowAllProgress((v) => !v)}
                  className="flex w-full items-center justify-center gap-1 text-sm text-muted-foreground hover:text-foreground transition-colors font-quicksand py-1"
                >
                  {showAllProgress ? (
                    <><ChevronUp className="h-3.5 w-3.5" /> Show less</>
                  ) : (
                    <><ChevronDown className="h-3.5 w-3.5" /> Show {program_details.length - PROGRESS_VISIBLE} more</>
                  )}
                </button>
              </div>
            )}
          </div>
        </AnimatedContent>

        {/* 3 ── SESSION PROGRESS RAIL */}
        <AnimatedContent delay={0.25} className="flex-1 min-w-0">
          <div className="flex flex-col rounded-2xl border bg-card shadow-sm font-quicksand h-full">
            <div className="p-5 pb-3">
              <div className="flex items-center justify-between gap-2">
                <div>
                  <h2 className="text-2xl font-semibold text-foreground font-quicksand">Session Progress</h2>
                  <p className="mt-0.5 text-lg text-muted-foreground font-quicksand">
                    Sessions across all programs.
                  </p>
                </div>
                {/* legend */}
                <div className="hidden sm:flex items-center gap-3 shrink-0">
                  {(["done", "live", "todo"] as SessionItem["status"][]).map((s) => (
                    <div key={s} className="flex items-center gap-1">
                      <span className={`h-2 w-2 rounded-sm ${SESSION_BG[s]}`} />
                      <span className="text-[10px] text-muted-foreground capitalize">{s}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex-1 overflow-hidden px-5">
              <div className="space-y-5 pb-2 ">
                {visibleSessions.map(([progName, sessions]) => (
                  <SessionRail key={progName} programTitle={progName} sessions={sessions} />
                ))}
              </div>
            </div>

            {sessionGroups.length > SESSION_VISIBLE && (
              <div className="border-t border-border px-5 py-2">
                <button
                  onClick={() => setShowAllSessions((v) => !v)}
                  className="flex w-full items-center justify-center gap-1 text-sm text-muted-foreground hover:text-foreground transition-colors font-quicksand py-1"
                >
                  {showAllSessions ? (
                    <><ChevronUp className="h-3.5 w-3.5" /> Show less</>
                  ) : (
                    <><ChevronDown className="h-3.5 w-3.5" /> Show {sessionGroups.length - SESSION_VISIBLE} more</>
                  )}
                </button>
              </div>
            )}
          </div>
        </AnimatedContent>

        {/* 4 ── PIE CHART — fixed size, never stretches */}
        <AnimatedContent delay={0.35}>
          <Card className="flex flex-col rounded-2xl w-full lg:w-72 shrink-0 h-full">
            <CardHeader className="items-center pb-2  px-5">
              <CardTitle className="font-quicksand text-2xl">Program Status</CardTitle>
              <CardDescription className="font-quicksand text-lg">
                Distribution of your programs
              </CardDescription>
            </CardHeader>
            <CardContent className="flex flex-1 items-center justify-center px-5 pb-5">
              <ChartContainer
                config={chartConfig}
                className="h-[220px] w-[220px] shrink-0"
              >
                <PieChart>
                  <Pie data={chartData} dataKey="count" nameKey="status" />
                  <ChartLegend
                    content={<ChartLegendContent nameKey="status" />}
                    className="mt-3 flex-wrap justify-center gap-3"
                  />
                </PieChart>
              </ChartContainer>
            </CardContent>
          </Card>
        </AnimatedContent>

      </div>

      {/* ── PROGRAM CARDS ─────────────────────────────────────────────────── */}
      <div className="mt-2 px-6 pb-8 font-quicksand">
        <AnimatedContent delay={0.4}>
          <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <p className="text-2xl font-semibold text-foreground sm:text-3xl font-quicksand">
              Programs
            </p>
            {user_details.is_admin && (
              <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
                <DialogTrigger >
                  <Button className="flex items-center gap-2 font-quicksand">
                    <Plus className="h-4 w-4 text-white" />
                    <span className="text-white">Add Program</span>
                  </Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-lg font-quicksand">
                  <form onSubmit={handleCreateProgram}>
                    <DialogHeader>
                      <DialogTitle className="font-quicksand">Add Program</DialogTitle>
                      <DialogDescription className="font-quicksand">
                        Fill in the details below to create a new training program.
                      </DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-5 py-4">
                      <div className="grid gap-2">
                        <Label htmlFor="title">Program Title</Label>
                        <Input id="title" placeholder="Freshers Training" value={title} onChange={(e) => setTitle(e.target.value)} required />
                      </div>
                      <div className="grid gap-2">
                        <Label htmlFor="description">Description</Label>
                        <Textarea id="description" placeholder="Enter program description..." value={description} onChange={(e) => setDescription(e.target.value)} required />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="grid gap-2">
                          <Label htmlFor="startDate">Start Date</Label>
                          <Input id="startDate" type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} required />
                        </div>
                        <div className="grid gap-2">
                          <Label htmlFor="endDate">End Date</Label>
                          <Input id="endDate" type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} required />
                        </div>
                      </div>
                    </div>
                    <DialogFooter>
                      <Button type="button" variant="outline" onClick={() => setIsCreateOpen(false)}>Cancel</Button>
                      <Button type="submit" disabled={isCreating}>
                        {isCreating && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        Create Program
                      </Button>
                    </DialogFooter>
                  </form>
                </DialogContent>
              </Dialog>
            )}
          </div>
        </AnimatedContent>

        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-3">
          {program_details.map((program, index) => (
            <div key={program.id} className="w-full">
              <AnimatedContent distance={30} direction="vertical" duration={0.5} delay={0.5 + index * 0.1}>
                <div className="cursor-pointer">
                  <GlowingStarsBackgroundCard>
                    <div className="flex h-full flex-col justify-between font-quicksand">
                      <div>
                        <div onClick={() => handleClickProgram(program.id)} className="flex items-start justify-between gap-3">
                          <GlowingStarsTitle className="font-quicksand">{program.title}</GlowingStarsTitle>
                          {user_details.is_admin && (
                            <div className="flex shrink-0 items-center gap-2">
                              <button
                                type="button"
                                onClick={(e) => { handleEdit(e, program); e.stopPropagation(); }}
                                className="rounded-lg p-2 text-muted-foreground transition-colors hover:bg-primary/10 hover:text-primary"
                              >
                                <Pencil className="h-5 w-5" />
                              </button>
                              <button
                                type="button"
                                onClick={(e) => handleDelete(e, program.id)}
                                disabled={isDeleting}
                                className="rounded-lg p-2 text-muted-foreground transition-colors hover:bg-destructive/10 hover:text-destructive disabled:opacity-50"
                              >
                                {isDeleting ? <Loader2 className="h-5 w-5 animate-spin" /> : <Trash className="h-5 w-5" />}
                              </button>
                            </div>
                          )}
                        </div>
                        <GlowingStarsDescription className="mt-3 line-clamp-3">
                          {program.description}
                        </GlowingStarsDescription>
                      </div>
                    </div>
                  </GlowingStarsBackgroundCard>
                </div>
              </AnimatedContent>

              {/* Update dialog per card */}
              <Dialog
                open={isUpdateOpen && editingProgramId === program.id}
                onOpenChange={(open) => { setIsUpdateOpen(open); if (!open) resetUpdateForm(); }}
              >
                <DialogContent className="sm:max-w-lg font-quicksand">
                  <form onSubmit={handleUpdateProgram}>
                    <DialogHeader>
                      <DialogTitle className="font-quicksand">Edit Program</DialogTitle>
                      <DialogDescription className="font-quicksand">Update the details for this program.</DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-5 py-4">
                      <div className="grid gap-2">
                        <Label htmlFor="update-title">Program Title</Label>
                        <Input id="update-title" placeholder="Freshers Training" value={updateTitle} onChange={(e) => setUpdateTitle(e.target.value)} required />
                      </div>
                      <div className="grid gap-2">
                        <Label htmlFor="update-description">Description</Label>
                        <Textarea id="update-description" placeholder="Enter program description..." value={updateDescription} onChange={(e) => setUpdateDescription(e.target.value)} required />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="grid gap-2">
                          <Label htmlFor="update-startDate">Start Date</Label>
                          <Input id="update-startDate" type="date" value={updateStartDate} onChange={(e) => setUpdateStartDate(e.target.value)} />
                        </div>
                        <div className="grid gap-2">
                          <Label htmlFor="update-endDate">End Date</Label>
                          <Input id="update-endDate" type="date" value={updateEndDate} onChange={(e) => setUpdateEndDate(e.target.value)} />
                        </div>
                      </div>
                    </div>
                    <DialogFooter>
                      <Button type="button" variant="outline" onClick={(e) => { setIsUpdateOpen(false); e.stopPropagation(); }}>Cancel</Button>
                      <Button type="submit" disabled={isUpdating}>
                        {isUpdating && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        Update Program
                      </Button>
                    </DialogFooter>
                  </form>
                </DialogContent>
              </Dialog>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}