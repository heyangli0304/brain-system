<template>
  <div class="pd-status">
    <div class="pd-item" :class="`pd-${role}`">
      <div class="pd-icon">{{ role === "prefill" ? "P" : role === "decode" ? "D" : "Px" }}</div>
      <div class="pd-info">
        <span class="pd-name">{{ name }}</span>
        <span class="pd-cluster">{{ cluster }}</span>
        <el-tag :type="statusType" size="small">{{ status }}</el-tag>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue"
const props = defineProps<{
  role: "prefill" | "decode" | "proxy"
  name: string
  cluster: string
  status: "PENDING" | "RUNNING" | "FAILED" | "COMPLETED"
}>()
const statusType = computed(() => {
  if (props.status === "RUNNING") return "success"
  if (props.status === "PENDING") return "warning"
  if (props.status === "FAILED") return "danger"
  return "info"
})
</script>

<style scoped lang="scss">
.pd-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  border-radius: 8px;
  border: 1px solid #eee;
  .pd-icon {
    width: 40px; height: 40px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-weight: bold; font-size: 18px; color: #fff;
  }
  &.pd-prefill .pd-icon { background: #409eff; }
  &.pd-decode .pd-icon { background: #67c23a; }
  &.pd-proxy .pd-icon { background: #e6a23c; }
  .pd-info {
    display: flex; flex-direction: column; gap: 4px;
    .pd-name { font-weight: 600; }
    .pd-cluster { font-size: 12px; color: #999; }
  }
}
</style>
