<template>
  <div class="room-container">
    <header class="header">
      <div class="header-left">
        <button class="btn-back" @click="goBack">← 返回</button>
        <h1>{{ roomStore.currentRoom?.name }}</h1>
        <span class="room-code">邀请码: {{ roomStore.currentRoom?.code }}</span>
      </div>
      <div class="header-right">
        <span class="username">{{ authStore.user?.username }}</span>
        <button class="btn-logout" @click="handleLogout">退出登录</button>
      </div>
    </header>

    <div class="content">
      <div class="toolbar">
        <button class="btn-primary" @click="showCreateContainer = true">创建容器/分区</button>
        <button class="btn-success" @click="showCreateItem = true">添加物品</button>
      </div>

      <div v-if="loading" class="loading">加载中...</div>

      <div v-else-if="resourceTree.length === 0" class="empty-state">
        <p>还没有创建任何资源</p>
        <button class="btn-primary" @click="showCreateContainer = true">创建第一个容器</button>
      </div>

      <div v-else class="resource-tree">
        <ResourceNode 
          v-for="resource in resourceTree" 
          :key="resource.id" 
          :resource="resource"
          :room-id="roomId"
          @edit="handleEditResource"
          @delete="handleDeleteResource"
          @add-child="handleAddChild"
        />
      </div>
    </div>

    <!-- 创建容器弹窗 -->
    <div v-if="showCreateContainer" class="modal" @click.self="showCreateContainer = false">
      <div class="modal-content">
        <h2>创建容器/分区</h2>
        <form @submit.prevent="handleCreateResource(true)">
          <div class="form-group">
            <label>名称</label>
            <input v-model="resourceForm.name" type="text" required placeholder="例如：厨房、冰箱" />
          </div>
          <div class="form-group">
            <label>描述</label>
            <input v-model="resourceForm.description" type="text" placeholder="选填" />
          </div>
          <div class="form-group">
            <label>父级容器</label>
            <select v-model="resourceForm.parent_id">
              <option value="">无（作为一级容器）</option>
              <option v-for="container in allContainers" :key="container.id" :value="container.id">
                {{ container.name }}
              </option>
            </select>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn-secondary" @click="showCreateContainer = false">取消</button>
            <button type="submit" class="btn-primary">创建</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 创建物品弹窗 -->
    <div v-if="showCreateItem" class="modal" @click.self="showCreateItem = false">
      <div class="modal-content">
        <h2>添加物品</h2>
        <form @submit.prevent="handleCreateResource(false)">
          <div class="form-group">
            <label>物品名称</label>
            <input v-model="resourceForm.name" type="text" required placeholder="例如：大米、鸡蛋" />
          </div>
          <div class="form-group">
            <label>描述</label>
            <input v-model="resourceForm.description" type="text" placeholder="选填" />
          </div>
          <div class="form-group">
            <label>数量</label>
            <input v-model.number="resourceForm.quantity" type="number" min="1" required />
          </div>
          <div class="form-group">
            <label>所属容器</label>
            <select v-model="resourceForm.parent_id" required>
              <option value="">请选择容器</option>
              <option v-for="container in allContainers" :key="container.id" :value="container.id">
                {{ container.name }}
              </option>
            </select>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn-secondary" @click="showCreateItem = false">取消</button>
            <button type="submit" class="btn-primary">添加</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 编辑资源弹窗 -->
    <div v-if="showEdit" class="modal" @click.self="showEdit = false">
      <div class="modal-content">
        <h2>编辑{{ currentEditResource?.is_container ? '容器' : '物品' }}</h2>
        <form @submit.prevent="handleUpdateResource">
          <div class="form-group">
            <label>名称</label>
            <input v-model="editForm.name" type="text" required />
          </div>
          <div class="form-group">
            <label>描述</label>
            <input v-model="editForm.description" type="text" />
          </div>
          <div v-if="!currentEditResource?.is_container" class="form-group">
            <label>数量</label>
            <input v-model.number="editForm.quantity" type="number" min="1" required />
          </div>
          <div class="modal-actions">
            <button type="button" class="btn-secondary" @click="showEdit = false">取消</button>
            <button type="submit" class="btn-primary">保存</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 添加子资源弹窗 -->
    <div v-if="showAddChild && parentResource" class="modal" @click.self="showAddChild = false">
      <div class="modal-content">
        <h2>添加到{{ parentResource.name }}</h2>
        <form @submit.prevent="handleCreateResource(false, parentResource.id)">
          <div class="form-group">
            <label>名称</label>
            <input v-model="resourceForm.name" type="text" required />
          </div>
          <div class="form-group">
            <label>描述</label>
            <input v-model="resourceForm.description" type="text" placeholder="选填" />
          </div>
          <div class="form-group">
            <label>类型</label>
            <div class="radio-group">
              <label>
                <input type="radio" v-model="resourceForm.is_container" :value="true" />
                容器（可以包含其他东西）
              </label>
              <label>
                <input type="radio" v-model="resourceForm.is_container" :value="false" />
                物品
              </label>
            </div>
          </div>
          <div v-if="!resourceForm.is_container" class="form-group">
            <label>数量</label>
            <input v-model.number="resourceForm.quantity" type="number" min="1" required />
          </div>
          <div class="modal-actions">
            <button type="button" class="btn-secondary" @click="showAddChild = false">取消</button>
            <button type="submit" class="btn-primary">添加</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore, useRoomStore } from '@/stores'
import { 
  getResourceTree, 
  createResource, 
  updateResource, 
  deleteResource,
  getResources
} from '@/api/inventory'
import { logout } from '@/api/auth'
import type { ResourceWithChildren, Resource } from '@/api/inventory'
import ResourceNode from '@/components/ResourceNode.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const roomStore = useRoomStore()

const roomId = parseInt(route.params.roomId as string)
const loading = ref(false)
const resourceTree = ref<ResourceWithChildren[]>([])
const allContainers = ref<Resource[]>([])

// 弹窗控制
const showCreateContainer = ref(false)
const showCreateItem = ref(false)
const showEdit = ref(false)
const showAddChild = ref(false)
const parentResource = ref<Resource | null>(null)
const currentEditResource = ref<Resource | null>(null)

// 表单数据
const resourceForm = ref({
  name: '',
  description: '',
  quantity: 1,
  is_container: false,
  parent_id: undefined as number | undefined
})

const editForm = ref({
  name: '',
  description: '',
  quantity: 1
})

async function loadData() {
  loading.value = true
  try {
    resourceTree.value = await getResourceTree(roomId)
    allContainers.value = await getResources(roomId, undefined, true)
  } catch (err) {
    console.error('加载数据失败', err)
  } finally {
    loading.value = false
  }
}

async function handleCreateResource(isContainer: boolean, parentId?: number) {
  try {
    await createResource(roomId, {
      name: resourceForm.value.name,
      description: resourceForm.value.description,
      quantity: isContainer ? undefined : resourceForm.value.quantity,
      is_container: isContainer,
      parent_id: parentId || resourceForm.value.parent_id
    })
    
    if (showCreateContainer.value) showCreateContainer.value = false
    if (showCreateItem.value) showCreateItem.value = false
    if (showAddChild.value) {
      showAddChild.value = false
      parentResource.value = null
    }
    
    resourceForm.value = { name: '', description: '', quantity: 1, is_container: false, parent_id: undefined }
    await loadData()
  } catch (err: any) {
    alert(err.response?.data?.detail || '创建失败')
  }
}

function handleEditResource(resource: Resource) {
  currentEditResource.value = resource
  editForm.value = {
    name: resource.name,
    description: resource.description || '',
    quantity: resource.quantity || 1
  }
  showEdit.value = true
}

async function handleUpdateResource() {
  if (!currentEditResource.value) return
  try {
    await updateResource(roomId, currentEditResource.value.id, {
      name: editForm.value.name,
      description: editForm.value.description,
      quantity: currentEditResource.value.is_container ? undefined : editForm.value.quantity
    })
    showEdit.value = false
    currentEditResource.value = null
    await loadData()
  } catch (err: any) {
    alert(err.response?.data?.detail || '更新失败')
  }
}

async function handleDeleteResource(resourceId: number) {
  if (!confirm('确定要删除吗？如果这是容器，需要先删除里面的所有内容。')) return
  try {
    await deleteResource(roomId, resourceId)
    await loadData()
  } catch (err: any) {
    alert(err.response?.data?.detail || '删除失败')
  }
}

function handleAddChild(resource: Resource) {
  parentResource.value = resource
  resourceForm.value.is_container = false
  showAddChild.value = true
}

function goBack() {
  router.push('/dashboard')
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
  loadData()
})
</script>

<style scoped>
.room-container {
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

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.btn-back {
  padding: 8px 16px;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-back:hover {
  background: #5a6268;
}

.header h1 {
  margin: 0;
  color: #333;
}

.room-code {
  color: #667eea;
  font-weight: 500;
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
}

.btn-logout:hover {
  background: #c82333;
}

.content {
  max-width: 1200px;
  margin: 40px auto;
  padding: 0 20px;
}

.toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
}

.btn-primary {
  padding: 10px 20px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-primary:hover {
  background: #5568d3;
}

.btn-success {
  padding: 10px 20px;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-success:hover {
  background: #218838;
}

.btn-secondary {
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-secondary:hover {
  background: #5a6268;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #999;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #999;
}

.empty-state p {
  margin-bottom: 20px;
}

.resource-tree {
  display: flex;
  flex-direction: column;
  gap: 20px;
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
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
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

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px;
  border: 2px solid #eee;
  border-radius: 4px;
  font-size: 14px;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #667eea;
}

.radio-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.radio-group label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.radio-group input[type="radio"] {
  width: auto;
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
