import api from './index'

export interface Resource {
  id: number
  name: string
  description: string | null
  quantity: number | null
  is_container: boolean
  room_id: number
  parent_id: number | null
  created_at: string
  updated_at: string
}

export interface ResourceWithChildren extends Resource {
  children: ResourceWithChildren[]
}

// 创建资源
export async function createResource(
  roomId: number,
  data: {
    name: string
    description?: string
    quantity?: number
    is_container: boolean
    parent_id?: number
  }
) {
  const response = await api.post<Resource>(`/api/rooms/${roomId}/resources`, data)
  return response.data
}

// 获取资源列表
export async function getResources(roomId: number, parentId?: number, isContainer?: boolean) {
  const params = new URLSearchParams()
  if (parentId !== undefined) params.append('parent_id', parentId.toString())
  if (isContainer !== undefined) params.append('is_container', isContainer.toString())
  
  const url = `/api/rooms/${roomId}/resources${params.toString() ? '?' + params.toString() : ''}`
  const response = await api.get<Resource[]>(url)
  return response.data
}

// 获取资源树（带层级关系）
export async function getResourceTree(roomId: number) {
  const response = await api.get<ResourceWithChildren[]>(`/api/rooms/${roomId}/resources/tree`)
  return response.data
}

// 获取单个资源详情
export async function getResource(roomId: number, resourceId: number) {
  const response = await api.get<Resource>(`/api/rooms/${roomId}/resources/${resourceId}`)
  return response.data
}

// 更新资源
export async function updateResource(
  roomId: number,
  resourceId: number,
  data: {
    name?: string
    description?: string
    quantity?: number
    is_container?: boolean
  }
) {
  const response = await api.put<Resource>(`/api/rooms/${roomId}/resources/${resourceId}`, data)
  return response.data
}

// 删除资源
export async function deleteResource(roomId: number, resourceId: number) {
  const response = await api.delete(`/api/rooms/${roomId}/resources/${resourceId}`)
  return response.data
}

// 获取资源的子资源
export async function getResourceChildren(roomId: number, resourceId: number) {
  const response = await api.get<Resource[]>(`/api/rooms/${roomId}/resources/${resourceId}/children`)
  return response.data
}
