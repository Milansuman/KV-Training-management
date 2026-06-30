export interface UserResponse {
  id: number
  username: string
  display_name: string
  email: string
  is_admin: boolean
}

export interface UserCreate {
  username: string
  display_name: string
  email: string
  password: string
  is_admin: boolean
}

export interface UserUpdate {
  username?: string
  display_name?: string
  email?: string
  password?: string
  is_admin?: boolean
}
