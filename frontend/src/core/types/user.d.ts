export interface UserResponse {
  id: number
  username: string
  email: string
  phone?: string
  real_name?: string
  avatar?: string
  status: number
  department_id?: number
  position?: string
  is_admin: boolean
  last_login_at?: string
  created_at: string
  updated_at: string
  roles?: string[]
}

export interface UserCreate {
  username: string
  email: string
  phone?: string
  real_name?: string
  password: string
  department_id?: number
  position?: string
  role_ids?: number[]
}

export interface UserUpdate {
  email?: string
  phone?: string
  real_name?: string
  avatar?: string
  department_id?: number
  position?: string
  status?: number
  role_ids?: number[]
}

export interface PageParams {
  page: number
  page_size: number
  keyword?: string
  status?: number
}

export interface PageResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}
