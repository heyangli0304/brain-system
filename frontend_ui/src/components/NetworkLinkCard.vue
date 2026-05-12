<template>
  <div class="network-link-card">
    <div class="link-header">
      <el-icon><Connection /></el-icon>
      <span>光网链路信息</span>
    </div>
    <div class="link-body">
      <div class="link-path">
        <span class="node" v-for="(node, idx) in nodes" :key="idx">
          {{ node }}
          <el-icon v-if="idx < nodes.length - 1" class="arrow"><Right /></el-icon>
        </span>
      </div>
      <div class="link-detail">
        <span>带宽: {{ bandwidth }}</span>
        <span>时延: {{ latency }}</span>
        <el-tag :type="linkStatus === "active" ? "success" : "info"" size="small">
          {{ linkStatus === "active" ? "活跃" : "已断开" }}
        </el-tag>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  nodes: string[]
  bandwidth: string
  latency: string
  linkStatus: "active" | "inactive"
}>()
</script>

<style scoped lang="scss">
.network-link-card {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #e4e7ed;
  .link-header {
    display: flex; align-items: center; gap: 6px;
    font-weight: 600; margin-bottom: 12px;
    color: #409eff;
  }
  .link-path {
    display: flex; align-items: center; gap: 4px;
    margin-bottom: 8px;
    .node { display: flex; align-items: center; font-weight: 500; }
    .arrow { color: #409eff; }
  }
  .link-detail {
    display: flex; gap: 16px; font-size: 13px; color: #666;
  }
}
</style>
