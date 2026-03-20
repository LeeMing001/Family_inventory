import api from './index'

export interface Room {
  id: number
  name: string
  code: string
  owner_id: number
  created_at: string
  member_count: number
  max_members: number
}

export interface RoomMember {
  id: number
  user_id: number
  room_id: number
  joined_at: string
  username: string
}

export async function createRoom(name: string, maxMembers: number = 5) {
  const response = await api.post<Room>('/api/rooms', {
    name,
    max_members: maxMembers
  })
  return response.data
}

export async function joinRoom(code: string) {
  const response = await api.post('/api/rooms/join', { code })
  return response.data
}

export async function getMyRooms() {
  const response = await api.get<Room[]>('/api/rooms')
  return response.data
}

export async function getRoom(roomId: number) {
  const response = await api.get<Room>(`/api/rooms/${roomId}`)
  return response.data
}

export async function getRoomMembers(roomId: number) {
  const response = await api.get<RoomMember[]>(`/api/rooms/${roomId}/members`)
  return response.data
}
