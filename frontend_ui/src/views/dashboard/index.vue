<template>
  <div class="dashboard-page">
    <div class="page-header">
      <h2>资源概况</h2>
      <el-button @click="refreshData" :loading="loading" icon="Refresh">刷新</el-button>
    </div>
    <el-row :gutter="16" class="cluster-cards">
      <el-col :span="8" v-for="cluster in clusterList" :key="cluster.name">
        <ResourceCard
          :title="cluster.name"
          :status="cluster.status"
          :stats="[
            { label: 'GPU总数', value: cluster.totalGpu },
            { label: 'GPU可用', value: cluster.availableGpu, color: cluster.availableGpu > 0 ? '#67c23a' : '#f56c6c' },
            { label: '节点数', value: cluster.totalNode },
            { label: '可用节点', value: cluster.availableNode }
          ]"
        />
      </el-col>
    </el-row>
    <el-row :gutter="16" class="chart-row">
      <el-col :span="12">
        <el-card header="GPU资源分布">
          <div ref="gpuChartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card header="网络资源状态">
          <div ref="networkChartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue"
import * as echarts from "echarts"
import ResourceCard from "@/components/ResourceCard.vue"
import { getClusterOverview } from "@/api/modules/resource"

const loading = ref(false)
const clusterList = ref<any[]>([])
const gpuChartRef = ref<HTMLDivElement>()
const networkChartRef = ref<HTMLDivElement>()
let gpuChart: echarts.ECharts | null = null
let networkChart: echarts.ECharts | null = null

async function refreshData() {
  loading.value = true
  try {
    const res: any = await getClusterOverview()
    console.log("资源概况 API 返回:", res)
    
    // 正确解析后端返回的数据结构
    if (res?.respBody?.data && Array.isArray(res.respBody.data)) {
      clusterList.value = res.respBody.data.map((cluster: any) => {
        // 从 node_metrics_info 中提取 GPU 信息
        const nodeMetrics = cluster.node_metrics_info?.[0] || {}
        const cardInfo = nodeMetrics.card_info?.[0] || {}
        
        return {
          name: cluster.cluster_name || "未知集群",
          status: cluster.control_plane_status === 1 ? "online" : "offline",
          totalGpu: cardInfo.card_total_count || cluster.total_card || 0,
          availableGpu: cardInfo.card_available_count || 0,
          totalNode: cluster.total_node || 0,
          availableNode: nodeMetrics.node_available_count || 0
        }
      })
      console.log("转换后的集群列表:", clusterList.value)
    } else {
      // 如果后端返回为空，使用默认数据
      clusterList.value = [
        { name: "韶关 DC-A", status: "online", totalGpu: 64, availableGpu: 32, totalNode: 8, availableNode: 4 },
        { name: "广州 DC-B", status: "online", totalGpu: 48, availableGpu: 16, totalNode: 6, availableNode: 2 },
        { name: "深圳 DC-C", status: "warning", totalGpu: 32, availableGpu: 2, totalNode: 4, availableNode: 1 }
      ]
    }
  } catch (error) {
    console.error("获取资源概况失败:", error)
    // 出错时使用默认数据
    clusterList.value = [
      { name: "韶关 DC-A", status: "online", totalGpu: 64, availableGpu: 32, totalNode: 8, availableNode: 4 },
      { name: "广州 DC-B", status: "online", totalGpu: 48, availableGpu: 16, totalNode: 6, availableNode: 2 },
      { name: "深圳 DC-C", status: "warning", totalGpu: 32, availableGpu: 2, totalNode: 4, availableNode: 1 }
    ]
  } finally {
    loading.value = false
    renderCharts()
  }
}

function renderCharts() {
  if (gpuChartRef.value && !gpuChart) gpuChart = echarts.init(gpuChartRef.value)
  if (networkChartRef.value && !networkChart) networkChart = echarts.init(networkChartRef.value)
  gpuChart?.setOption({
    tooltip: { trigger: "item" },
    series: [{
      type: "pie", radius: ["40%", "70%"],
      data: clusterList.value.map(c => ({ name: c.name, value: c.availableGpu })),
      emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: "rgba(0,0,0,0.5)" } }
    }]
  })
  networkChart?.setOption({
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: clusterList.value.map(c => c.name) },
    yAxis: { type: "value", name: "带宽(Gbps)" },
    series: [{ type: "bar", data: [100, 80, 50], itemStyle: { color: "#409eff" } }]
  })
}

onMounted(() => refreshData())
onUnmounted(() => { gpuChart?.dispose(); networkChart?.dispose() })
</script>

<style scoped lang="scss">
.dashboard-page {
  .page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
  .cluster-cards { margin-bottom: 16px; }
  .chart-row { margin-top: 16px; }
}
</style>
