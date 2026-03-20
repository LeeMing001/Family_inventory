import api from './index'

export interface User {
  id: number
  username: string
  created_at: string
  is_active: boolean
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

export async function register(username: string, password: string) {
  const formData = new FormData()
  formData.append('username', username)
  formData.append('password', password)
  
  const response = await api.post<User>('/api/auth/register', {
    username,
    password
  })
  return response.data
}

export async function login(username: string, password: string) {
  const formData = new FormData()
  formData.append('username', username)
  formData.append('password', password)
  
  const response = await api.post<LoginResponse>('/api/auth/login', formData)
  return response.data
}

export async function getCurrentUser() {
  const response = await api.get<User>('/api/auth/me')
  return response.data
}

export async function logout() {
  await api.post('/api/auth/logout')
}
