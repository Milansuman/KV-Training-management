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
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { useGetMyselfQuery } from "@/lib/api/user/user.api";
import {
  useGetProgramProgressQuery,
  useCreateProgramMutation,
} from "@/lib/api/programs/programs.api";
import { toast } from "sonner";

export default function Dashboard() {
  const router = useRouter();
  const { data: user_details, isLoading: userLoading } = useGetMyselfQuery();
  const { data: program_details = [], isLoading: programsLoading } =
    useGetProgramProgressQuery(user_details?.id ?? 0, {
      skip: !user_details,
    });

  const [createProgram, { isLoading: isCreating }] = useCreateProgramMutation();

  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  const program_count = program_details.length;

  function handleClickProgram(id: number) {
    router.push(`/dashboard/program/${id}`);
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
    } catch (err: any) {
      toast.error(err?.data?.detail || err?.data?.message || "Failed to create program");
    }
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

  return (
    <>
      <div className="flex flex-col-reverse gap-6 p-6 lg:flex-row">
        {/* Number Card */}
        <div className="flex w-full lg:w-52 flex-col items-center justify-center rounded-2xl border bg-card p-6 shadow-sm font-quicksand">
          <p className="text-center text-lg font-medium text-muted-foreground ">
            Programs Enrolled
          </p>
          <NumberTicker
            value={program_count}
            className="mt-4 text-6xl font-bold text-primary"
          />
        </div>

        {/* Progress Card */}
        <div className="w-full flex-1 rounded-2xl border bg-card p-6 shadow-sm font-quicksand">
          <h2 className="font-quicksand text-xl">Learning Progress</h2>
          <p className="mb-8 mt-1 text-sm text-muted-foreground">
            Track your progress across enrolled programs.
          </p>
          <div className="space-y-7">
            {program_details.map((program) => {
              const progress =
                program.total_sessions > 0
                  ? (program.completed_sessions / program.total_sessions) * 100
                  : 0;

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
                  <Progress value={progress} className="[&>div]:bg-[#2757ff]" />
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* PROGRAM CARDS */}
      <div className="mt-9 ml-7 mr-7 mb-7 font-quicksand">
        <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-2xl font-semibold text-foreground sm:text-3xl">
            Programs
          </p>

          {/* CONDITIONAL RENDERING OF THE ADD PROGRAM BUTTON */}
          {user_details.is_admin && (
            <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
              <DialogTrigger asChild>
                <Button className="flex flex-row items-center">
                  <Plus className="mr-2 h-4 w-4" />
                  Add
                </Button>
              </DialogTrigger>

              <DialogContent className="sm:max-w-lg">
                <form onSubmit={handleCreateProgram}>
                  <DialogHeader>
                    <DialogTitle>Add Program</DialogTitle>
                    <DialogDescription>
                      Fill in the details below to create a new training program.
                    </DialogDescription>
                  </DialogHeader>

                  <div className="grid gap-5 py-4">
                    <div className="grid gap-2">
                      <Label htmlFor="title">Program Title</Label>
                      <Input
                        id="title"
                        placeholder="Freshers Training"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        required
                      />
                    </div>

                    <div className="grid gap-2">
                      <Label htmlFor="description">Description</Label>
                      <Textarea
                        id="description"
                        placeholder="Enter program description..."
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        required
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
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
                      {isCreating && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                      Create Program
                    </Button>
                  </DialogFooter>
                </form>
              </DialogContent>
            </Dialog>
          )}
        </div>

        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-3">
          {program_details.map((program) => (
            <div
              key={program.id}
              onClick={() => handleClickProgram(program.id)}
              className="group cursor-pointer rounded-2xl border bg-card p-6 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-primary hover:shadow-lg"
            >
              <div className="space-y-3">
                <h3 className="text-xl font-semibold text-foreground group-hover:text-primary">
                  {program.title}
                </h3>
                <p className="line-clamp-3 text-sm leading-6 text-muted-foreground">
                  {program.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
