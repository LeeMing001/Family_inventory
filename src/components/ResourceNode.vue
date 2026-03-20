<template>
  <div class="resource-node" :class="{ 'container': resource.is_container, 'item': !resource.is_container }">
    <div class="resource-header">
      <div class="resource-info">
        <div class="resource-type">
          <span class="type-badge" :class="resource.is_container ? 'badge-container' : 'badge-item'">
            {{ resource.is_container ? '容器' : '物品' }}
          </span>
          <h3>{{ resource.name }}</h3>
        </div>
        <p v-if="resource.description" class="description">{{ resource.description }}</p>
        <div v-if="!resource.is_container && resource.quantity" class="quantity">
          数量: {{ resource.quantity }}
        </div>
      </div>
      <div class="resource-actions">
        <button v-if="resource.is_container" class="btn-sm btn-success" @click="$emit('add-child', resource)">
          + 添加
        </button>
        <button class="btn-sm btn-primary" @click="$emit('edit', resource)">
          编辑
        </button>
        <button class="btn-sm btn-danger" @click="$emit('delete', resource.id)">
          删除
        </button>
      </div>
    </div>

    <!-- 子资源 -->
    <div v-if="resource.is_container && resource.children.length > 0" class="children">
      <ResourceNode
        v-for="child in resource.children"
        :key="child.id"
        :resource="child"
        :room-id="roomId"
        @edit="$emit('edit', $event)"
        @delete="$emit('delete', $event)"
        @add-child="$emit('add-child', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ResourceWithChildren } from '@/api/inventory'

defineProps<{
  resource: ResourceWithChildren
  roomId: number
}>()

defineEmits<{
  edit: [resource: ResourceWithChildren]
  delete: [id: number]
  'add-child': [resource: ResourceWithChildren]
}>()
</script>

<style scoped>
.resource-node {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 10px;
  overflow: hidden;
}

.resource-node.container {
  border-left: 4px solid #667eea;
}

.resource-node.item {
  border-left: 4px solid #28a745;
}

.resource-header {
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
}

.resource-info {
  flex: 1;
}

.resource-type {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.type-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.badge-container {
  background: #e7eaff;
  color: #667eea;
}

.badge-item {
  background: #e8f5e9;
  color: #28a745;
}

.resource-info h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
}

.description {
  margin: 8px 0;
  color: #666;
  font-size: 14px;
}

.quantity {
  display: inline-block;
  margin-top: 8px;
  padding: 4px 12px;
  background: #fff3cd;
  color: #856404;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.resource-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover {
  background: #5568d3;
}

.btn-success {
  background: #28a745;
  color: white;
}

.btn-success:hover {
  background: #218838;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-danger:hover {
  background: #c82333;
}

.children {
  padding: 0 20px 20px 20px;
  background: #f8f9fa;
  border-top: 1px solid #eee;
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 10px;
}
</style>
