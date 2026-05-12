<template>
  <div class="resource-card">
    <div class="card-header">
      <span class="card-title">{{ title }}</span>
      <el-tag :type="statusType" size="small">{{ statusText }}</el-tag>
    </div>
    <div class="card-body">
      <div class="stat-item" v-for="item in stats" :key="item.label">
        <span class="stat-label">{{ item.label }}</span>
        <span class="stat-value" :style="{ color: item.color || '#333' }">{{ item.value }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue"
const props = defineProps<{
  title: string
  stats: { label: string; value: string | number; color?: string }[]
  status?: "online" | "offline" | "warning"
}>()
const statusType = computed(() => {
  if (props.status === "online") return "success"
  if (props.status === "warning") return "warning"
  if (props.status === "offline") return "danger"
  return "info"
})
const statusText = computed(() => {
  if (props.status === "online") return "在线"
  if (props.status === "warning") return "告警"
  if (props.status === "offline") return "离线"
  return "未知"
})
</script>

<style scoped lang="scss">
.resource-card {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    .card-title { font-size: 16px; font-weight: 600; }
  }
  .card-body {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
    .stat-item {
      display: flex;
      flex-direction: column;
      .stat-label { font-size: 12px; color: #999; }
      .stat-value { font-size: 20px; font-weight: bold; }
    }
  }
}
</style>
