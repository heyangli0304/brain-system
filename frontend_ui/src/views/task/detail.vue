<template>
  <div class="task-detail-page">
    <el-page-header @back="router.back()" title="返回" content="任务详情" />
    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :span="16">
        <el-card header="基本信息">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="任务ID">{{ taskDetail.taskId }}</el-descriptions-item>
            <el-descriptions-item label="任务名称">{{ taskDetail.taskName }}</el-descriptions-item>
            <el-descriptions-item label="模型">{{ taskDetail.modelName }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="statusMap[taskDetail.status]">{{ taskDetail.status }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ taskDetail.createdAt }}</el-descriptions-item>
            <el-descriptions-item label="部署模式">P/D分离拉远</el-descriptions-item>
          </el-descriptions>
        </el-card>
        <el-card header="P/D 实例状态" style="margin-top: 16px">
          <div class="pd-list">
            <PdStatus v-if="taskDetail.pInstance" role="prefill" :name="taskDetail.pInstance.name" :cluster="taskDetail.pInstance.cluster" :status="taskDetail.pInstance.status" />
            <PdStatus v-if="taskDetail.dInstance" role="decode" :name="taskDetail.dInstance.name" :cluster="taskDetail.dInstance.cluster" :status="taskDetail.dInstance.status" />
            <PdStatus v-if="taskDetail.proxyInstance" role="proxy" :name="taskDetail.proxyInstance.name" :cluster="taskDetail.proxyInstance.cluster" :status="taskDetail.proxyInstance.status" />
          </div>
        </el-card>
        <el-card header="性能监控" style="margin-top: 16px">
          <div ref="metricsChartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card header="光网链路信息">
          <NetworkLinkCard
            v-if="taskDetail.networkLink"
            :nodes="taskDetail.networkLink.nodes"
            :bandwidth="taskDetail.networkLink.bandwidth"
            :latency="taskDetail.networkLink.latency"
            :link-status="taskDetail.networkLink.status"
          />
          <el-empty v-else description="暂无光网链路信息" />
        </el-card>
        <el-card header="调度决策" style="margin-top: 16px">
          <el-timeline>
            <el-timeline-item timestamp="步骤1" type="primary">建立光网链路 DC-A → DC-B</el-timeline-item>
            <el-timeline-item timestamp="步骤2" type="primary">在 DC-A 部署 P(Prefill) 实例</el-timeline-item>
            <el-timeline-item timestamp="步骤3" type="success">在 DC-B 部署 D(Decode) 实例</el-timeline-item>
            <el-timeline-item timestamp="步骤4" type="warning">在 DC-B 部署 Proxy 实例</el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue"
import { useRoute, useRouter } from "vue-router"
import * as echarts from "echarts"
import PdStatus from "@/components/PdStatus.vue"
import NetworkLinkCard from "@/components/NetworkLinkCard.vue"
import { getTaskDetail } from "@/api/modules/task"

const route = useRoute()
const router = useRouter()
const metricsChartRef = ref<HTMLDivElement>()
let metricsChart: echarts.ECharts | null = null
const statusMap: Record<string, string> = { PENDING: "warning", RUNNING: "success", COMPLETED: "info", FAILED: "danger" }

const taskDetail = ref<any>({
  taskId: route.params.id as string,
  taskName: "LLaMA3-PD 部署",
  modelName: "LLaMA3-70B",
  status: "RUNNING",
  createdAt: "2026-04-28 10:00",
  pInstance: { name: "P-llama3", cluster: "韶关 DC-A", status: "RUNNING" },
  dInstance: { name: "D-llama3", cluster: "广州 DC-B", status: "RUNNING" },
  proxyInstance: { name: "Proxy-llama3", cluster: "广州 DC-B", status: "RUNNING" },
  networkLink: { nodes: ["韶关 DC-A", "OTN 节点 1", "OTN 节点 2", "广州 DC-B"], bandwidth: "100Gbps", latency: "1.2ms", status: "active" }
})

// 从后端获取任务详情
async function fetchTaskDetail() {
  const tunnelName = route.params.id as string
  if (!tunnelName) return
  
  try {
    const res: any = await getTaskDetail(tunnelName)
    if (res?.data) {
      const tunnel = res.data
      taskDetail.value = {
        ...taskDetail.value,
        taskId: tunnel["tunnel-name"] || tunnelName,
        status: tunnel["provisioning-state"] === "up" ? "RUNNING" : "PENDING",
        networkLink: {
          nodes: tunnel.path || ["韶关 DC-A", "OTN 节点", "广州 DC-B"],
          bandwidth: tunnel.bandwidth || "100Gbps",
          latency: tunnel.latency || "1.2ms",
          status: tunnel["provisioning-state"] === "up" ? "active" : "down"
        }
      }
    }
  } catch (error: any) {
    console.error("获取任务详情失败:", error)
  }
}

onMounted(() => {
  fetchTaskDetail()
  if (metricsChartRef.value) {
    metricsChart = echarts.init(metricsChartRef.value)
    metricsChart.setOption({
      tooltip: { trigger: "axis" },
      xAxis: { type: "category", data: ["10:00", "10:05", "10:10", "10:15", "10:20"] },
      yAxis: [
        { type: "value", name: "TTFT(ms)" },
        { type: "value", name: "TPOT(ms)" }
      ],
      series: [
        { name: "TTFT", type: "line", data: [120, 150, 130, 140, 125], smooth: true },
        { name: "TPOT", type: "line", yAxisIndex: 1, data: [30, 35, 28, 32, 29], smooth: true }
      ]
    })
  }
})

onUnmounted(() => {
  if (metricsChart) metricsChart.dispose()
})
</script>

<style scoped lang="scss">
.task-detail-page {
  .pd-list { display: flex; flex-direction: column; gap: 12px; }
}
</style>
