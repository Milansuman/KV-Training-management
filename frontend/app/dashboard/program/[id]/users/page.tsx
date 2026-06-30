"use client";

import { useState } from "react";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogClose,
} from "@/components/ui/dialog";

import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";

import { Trash } from "lucide-react";

const users = [
  {
    id: 1,
    username: "john_doe",
    display_name: "John Doe",
    role: "candidate",
  },
  {
    id: 2,
    username: "jane_smith",
    display_name: "Jane Smith",
    role: "staff",
  },
  {
    id: 3,
    username: "alex_wilson",
    display_name: "Alex Wilson",
    role: "candidate",
  },
  {
    id: 4,
    username: "emma_jones",
    display_name: "Emma Jones",
    role: "staff",
  },
  {
    id: 5,
    username: "oliver_lee",
    display_name: "Oliver Lee",
    role: "candidate",
  },
  {
    id: 6,
    username: "sophia_walker",
    display_name: "Sophia Walker",
    role: "staff",
  },
];

const sessions = [
  {
    id: 1,
    name: "Introduction",
    description: "Course overview and orientation",
    role: "candidate",
  },
  {
    id: 2,
    name: "React Basics",
    description: "React fundamentals",
    role: "trainer",
  },
  {
    id: 3,
    name: "Redux Toolkit",
    description: "State management",
    role: "moderator",
  },
  {
    id: 4,
    name: "Final Assessment",
    description: "Evaluation session",
    role: "candidate",
  },
];

export default function UsersPage() {
  const [selectedUser, setSelectedUser] = useState<
    (typeof users)[0] | null
  >(null);

  const [dialogOpen, setDialogOpen] = useState(false);

  return (
    <>
      <div className="flex h-full w-full justify-center px-12 py-10">
        <div className="w-full">
          {/* Heading */}

          <div className="mb-8">
            <h1 className="font-quicksand text-4xl font-semibold">
              Users Details
            </h1>

            <p className="mt-2 text-lg text-muted-foreground">
              Manage the users enrolled in this program and assign their roles.
            </p>
          </div>

          {/* Users Table */}

          <div className="overflow-auto rounded-2xl border border-border bg-card shadow-lg">
            <Table className="table-fixed w-full">
              <TableHeader>
                <TableRow className="h-16 bg-muted/40 text-center font-quicksand">
                  <TableHead className="w-20 text-center text-lg">
                    ID
                  </TableHead>

                  <TableHead className="w-64 text-center text-lg">
                    Username
                  </TableHead>

                  <TableHead className="w-72 text-center text-lg">
                    Display Name
                  </TableHead>

                  <TableHead className="w-60 text-center text-lg">
                    Role
                  </TableHead>

                  <TableHead className="w-72 text-center text-lg">
                    Actions
                  </TableHead>
                </TableRow>
              </TableHeader>

              <TableBody>
                {users.map((user) => (
                  <TableRow
                    key={user.id}
                    className="h-20 text-center font-quicksand hover:bg-muted/30"
                  >
                    <TableCell>{user.id}</TableCell>

                    <TableCell>{user.username}</TableCell>

                    <TableCell>{user.display_name}</TableCell>

                    <TableCell>
                      <Select defaultValue={user.role}>
                        <SelectTrigger className="mx-auto w-44">
                          <SelectValue />
                        </SelectTrigger>

                        <SelectContent>
                          <SelectItem value="candidate">
                            Candidate
                          </SelectItem>

                          <SelectItem value="staff">
                            Staff
                          </SelectItem>
                        </SelectContent>
                      </Select>
                    </TableCell>

                    <TableCell>
                      <div className="flex items-center justify-center gap-3">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="hover:bg-destructive/10 hover:text-destructive"
                        >
                          <Trash className="h-5 w-5" />
                        </Button>

                        <Button
                          className="rounded-full bg-primary px-6 text-white"
                          onClick={() => {
                            setSelectedUser(user);
                            setDialogOpen(true);
                          }}
                        >
                          Manage Sessions
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>
      </div>

      {/* Dialog */}

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="lg:min-w-[800px] rounded-2xl font-quicksand">
          <DialogHeader>
            <DialogTitle className="text-2xl font-quicksand">
              Manage Sessions
            </DialogTitle>

            <DialogDescription>
              {selectedUser && (
                <>
                  Assign sessions for{" "}
                  <span className="font-semibold text-foreground">
                    {selectedUser.display_name}
                  </span>
                </>
              )}
            </DialogDescription>
          </DialogHeader>

          <div className="mt-6  overflow-y-auto rounded-xl border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-16">
                    <Checkbox />
                  </TableHead>

                  <TableHead>Session Name</TableHead>

                  <TableHead>Description</TableHead>

                  <TableHead className="w-56">
                    Role
                  </TableHead>
                </TableRow>
              </TableHeader>

              <TableBody>
                {sessions.map((session) => (
                  <TableRow key={session.id}>
                    <TableCell>
                      <Checkbox />
                    </TableCell>

                    <TableCell className="font-medium">
                      {session.name}
                    </TableCell>

                    <TableCell>
                      {session.description}
                    </TableCell>

                    <TableCell>
                      <Select defaultValue={session.role}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>

                        <SelectContent>
                          <SelectItem value="trainer">
                            Trainer
                          </SelectItem>

                          <SelectItem value="moderator">
                            Moderator
                          </SelectItem>

                          <SelectItem value="candidate">
                            Candidate
                          </SelectItem>
                        </SelectContent>
                      </Select>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          <DialogFooter className="mt-6">
            <DialogClose >
              <Button variant="outline">
                Cancel
              </Button>
            </DialogClose>

            <Button
              className="bg-primary text-white"
              onClick={() => setDialogOpen(false)}
            >
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}