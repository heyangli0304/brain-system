<template>
  <div class="system-user-page">
    <div class="page-header"><h2>用户管理</h2></div>
    <el-card>
      <el-table :data="userList" stripe>
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="role" label="角色">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'info'">{{ row.role === 'admin' ? '管理员' : '普通用户' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">{{ row.status === 'active' ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lastLogin" label="最后登录" />
        <el-table-column label="操作" width="200">
          <template #default>
            <el-button link type="primary">编辑</el-button>
            <el-button link type="danger">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue"
const userList = ref([
  { username: "admin", role: "admin", status: "active", lastLogin: "2026-04-28 10:00" },
  { username: "user01", role: "user", status: "active", lastLogin: "2026-04-27 15:30" },
  { username: "user02", role: "user", status: "inactive", lastLogin: "2026-04-20 09:00" }
])
</script>

<style scoped lang="scss">
.system-user-page { .page-header { margin-bottom: 16px; } }
</style>
