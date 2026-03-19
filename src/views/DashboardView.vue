<template>
  <div class="dashboard-container">
    <header class="header">
      <h1>我的房间</h1>
      <div class="header-actions">
        <span class="username">{{ authStore.user?.username }}</span>
        <button class="btn-logout" @click="handleLogout">退出登录</button>
      </div>
    </header>

    <div class="content">
      <div class="rooms-section">
        <div class="section-header">
          <h2>房间列表</h2>
          <button class="btn-primary" @click="showCreateRoom = true">创建房间</button>
          <button class="btn-secondary" @click="showJoinRoom = true">加入房间</button>
        </div>

        <div v-if="rooms.length === 0" class="empty-state">
          <p>你还没有加入任何房间</p>
          <p>创建一个新房间或通过邀请码加入房间</p>
        </div>

        <div class="rooms-grid">
          <div 
            v-for="room in rooms" 
            :key="room.id" 
            class="room-card"
            @click="enterRoom(room)"
          >
            <h3>{{ room.name }}</h3>
            <p>邀请码: <strong>{{ room.code }}</strong></p>
            <p>成员: {{ room.member_count }}/{{ room.max_members }}人</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建房间弹窗 -->
    <div v-if="showCreateRoom" class="modal" @click.self="showCreateRoom = false">
      <div class="modal-content">
        <h2>创建房间</h2>
        <form @submit.prevent="handleCreateRoom">
          <div class="form-group">
            <label>房间名称</label>
            <input v-model="createRoomForm.name" type="text" required />
          </div>
          <div class="form-group">
            <label>最大成员数 (2-5)</label>
            <input 
              v-model.number="createRoomForm.max_members" 
              type="number" 
              min="2" 
              max="5" 
              required 
            />
          </div>
          <div class="modal-actions">
            <button type="button" class="btn-secondary" @click="showCreateRoom = false">取消</button>
            <button type="submit" class="btn-primary">创建</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 加入房间弹窗 -->
    <div v-if="showJoinRoom" class="modal" @click.self="showJoinRoom = false">
      <div class="modal-content">
        <h2>加入房间</h2>
        <form @submit.prevent="handleJoinRoom">
          <div class="form-group">
            <label>邀请码</label>
            <input v-model="joinRoomForm.code" type="text" required placeholder="请输入6位邀请码" />
          </div>
          <div class="modal-actions">
            <button type="button" class="btn-secondary" @click="showJoinRoom = false">取消</button>
            <button type="submit" class="btn-primary">加入</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore, useRoomStore } from '@/stores'
import { getMyRooms, createRoom, joinRoom } from '@/api/room'
import { logout } from '@/api/auth'
import type { Room } from '@/api/room'

const router = useRouter()
const authStore = useAuthStore()
const roomStore = useRoomStore()

const rooms = ref<Room[]>([])
const showCreateRoom = ref(false)
const showJoinRoom = ref(false)
const createRoomForm = ref({
  name: '',
  max_members: 5
})
const joinRoomForm = ref({
  code: ''
})

async function loadRooms() {
  try {
    rooms.value = await getMyRooms()
  } catch (err) {
    console.error('加载房间失败', err)
  }
}

async function handleCreateRoom() {
  try {
    await createRoom(createRoomForm.value.name, createRoomForm.value.max_members)
    showCreateRoom.value = false
    createRoomForm.value.name = ''
    await loadRooms()
  } catch (err: any) {
    alert(err.response?.data?.detail || '创建房间失败')
  }
}

async function handleJoinRoom() {
  try {
    await joinRoom(joinRoomForm.value.code)
    showJoinRoom.value = false
    joinRoomForm.value.code = ''
    await loadRooms()
  } catch (err: any) {
    alert(err.response?.data?.detail || '加入房间失败')
  }
}

function enterRoom(room: Room) {
  roomStore.setCurrentRoom(room)
  router.push(`/room/${room.id}`)
}

async function handleLogout() {
  try {
    await logout()
  } catch (err) {
    console.error('登出失败', err)
  }
  authStore.logout()
  roomStore.clearCurrentRoom()
  router.push('/login')
}

onMounted(() => {
  loadRooms()
})
</script>

<style scoped>
.dashboard-container {
  min-height: 100vh;
  background: #f5f5f5;
}

.header {
  background: white;
  padding: 20px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header h1 {
  margin: 0;
  color: #333;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.username {
  color: #666;
  font-weight: 500;
}

.btn-logout {
  padding: 8px 16px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-logout:hover {
  background: #c82333;
}

.content {
  max-width: 1200px;
  margin: 40px auto;
  padding: 0 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.section-header h2 {
  margin: 0;
  color: #333;
}

.btn-primary {
  padding: 10px 20px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-primary:hover {
  background: #5568d3;
}

.btn-secondary {
  padding: 10px 20px;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-secondary:hover {
  background: #5a6268;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #999;
}

.empty-state p {
  margin: 10px 0;
}

.rooms-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.room-card {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.room-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
}

.room-card h3 {
  margin: 0 0 15px;
  color: #333;
  font-size: 20px;
}

.room-card p {
  margin: 10px 0;
  color: #666;
}

.room-card strong {
  color: #667eea;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 30px;
  border-radius: 8px;
  width: 100%;
  max-width: 400px;
}

.modal-content h2 {
  margin: 0 0 20px;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #333;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 10px;
  border: 2px solid #eee;
  border-radius: 4px;
  font-size: 14px;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 30px;
}

.modal-actions button {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>
