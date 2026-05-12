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

const router = useRouter()

const title = computed(() => "服务器错误")
const desc = computed(() => "服务器开小差了，请稍后再试")
const imgSrc = computed(() => "https://via.placeholder.com/300x200?text=500")
</script>

<style scoped lang="scss">
.error-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  gap: 16px;
  color: #666;

  img {
    width: 300px;
  }
}
</style>
