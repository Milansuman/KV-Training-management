"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { Loader2, Trash, Plus } from "lucide-react";
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
import { toast } from "sonner";

import { useGetMyselfQuery } from "@/lib/api/user/user.api";
import { useGetAllUsersQuery } from "@/lib/api/user/user.api";
import {
  useListProgramPermissionsQuery,
  useAddPersonToProgramMutation,
  useUpdatePersonInProgramMutation,
  useRemovePersonFromProgramMutation,
} from "@/lib/api/program-permissions/program-permissions.api";
import {
  useGetSessionsWithRoleQuery,
  useAddSessionPermissionMutation,
  useUpdateSessionPermissionMutation,
} from "@/lib/api/session-permissions/session-permissions.api";
import type { SessionRole } from "@/lib/api/session-permissions/session-permissions.type";
import type {
  ListProgramPermissionItem,
  ProgramRole,
} from "@/lib/api/program-permissions/program-permissions.type";

function getErrorDetail(err: unknown): string {
  const data = (err as { data?: { detail?: string; message?: string } })?.data;
  return data?.detail || data?.message || "An error occurred";
}

export default function UsersPage() {
  const params = useParams<{ id: string }>();
  const programId = Number(params.id);

  const { data: currentUser } = useGetMyselfQuery();
  const { data: allUsers = [] } = useGetAllUsersQuery();
  const {
    data: programMembers = [],
    isLoading: membersLoading,
  } = useListProgramPermissionsQuery(programId);

  const [addPerson, { isLoading: isAddingPerson }] =
    useAddPersonToProgramMutation();
  const [updatePerson, { isLoading: isUpdatingPerson }] =
    useUpdatePersonInProgramMutation();
  const [removePerson, { isLoading: isRemovingPerson }] =
    useRemovePersonFromProgramMutation();

  // Helper: map program member to display info
  const membersWithDetails = programMembers.map((pm) => {
    return {
      permission_id: pm.permission_id,
      user_id: pm.user_id,
      username: pm.username,
      display_name: pm.display_name,
      role: pm.role,
    };
  });

  // ── Add User dialog ─────────────────────────────────────────────
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [selectedUserIds, setSelectedUserIds] = useState<Set<number>>(new Set());
  const [newRole, setNewRole] = useState<ProgramRole>("CANDIDATE");

  const usersNotInProgram = allUsers.filter(
    (u) => !programMembers.some((pm) => pm.user_id === u.id),
  );

  function toggleUserSelection(userId: number) {
    setSelectedUserIds((prev) => {
      const next = new Set(prev);
      if (next.has(userId)) {
        next.delete(userId);
      } else {
        next.add(userId);
      }
      return next;
    });
  }

  async function handleAddUser() {
    if (selectedUserIds.size === 0) {
      toast.error("Please select at least one user.");
      return;
    }
    try {
      for (const userId of selectedUserIds) {
        await addPerson({
          user_id: userId,
          program_id: programId,
          role: newRole,
        }).unwrap();
      }
      toast.success(`${selectedUserIds.size} user(s) added to program.`);
      setIsAddOpen(false);
      setSelectedUserIds(new Set());
      setNewRole("CANDIDATE");
    } catch (err) {
      toast.error(getErrorDetail(err));
    }
  }

  async function handleRemoveUser(permissionId: number) {
    try {
      await removePerson(permissionId).unwrap();
      toast.success("User removed from program.");
    } catch (err) {
      toast.error(getErrorDetail(err));
    }
  }

  // ── Manage Sessions dialog ─────────────────────────────────────
  const [selectedUser, setSelectedUser] =
    useState<ListProgramPermissionItem | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  // Fetch sessions with role for the selected user
  const { data: sessionsWithRole = [], isLoading: sessionsLoading } =
    useGetSessionsWithRoleQuery(
      { programId, userId: selectedUser?.user_id ?? 0 },
      { skip: !selectedUser },
    );

  const [addSessionPerm] = useAddSessionPermissionMutation();
  const [updateSessionPerm] = useUpdateSessionPermissionMutation();

  // Track which sessions are selected for assignment
  const [selectedSessionIds, setSelectedSessionIds] = useState<Set<number>>(
    new Set(),
  );

  function handleOpenManageSessions(member: ListProgramPermissionItem) {
    setSelectedUser(member);
    setSelectedSessionIds(new Set());
    setDialogOpen(true);
  }

  function toggleSessionSelection(sessionId: number) {
    setSelectedSessionIds((prev) => {
      const next = new Set(prev);
      if (next.has(sessionId)) {
        next.delete(sessionId);
      } else {
        next.add(sessionId);
      }
      return next;
    });
  }

  // ── Role change handler for Manage Sessions dialog ──────────

  async function handleSessionRoleChange(
    sessionId: number,
    newRoleValue: SessionRole,
  ) {
    if (!selectedUser) return;

    const existing = sessionsWithRole.find((s) => s.id === sessionId);

    try {
      if (existing?.role) {
        await updateSessionPerm({
          permissionId: sessionId,
          body: { role: newRoleValue },
        }).unwrap();
      } else {
        await addSessionPerm({
          user_id: selectedUser.user_id,
          session_id: sessionId,
          role: newRoleValue,
        }).unwrap();
      }
    } catch (err) {
      toast.error(getErrorDetail(err));
    }
  }

  async function handleSaveSessionChanges() {
    if (!selectedUser) return;

    try {
      // For each selected session, create a permission
      for (const sessionId of selectedSessionIds) {
        const existing = sessionsWithRole.find((s) => s.id === sessionId);
        if (!existing?.role) {
          await addSessionPerm({
            user_id: selectedUser.user_id,
            session_id: sessionId,
            role: "CANDIDATE",
          }).unwrap();
        }
      }
      toast.success("Session assignments saved.");
      setDialogOpen(false);
    } catch (err) {
      toast.error(getErrorDetail(err));
    }
  }

  if (membersLoading) {
    return (
      <div className="flex h-[70vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <>
      <div className="flex h-full w-full justify-center px-12 py-10">
        <div className="w-full">
          {/* Heading */}
          <div className="mb-8 flex items-center justify-between">
            <div>
              <h1 className="font-quicksand text-4xl font-semibold">
                Users Details
              </h1>
              <p className="mt-2 text-lg text-muted-foreground">
                Manage the users enrolled in this program and assign their
                roles.
              </p>
            </div>

            {currentUser?.is_admin && (
              <Button onClick={() => setIsAddOpen(true)}>
                <Plus data-icon="inline-start" />
                Add User
              </Button>
            )}
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
                {membersWithDetails.length === 0 ? (
                  <TableRow>
                    <TableCell
                      colSpan={5}
                      className="h-40 text-center text-muted-foreground"
                    >
                      No users enrolled in this program yet.
                    </TableCell>
                  </TableRow>
                ) : (
                  membersWithDetails.map((member) => (
                    <TableRow
                      key={member.permission_id}
                      className="h-20 text-center font-quicksand hover:bg-muted/30"
                    >
                      <TableCell>{member.user_id}</TableCell>
                      <TableCell>{member.username}</TableCell>
                      <TableCell>{member.display_name}</TableCell>
                      <TableCell>
                        <Select
                          defaultValue={member.role}
                          disabled={isUpdatingPerson}
                          onValueChange={async (v) => {
                            try {
                              await updatePerson({
                                permissionId: member.permission_id,
                                body: { role: v as ProgramRole },
                              }).unwrap();
                              toast.success(
                                `${member.display_name}'s role updated to ${v}.`,
                              );
                            } catch (err) {
                              toast.error(getErrorDetail(err));
                            }
                          }}
                        >
                          <SelectTrigger className="w-40 uppercase">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="CANDIDATE">
                              Candidate
                            </SelectItem>
                            <SelectItem value="STAFF">Staff</SelectItem>
                          </SelectContent>
                        </Select>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center justify-center gap-3">
                          <Button
                            variant="ghost"
                            size="icon"
                            disabled={
                              isRemovingPerson ||
                              member.user_id === currentUser?.id
                            }
                            onClick={() =>
                              handleRemoveUser(member.permission_id)
                            }
                            className="hover:bg-destructive/10 hover:text-destructive"
                          >
                            {isRemovingPerson ? (
                              <Loader2 className="h-5 w-5 animate-spin" />
                            ) : (
                              <Trash className="h-5 w-5" />
                            )}
                          </Button>

                          <Button
                            className="rounded-full bg-primary px-6 text-white"
                            onClick={() => handleOpenManageSessions(member)}
                          >
                            Manage Sessions
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </div>
      </div>

      {/* ── Add User Dialog ───────────────────────────────────── */}
      <Dialog open={isAddOpen} onOpenChange={setIsAddOpen}>
        <DialogContent className="min-w-[700px] rounded-2xl font-quicksand max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Add User(s) to Program</DialogTitle>
            <DialogDescription>
              Select users from the table below and assign a program role for
              all selected users.
            </DialogDescription>
          </DialogHeader>

          {/* ── Role selector (applies to all selected) ── */}
          <div className="flex items-center gap-4 py-2">
            <label className="text-sm font-medium whitespace-nowrap">
              Program Role
            </label>
            <Select
              value={newRole}
              onValueChange={(v) => setNewRole(v as ProgramRole)}
            >
              <SelectTrigger className="w-48">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="CANDIDATE">Candidate</SelectItem>
                <SelectItem value="STAFF">Staff</SelectItem>
              </SelectContent>
            </Select>

            <span className="ml-auto text-sm text-muted-foreground">
              {selectedUserIds.size} selected
            </span>
          </div>

          {/* ── Users table with checkboxes ── */}
          <div className="max-h-80 overflow-y-auto rounded-xl border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-12">
                    <Checkbox
                      checked={
                        usersNotInProgram.length > 0 &&
                        usersNotInProgram.every((u) =>
                          selectedUserIds.has(u.id),
                        )
                      }
                      onCheckedChange={() => {
                        const allSelected = usersNotInProgram.every((u) =>
                          selectedUserIds.has(u.id),
                        );
                        if (allSelected) {
                          setSelectedUserIds(new Set());
                        } else {
                          setSelectedUserIds(
                            new Set(usersNotInProgram.map((u) => u.id)),
                          );
                        }
                      }}
                    />
                  </TableHead>
                  <TableHead>ID</TableHead>
                  <TableHead>Username</TableHead>
                  <TableHead>Display Name</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {usersNotInProgram.length === 0 ? (
                  <TableRow>
                    <TableCell
                      colSpan={4}
                      className="h-28 text-center text-muted-foreground"
                    >
                      All users are already enrolled in this program.
                    </TableCell>
                  </TableRow>
                ) : (
                  usersNotInProgram.map((user) => (
                    <TableRow
                      key={user.id}
                      className={
                        selectedUserIds.has(user.id)
                          ? "bg-muted/40"
                          : undefined
                      }
                    >
                      <TableCell>
                        <Checkbox
                          checked={selectedUserIds.has(user.id)}
                          onCheckedChange={() => toggleUserSelection(user.id)}
                        />
                      </TableCell>
                      <TableCell>{user.id}</TableCell>
                      <TableCell>{user.username}</TableCell>
                      <TableCell>{user.display_name}</TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>

          <DialogFooter className="mt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                setIsAddOpen(false);
                setSelectedUserIds(new Set());
                setNewRole("CANDIDATE");
              }}
            >
              Cancel
            </Button>
            <Button
              onClick={handleAddUser}
              disabled={selectedUserIds.size === 0 || isAddingPerson}
            >
              {isAddingPerson && (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              )}
              Add {selectedUserIds.size > 0 && `(${selectedUserIds.size})`} to Program
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* ── Manage Sessions Dialog ────────────────────────────── */}
      <Dialog
        open={dialogOpen}
        onOpenChange={(open) => {
          setDialogOpen(open);
          if (!open) setSelectedUser(null);
        }}
      >
        <DialogContent className="min-w-[800px] rounded-2xl font-quicksand">
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

          {sessionsLoading ? (
            <div className="flex items-center justify-center py-10">
              <Loader2 className="h-6 w-6 animate-spin text-primary" />
            </div>
          ) : (
            <div className="mt-6 overflow-y-auto rounded-xl border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-16">
                      <Checkbox
                        checked={
                          sessionsWithRole.length > 0 &&
                          sessionsWithRole.every((s) => s.role)
                        }
                        onCheckedChange={() => {
                          // Select/deselect all
                          const allSelected = sessionsWithRole.every((s) =>
                            selectedSessionIds.has(s.id),
                          );
                          if (allSelected) {
                            setSelectedSessionIds(new Set());
                          } else {
                            setSelectedSessionIds(
                              new Set(sessionsWithRole.map((s) => s.id)),
                            );
                          }
                        }}
                      />
                    </TableHead>
                    <TableHead>Session Name</TableHead>
                    <TableHead>Description</TableHead>
                    <TableHead className="w-56">Role</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {sessionsWithRole.length === 0 ? (
                    <TableRow>
                      <TableCell
                        colSpan={4}
                        className="h-20 text-center text-muted-foreground"
                      >
                        No sessions available in this program.
                      </TableCell>
                    </TableRow>
                  ) : (
                    sessionsWithRole.map((session) => (
                      <TableRow key={session.id}>
                        <TableCell>
                          <Checkbox
                            checked={selectedSessionIds.has(session.id)}
                            onCheckedChange={() =>
                              toggleSessionSelection(session.id)
                            }
                          />
                        </TableCell>
                        <TableCell className="font-medium">
                          {session.title}
                        </TableCell>
                        <TableCell>{session.description}</TableCell>
                        <TableCell>
                          <Select
                            defaultValue={session.role ?? undefined}
                            onValueChange={(v) =>
                              handleSessionRoleChange(session.id, v as SessionRole)
                            }
                          >
                            <SelectTrigger>
                              <SelectValue placeholder="No role" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="TRAINER">
                                Trainer
                              </SelectItem>
                              <SelectItem value="MODERATOR">
                                Moderator
                              </SelectItem>
                              <SelectItem value="CANDIDATE">
                                Candidate
                              </SelectItem>
                            </SelectContent>
                          </Select>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </div>
          )}

          <DialogFooter className="mt-6">
            <DialogClose>
              <Button variant="outline">Cancel</Button>
            </DialogClose>
            <Button
              className="bg-primary text-white"
              onClick={handleSaveSessionChanges}
            >
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
