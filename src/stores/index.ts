import { defineStore } from 'pinia'
import { ref } from 'vue'

interface User {
  id: number
  username: string
  created_at: string
  is_active: boolean
}

interface Room {
  id: number
  name: string
  code: string
  owner_id: number
  created_at: string
  member_count: number
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<User | null>(null)

  function setToken(newToken: string) {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  function setUser(newUser: User) {
    user.value = newUser
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
  }

  function isAuthenticated() {
    return !!token.value
  }

  return {
    token,
    user,
    setToken,
    setUser,
    logout,
    isAuthenticated
  }
})

export const useRoomStore = defineStore('room', () => {
  const currentRoom = ref<Room | null>(null)

  function setCurrentRoom(room: Room) {
    currentRoom.value = room
  }

  function clearCurrentRoom() {
    currentRoom.value = null
  }

  return {
    currentRoom,
    setCurrentRoom,
    clearCurrentRoom
  }
})
