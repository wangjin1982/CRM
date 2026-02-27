export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
  timestamp: number
}

export interface ErrorResponse {
  code: number
  message: string
  errors?: ValidationError[]
  timestamp: number
}

export interface ValidationError {
  field: string
  message: string
}
