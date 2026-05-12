<template>
  <div class="system-role-page">
    <div class="page-header"><h2>角色管理</h2></div>
    <el-card>
      <el-table :data="roleList" stripe>
        <el-table-column prop="name" label="角色名" />
        <el-table-column prop="desc" label="描述" />
        <el-table-column prop="permissions" label="权限">
          <template #default="{ row }">
            <el-tag v-for="p in row.permissions" :key="p" size="small" style="margin-right: 4px">{{ p }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue"
const roleList = ref([
  { name: "admin", desc: "系统管理员", permissions: ["全部功能", "用户管理", "系统配置"] },
  { name: "user", desc: "普通用户", permissions: ["资源查看", "任务提交", "推理使用"] }
])
</script>

<style scoped lang="scss">
.system-role-page { .page-header { margin-bottom: 16px; } }
</style>
