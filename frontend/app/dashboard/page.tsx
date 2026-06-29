"use client";

import { Button } from "@/components/ui/button";
import { NumberTicker } from "@/components/ui/number-ticker";
import { Progress } from "@/components/ui/progress";
import { Plus } from "lucide-react";
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

export default function Dashboard() {
  const router = useRouter();
  const program_details = [
    {
      id: 1,
      title: "Freshers Training",
      description: "Training for freshers",
      start_date: "12-03-2026",
      end_date: "27-04-2026",
      totalSessions: 5,
      completedSessions: 2,
    },
    {
      id: 2,
      title: "AI Advanced Training",
      description: "Training for backend developers",
      start_date: "12-03-2026",
      end_date: "27-04-2026",
      totalSessions: 8,
      completedSessions: 1,
    },
  ];

  const program_count = program_details.length;
  const user_details = {
    id: 12,
    username: "aswini1212",
    display_name: "Aswini P",
    email: "aswinipriya2004@gmail.com",
    is_admin: true,
  };

  function handleClickProgram() {
    router.push(`dashboard/program/{id}`);
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
                (program.completedSessions / program.totalSessions) * 100;

              return (
                <div key={program.id}>
                  <div className="mb-2 flex items-center justify-between">
                    <h3 className="font-quicksand font-medium">
                      {program.title}
                    </h3>

                    <span className="text-sm text-muted-foreground">
                      {program.completedSessions}/{program.totalSessions}
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
      <div className="mt-9 ml-7 mr-7 mb-7">
        <div className="mb-4  flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <p className="font-quicksand text-2xl font-semibold text-foreground sm:text-3xl">
            Programs
          </p>

          {/* CONDITIONAL RENDERING OF THE ADD PROGRAM BUTTON */}
          {user_details.is_admin && (
            <Dialog>
              <DialogTrigger>
                <div className="bg-primary font-quicksand flex flex-row items-center rounded-md mg-4 p-1 ">
                    <Plus className="mr-2 h-4 w-4" />
                     Add
                </div>
              </DialogTrigger>

              <DialogContent className="sm:max-w-lg">
              <DialogHeader>
                <DialogTitle>Add Program</DialogTitle>

                <DialogDescription>
                  Fill in the details below to create a new training program.
                </DialogDescription>
              </DialogHeader>

              <div className="grid gap-5 py-4">
                <div className="grid gap-2">
                  <Label htmlFor="title">Program Title</Label>

                  <Input id="title" placeholder="Freshers Training" />
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="description">Description</Label>

                  <Textarea
                    id="description"
                    placeholder="Enter program description..."
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="grid gap-2">
                    <Label>Start Date</Label>
                    <Input type="date" />
                  </div>

                  <div className="grid gap-2">
                    <Label>End Date</Label>
                    <Input type="date" />
                  </div>
                </div>
              </div>

              <DialogFooter>
                <Button variant="outline">Cancel</Button>

                <Button>Create Program</Button>
              </DialogFooter>
            </DialogContent>
            </Dialog>
          )}
        </div>

        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-3">
          {program_details.map((program) => (
            <div
              key={program.id}
              onClick={handleClickProgram}
              className="group rounded-2xl border bg-card p-6 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-primary hover:shadow-lg"
            >
              <div className="space-y-3">
                <h3 className="font-quicksand text-xl font-semibold text-foreground group-hover:text-primary">
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
