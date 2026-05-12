<template>
  <el-container class="layout-container">
    <el-aside :width="globalStore.isCollapse ? '64px' : '210px'" class="layout-aside">
      <div class="logo-wrap">
        <img src="@/assets/images/logo.svg" alt="logo" class="logo-img" />
        <span v-show="!globalStore.isCollapse" class="logo-text">算网大脑</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        :collapse="globalStore.isCollapse"
        :collapse-transition="false"
        router
        background-color="#001529"
        text-color="#ffffffa6"
        active-text-color="#ffffff"
      >
        <template v-for="item in menuList" :key="item.path">
          <el-menu-item :index="item.path" v-if="!item.meta?.isHide">
            <el-icon><component :is="item.meta?.icon" /></el-icon>
            <template #title>{{ item.meta?.title }}</template>
          </el-menu-item>
        </template>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="layout-header">
        <div class="header-left">
          <el-icon class="collapse-icon" @click="globalStore.setCollapse(!globalStore.isCollapse)">
            <Fold v-if="!globalStore.isCollapse" />
            <Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>{{ currentRoute?.meta?.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-dropdown>
            <span class="user-info">
              <el-avatar :size="28">{{ userStore.username?.charAt(0) || "U" }}</el-avatar>
              <span class="username">{{ userStore.username || "用户" }}</span>
              <el-tag v-if="userStore.isAdmin" type="danger" size="small">管理员</el-tag>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from "vue"
import { useRoute, useRouter } from "vue-router"
import { useGlobalStore } from "@/store/modules/global"
import { useUserStore } from "@/store/modules/user"
import staticRouter from "@/router"

const route = useRoute()
const router = useRouter()
const globalStore = useGlobalStore()
const userStore = useUserStore()

const activeMenu = computed(() => route.meta.activeMenu as string || route.path)
const currentRoute = computed(() => route)

const menuList = computed(() => {
  const layoutRoute = staticRouter.options.routes.find(r => r.name === "layout")
  if (!layoutRoute?.children) return []
  return layoutRoute.children.filter(item => {
    if (item.meta?.isHide) return false
    if (item.meta?.roles && !item.meta.roles.includes(userStore.role)) return false
    return true
  })
})

function handleLogout() {
  userStore.logout()
  router.replace("/login")
}
</script>

<style scoped lang="scss">
.layout-container {
  height: 100vh;
}
.layout-aside {
  background-color: #001529;
  transition: width 0.3s;
  overflow: hidden;
  .logo-wrap {
    height: 55px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    border-bottom: 1px solid #ffffff1a;
    .logo-img { width: 32px; height: 32px; }
    .logo-text { color: #fff; font-size: 18px; font-weight: bold; white-space: nowrap; }
  }
  .el-menu { border-right: none; }
}
.layout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #eee;
  padding: 0 20px;
  height: 55px;
  .header-left { display: flex; align-items: center; gap: 12px; }
  .collapse-icon { font-size: 20px; cursor: pointer; }
  .header-right { display: flex; align-items: center; gap: 16px; }
  .header-icon { font-size: 20px; cursor: pointer; }
  .user-info { display: flex; align-items: center; gap: 8px; cursor: pointer; }
  .username { font-size: 14px; }
}
.layout-main {
  background-color: #f5f7fa;
  padding: 16px;
}
</style>
