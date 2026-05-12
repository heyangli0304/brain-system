<template>
  <div class="error-page">
    <img :src="imgSrc" alt="error" />
    <h2>{{ title }}</h2>
    <p>{{ desc }}</p>
    <el-button type="primary" @click="router.replace('/')">返回首页</el-button>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue"
import { useRouter } from "vue-router"
const props = defineProps<{ code: 403 | 404 | 500 }>()
const router = useRouter()
const config: Record<number, { title: string; desc: string }> = {
  403: { title: "无访问权限", desc: "您没有权限访问此页面，请联系管理员" },
  404: { title: "页面不存在", desc: "您访问的页面不存在" },
  500: { title: "服务器错误", desc: "服务器开小差了，请稍后再试" }
}
const title = computed(() => config[props.code].title)
const desc = computed(() => config[props.code].desc)
const imgSrc = computed(() => `https://via.placeholder.com/300x200?text=${props.code}`)
</script>

<style scoped>
.error-page {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  height: 100vh; gap: 16px; color: #666;
  img { width: 300px; }
}
</style>
