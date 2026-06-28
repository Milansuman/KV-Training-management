export type RegisterRequest = {
  username: string
  email: string
  display_name: string
  password: string
}

export type LoginRequest = {
  username_or_email: string
  password: string
}

export type GoogleAuthRequest = {
  code: string
}

export type UserResponse = {
  id: number
  username: string
  email: string
  display_name: string
  is_admin: boolean
}

export type TokenResponse = {
  access_token: string
  refresh_token: string
}
