"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { NumberTicker } from "@/components/ui/number-ticker";
import { Progress } from "@/components/ui/progress";
import { Plus, Loader2 } from "lucide-react";
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


export default function Dashboard() {
  const router = useRouter();
  const { data: user_details, isLoading: userLoading } = useGetMyselfQuery();
  const {
    data: program_details = [],
    isLoading: programsLoading,
    refetch: refetchProgramProgress,
  } = useGetProgramProgressQuery(user_details?.id ?? 0, {
    skip: !user_details,
  });

  const [createProgram, { isLoading: isCreating }] = useCreateProgramMutation();
  const [updateProgram, { isLoading: isUpdating }] = useUpdateProgramMutation();
  const [deleteProgram, { isLoading: isDeleting }] = useDeleteProgramMutation();

  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isUpdateOpen, setIsUpdateOpen] = useState(false);
  const [editingProgramId, setEditingProgramId] = useState<number | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [updateTitle, setUpdateTitle] = useState("");
  const [updateDescription, setUpdateDescription] = useState("");
  const [updateStartDate, setUpdateStartDate] = useState("");
  const [updateEndDate, setUpdateEndDate] = useState("");

  const program_count = program_details.length;

  const { upcoming, ongoing, completed } = getProgramCounts(program_details);
  const chartData = [
    {
      status: "Completed",
      count: completed,
      fill: "var(--chart-1)",
    },
    {
      status: "Ongoing",
      count: ongoing,
      fill: "var(--chart-2)",
    },
    {
      status: "Upcoming",
      count: upcoming,
      fill: "var(--chart-3)",
    },
  ];

  const chartConfig = {
    count: {
      label: "Programs",
    },

    Completed: {
      label: "Completed",
      color: "var(--chart-1)",
    },

    Ongoing: {
      label: "Ongoing",
      color: "var(--chart-2)",
    },

    Upcoming: {
      label: "Upcoming",
      color: "var(--chart-3)",
    },
  } satisfies ChartConfig;

  function handleClickProgram(id: number) {
    router.push(`/dashboard/program/${id}`);
  }

  function resetUpdateForm() {
    setEditingProgramId(null);
    setUpdateTitle("");
    setUpdateDescription("");
    setUpdateStartDate("");
    setUpdateEndDate("");
  }

  function handleEdit(
    e: React.MouseEvent,
    program: {
      id: number;
      title: string;
      description: string;
      start_date: string;
      end_date: string;
    },
  ) {
    e.preventDefault();
    e.stopPropagation();
    setEditingProgramId(program.id);
    setUpdateTitle(program.title);
    setUpdateDescription(program.description);
    setUpdateStartDate(program.start_date);
    setUpdateEndDate(program.end_date);
    setIsUpdateOpen(true);
  }

  async function handleDelete(e: React.MouseEvent, programId: number) {
    e.preventDefault();
    e.stopPropagation();

    try {
      await deleteProgram(programId).unwrap();
      toast.success("Program deleted successfully!");
      await refetchProgramProgress();
    } catch (err: any) {
      toast.error(
        err?.data?.detail || err?.data?.message || "Failed to delete program",
      );
    }
  }

  const handleCreateProgram = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !description || !startDate || !endDate) {
      toast.error("Please fill in all fields.");
      return;
    }

    try {
      await createProgram({
        title,
        description,
        start_date: startDate,
        end_date: endDate,
      }).unwrap();

      toast.success("Program created successfully!");
      setIsCreateOpen(false);
      setTitle("");
      setDescription("");
      setStartDate("");
      setEndDate("");
      await refetchProgramProgress();
    } catch (err: any) {
      toast.error(
        err?.data?.detail || err?.data?.message || "Failed to create program",
      );
    }
  };

  const handleUpdateProgram = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingProgramId || !updateTitle || !updateDescription) {
      toast.error("Please fill in all fields.");
      return;
    }

    try {
      await updateProgram({
        programId: editingProgramId,
        body: {
          title: updateTitle,
          description: updateDescription,
          ...(updateStartDate ? { start_date: updateStartDate } : {}),
          ...(updateEndDate ? { end_date: updateEndDate } : {}),
        },
      }).unwrap();

      toast.success("Program updated successfully!");
      setIsUpdateOpen(false);
      resetUpdateForm();
      await refetchProgramProgress();
    } catch (err: any) {
      toast.error(
        err?.data?.detail || err?.data?.message || "Failed to update program",
      );
    }
    router.push("/dashboard");
  };

  if (userLoading || programsLoading) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!user_details) {
    return null;
  }

//   FUNCTION TO GET THE COUNTS OF UPCOMING, ONGOING, AND COMPLETED PROGRAMS 
  function getProgramCounts(program_details: ProgramProgressItem[]) {
    const today = new Date();

    let upcoming = 0;
    let ongoing = 0;
    let completed = 0;

    program_details.forEach((program) => {
      const start = new Date(program.start_date);
      const end = new Date(program.end_date);

      if (today < start) {
        upcoming++;
      } else if (today > end) {
        completed++;
      } else {
        ongoing++;
      }
    });

    return {
      upcoming,
      ongoing,
      completed,
    };
  }

  return (
    <>
    
      <div className="flex flex-col-reverse gap-6 p-6 lg:flex-row lg:items-stretch">
        {/* NUMBER CARD*/}
        <AnimatedContent delay={0}>
          <div className="flex w-full lg:w-52 flex-col items-center justify-center rounded-2xl border bg-card p-6 shadow-sm gap-4 h-full">
            <p className="text-center text-lg text-foreground font-semibold font-quicksand">
              Programs Enrolled
            </p>
            <NumberTicker
              value={program_count}
              className="mt-4 text-8xl font-bold text-primary font-quicksand"
            />
          </div>
        </AnimatedContent>

        {/* PROGRESS CARD */}
        <AnimatedContent delay={0.2} className="w-full flex-1">
          <div className="rounded-2xl border bg-card p-6 shadow-sm font-quicksand">
            <h2 className="font-quicksand text-xl">Learning Progress</h2>
            <p className="mb-8 mt-1 text-sm text-muted-foreground">
              Track your progress across enrolled programs.
            </p>
            <div className="space-y-7">
              {program_details.map((program) => {
                const totalSessions = Number(program.total_sessions) || 0;
                const completedSessions =
                  Number(program.completed_sessions) || 0;
                const progress =
                  totalSessions === 0
                    ? 0
                    : Math.min(
                        100,
                        Math.max(0, (completedSessions / totalSessions) * 100),
                      );

                return (
                  <div key={program.id}>
                    <div className="mb-2 flex items-center justify-between">
                      <h3 className="font-quicksand font-medium">
                        {program.title}
                      </h3>
                      <span className="text-sm text-muted-foreground">
                        {program.completed_sessions}/{program.total_sessions}
                      </span>
                    </div>
                    <Progress value={progress} />
                  </div>
                );
              })}
            </div>
          </div>
        </AnimatedContent>

        {/* PIE CHART CARD */}
        <AnimatedContent delay={0.3}>
          <Card className="flex flex-col rounded-2xl">
            <CardHeader className="items-center pb-2">
              <CardTitle className="font-quicksand">Program Status</CardTitle>

              <CardDescription className="font-quicksand">
                Distribution of your programs
              </CardDescription>
            </CardHeader>

            <CardContent>
              <ChartContainer
                config={chartConfig}
                className="mx-auto aspect-square h-[320px]"
              >
                <PieChart>
                  <Pie data={chartData} dataKey="count" nameKey="status" />

                  <ChartLegend
                    content={<ChartLegendContent nameKey="status" />}
                    className="mt-4 flex-wrap justify-center gap-4"
                  />
                </PieChart>
              </ChartContainer>
            </CardContent>
          </Card>
        </AnimatedContent>
        
      </div>

      {/* PROGRAM CARDS */}
     <div className="mt-9 ml-7 mr-7 mb-7 font-quicksand">
        <AnimatedContent delay={0.4}>
          <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <p className="text-2xl font-semibold text-foreground sm:text-3xl mb-1.5">
              Programs
            </p>

            {/* CONDITIONAL RENDERING OF THE ADD PROGRAM BUTTON */}
            {user_details.is_admin && (
              <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
                <DialogTrigger>
                  <div className="flex items-center justify-center gap-2 rounded-lg bg-primary px-3 py-2 font-quicksand">
                    <Plus className="h-4 w-4" />
                    <span>Add</span>
                  </div>
                </DialogTrigger>

                <DialogContent className="sm:max-w-lg font-quicksand">
                  <form onSubmit={handleCreateProgram}>
                    <DialogHeader className="font-quicksand">
                      <DialogTitle className="font-quicksand">
                        Add Program
                      </DialogTitle>
                      <DialogDescription className="font-quicksand">
                        Fill in the details below to create a new training
                        program.
                      </DialogDescription>
                    </DialogHeader>

                    <div className="grid gap-5 py-4 font-quicksand">
                      <div className="grid gap-2 font-quicksand">
                        <Label htmlFor="title">Program Title</Label>
                        <Input
                          id="title"
                          placeholder="Freshers Training"
                          value={title}
                          onChange={(e) => setTitle(e.target.value)}
                          required
                        />
                      </div>

                      <div className="grid gap-2 font-quicksand">
                        <Label htmlFor="description">Description</Label>
                        <Textarea
                          id="description"
                          placeholder="Enter program description..."
                          value={description}
                          onChange={(e) => setDescription(e.target.value)}
                          required
                        />
                      </div>

                      <div className="grid grid-cols-2 gap-4 font-quicksand">
                        <div className="grid gap-2">
                          <Label htmlFor="startDate">Start Date</Label>
                          <Input
                            id="startDate"
                            type="date"
                            value={startDate}
                            onChange={(e) => setStartDate(e.target.value)}
                            required
                          />
                        </div>

                        <div className="grid gap-2">
                          <Label htmlFor="endDate">End Date</Label>
                          <Input
                            id="endDate"
                            type="date"
                            value={endDate}
                            onChange={(e) => setEndDate(e.target.value)}
                            required
                          />
                        </div>
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
                      <Button type="submit" disabled={isCreating}>
                        {isCreating && (
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        )}
                        Create Program
                      </Button>
                    </DialogFooter>
                  </form>
                </DialogContent>
              </Dialog>
            )}
          </div>
        </AnimatedContent>

        {/* HANDLING THE RENDERING,UPDATE AND DELETE OF PROGRAM CARDS */}
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-3">
          {program_details.map((program, index) => (
            <div key={program.id} className="w-full">
              <AnimatedContent
                distance={30}
                direction="vertical"
                duration={0.5}
                delay={0.6 + index * 0.12}
              >
                <div className="cursor-pointer">
                  <GlowingStarsBackgroundCard>
                    <div className="flex h-full flex-col justify-between font-quicksand">
                      <div>
                        <div
                          onClick={() => handleClickProgram(program.id)}
                          className="flex items-start justify-between gap-3 "
                        >
                          <GlowingStarsTitle className="font-quicksand">
                            {program.title}
                          </GlowingStarsTitle>

                          {user_details.is_admin && (
                            <div className="flex shrink-0 items-center gap-2">
                              <button
                                type="button"
                                onClick={(e) => {
                                  handleEdit(e, program);
                                  e.stopPropagation();
                                }}
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
                                {isDeleting ? (
                                  <Loader2 className="h-5 w-5 animate-spin" />
                                ) : (
                                  <Trash className="h-5 w-5" />
                                )}
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
              <Dialog
                open={isUpdateOpen && editingProgramId === program.id}
                onOpenChange={(open) => {
                  setIsUpdateOpen(open);
                  if (!open) {
                    resetUpdateForm();
                  }
                }}
              >
                <DialogContent className="sm:max-w-lg font-quicksand">
                  <form onSubmit={handleUpdateProgram}>
                    <DialogHeader className="font-quicksand">
                      <DialogTitle className="font-quicksand">
                        Edit Program
                      </DialogTitle>
                      <DialogDescription className="font-quicksand">
                        Update the details for this program.
                      </DialogDescription>
                    </DialogHeader>

                    <div className="grid gap-5 py-4 font-quicksand">
                      <div className="grid gap-2 font-quicksand">
                        <Label htmlFor="update-title">Program Title</Label>
                        <Input
                          id="update-title"
                          placeholder="Freshers Training"
                          value={updateTitle}
                          onChange={(e) => setUpdateTitle(e.target.value)}
                          required
                        />
                      </div>

                      <div className="grid gap-2 font-quicksand">
                        <Label htmlFor="update-description">Description</Label>
                        <Textarea
                          id="update-description"
                          placeholder="Enter program description..."
                          value={updateDescription}
                          onChange={(e) => setUpdateDescription(e.target.value)}
                          required
                        />
                      </div>

                      <div className="grid grid-cols-2 gap-4 font-quicksand">
                        <div className="grid gap-2">
                          <Label htmlFor="update-startDate">Start Date</Label>
                          <Input
                            id="update-startDate"
                            type="date"
                            value={updateStartDate}
                            onChange={(e) => setUpdateStartDate(e.target.value)}
                          />
                        </div>

                        <div className="grid gap-2">
                          <Label htmlFor="update-endDate">End Date</Label>
                          <Input
                            id="update-endDate"
                            type="date"
                            value={updateEndDate}
                            onChange={(e) => setUpdateEndDate(e.target.value)}
                          />
                        </div>
                      </div>
                    </div>

                    <DialogFooter>
                      <Button
                        type="button"
                        variant="outline"
                        onClick={(e) => {
                          setIsUpdateOpen(false);
                          e.stopPropagation();
                        }}
                      >
                        Cancel
                      </Button>
                      <Button type="submit" disabled={isUpdating}>
                        {isUpdating && (
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        )}
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
