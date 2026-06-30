import { useGetMyselfQuery, useGetUserProgramStatusQuery } from "@/lib/api/user/user.api"

export function useProgramPermissions(programId: number) {
  const { data: user } = useGetMyselfQuery()
  const userId = user?.id ?? 0

  const { data: programStatus, isLoading: statusLoading } =
    useGetUserProgramStatusQuery(
      { userId, programId },
      { skip: !userId },
    )

  const isAdmin = user?.is_admin ?? false
  const isStaff = programStatus?.program_role === "STAFF"
  const isCandidate = programStatus?.program_role === "CANDIDATE"

  /**
   * Returns the session role for a given session, or null if none.
   */
  function getSessionRole(sessionId: number): string | null {
    return programStatus?.session_roles?.find(
      (sr) => sr.session_id === sessionId,
    )?.role ?? null
  }

  /**
   * Whether the user can manage training materials / assignments
   * for a given session (admin or trainer).
   */
  function canManageSessionContent(sessionId: number): boolean {
    if (isAdmin) return true
    return getSessionRole(sessionId) === "TRAINER"
  }

  return {
    /** The raw program status data. */
    programStatus,
    /** Whether the status fetch is in progress. */
    statusLoading,
    /** Global admin — full access. */
    isAdmin,
    /** Program-level role is STAFF. */
    isStaff,
    /** Program-level role is CANDIDATE. */
    isCandidate,
    /** Whether the user is either an admin or a staff member. */
    canManageUsers: isAdmin, // only admins can add/remove users
    /** Whether the user can create/edit/delete sessions (admin only). */
    canManageSessions: isAdmin,
    /** Look up a user's role in a specific session. */
    getSessionRole,
    /** Whether the user can manage materials/assignments for a session. */
    canManageSessionContent,
  }
}
