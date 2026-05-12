<template>
  <div class="datascreen-page">
    <div class="screen-header">
      <div class="header-left">
        <span class="back-btn" @click="router.replace('/')">← 返回</span>
      </div>
      <div class="header-center">
        <h1>算网大脑可视化大屏</h1>
        <span class="time">{{ currentTime }}</span>
      </div>
      <div class="header-right">
        <span>算网资源实时监控</span>
      </div>
    </div>
    <div class="screen-body">
      <div class="screen-left">
        <div class="screen-panel">
          <div class="panel-title">集群资源概览</div>
          <div ref="clusterChartRef" class="panel-chart"></div>
        </div>
        <div class="screen-panel">
          <div class="panel-title">GPU使用率</div>
          <div ref="gpuChartRef" class="panel-chart"></div>
        </div>
      </div>
      <div class="screen-center">
        <div class="screen-panel" style="flex: 1">
          <div class="panel-title">全网拓扑</div>
          <TopologyChart :nodes="topoNodes" :links="topoLinks" style="height: 100%" />
        </div>
      </div>
      <div class="screen-right">
        <div class="screen-panel">
          <div class="panel-title">任务状态统计</div>
          <div ref="taskChartRef" class="panel-chart"></div>
        </div>
        <div class="screen-panel">
          <div class="panel-title">性能监控</div>
          <div ref="perfChartRef" class="panel-chart"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue"
import { useRouter } from "vue-router"
import * as echarts from "echarts"
import TopologyChart from "@/components/TopologyChart.vue"
import { getSimplifiedTopology } from "@/api/modules/network"
import { getClusterResource, getJobMetrics } from "@/api/modules/resource"
import { getTaskList } from "@/api/modules/task"

const router = useRouter()
const currentTime = ref(new Date().toLocaleString())
let timer: any = null
let dataTimer: any = null

const clusterChartRef = ref<HTMLDivElement>()
const gpuChartRef = ref<HTMLDivElement>()
const taskChartRef = ref<HTMLDivElement>()
const perfChartRef = ref<HTMLDivElement>()
let charts: echarts.ECharts[] = []

const topoNodes = ref<any[]>([])
const topoLinks = ref<any[]>([])

async function loadTopology() {
  try {
    const res: any = await getSimplifiedTopology()
    if (res?.code === 0 && res?.data) {
      const { nodes, links } = res.data
      
      // 创建节点 ID 到名称的映射
      const nodeMap = new Map<string, string>()
      nodes.forEach((n: any) => {
        nodeMap.set(n["node-id"], n.label || n.name)
      })
      
      topoNodes.value = nodes.map((n: any) => ({
        name: n.label || n.name,
        category: 0,
        symbolSize: 60,
        nodeId: n["node-id"]
      }))
      topoLinks.value = links.map((l: any) => ({
        source: nodeMap.get(l["source-node"]) || l["source-node"],
        target: nodeMap.get(l["dest-node"]) || l["dest-node"]
      }))
    }
  } catch (error: any) {
    console.error("加载拓扑失败:", error)
  }
}

async function loadClusterResource() {
  try {
    const res: any = await getClusterResource()
    if (res?.respCode === 0 && res?.respBody?.data) {
      const clusters = res.respBody.data
      // 解析集群资源数据，更新图表
      const clusterData = clusters.map((c: any) => ({
        name: c.cluster_name.replace(/-DC.*/, '-DC'), // 简化名称
        value: c.total_card || 0
      }))
      
      charts[0]?.setOption({
        tooltip: {},
        series: [{
          type: "pie",
          radius: ["35%", "60%"],
          data: clusterData,
          label: {
            formatter: '{b}: {c}卡'
          }
        }]
      })
    }
  } catch (error: any) {
    console.error("加载集群资源失败:", error)
  }
}

async function loadTaskStats() {
  try {
    const res: any = await getTaskList()
    // 统计任务状态
    const stats = { running: 0, pending: 0, completed: 0, failed: 0 }
    
    if (res?.data) {
      res.data.forEach((tunnel: any) => {
        const state = tunnel["provisioning-state"] || "unknown"
        if (state === "installed") stats.running++
        else if (state === "installing") stats.pending++
        else if (state === "failed") stats.failed++
        else stats.completed++
      })
    }
    
    charts[2]?.setOption({
      tooltip: {},
      xAxis: { type: "category", data: ["运行中", "等待中", "已完成", "失败"] },
      yAxis: { type: "value" },
      series: [{
        type: "bar",
        data: [stats.running, stats.pending, stats.completed, stats.failed],
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#83bff6' },
            { offset: 1, color: '#188df0' }
          ])
        }
      }]
    })
  } catch (error: any) {
    console.error("加载任务统计失败:", error)
  }
}

async function loadGPUMetrics() {
  try {
    // 获取作业 GPU 使用率指标
    const res: any = await getJobMetrics(1, "ShaoGuan-DC-A", "gpu_utilization")
    let gpuUsage = 65 // 默认值
    
    if (res?.respCode === 0 && res?.respBody?.metrics) {
      const gpuMetric = res.respBody.metrics.find((m: any) => m.metric_types === "gpu_utilization")
      if (gpuMetric) {
        gpuUsage = gpuMetric.value_current || 65
      }
    }
    
    charts[1]?.setOption({
      tooltip: { formatter: '{a}: {b}%' },
      series: [{
        type: "gauge",
        radius: '70%',
        detail: { formatter: '{value}%' },
        data: [{ value: gpuUsage, name: '平均 GPU 使用率' }],
        axisLine: {
          lineStyle: {
            width: 10,
            color: [
              [0.3, '#67e0e3'],
              [0.7, '#37a2da'],
              [1, '#fd666d']
            ]
          }
        }
      }]
    })
  } catch (error: any) {
    console.error("加载 GPU 指标失败:", error)
  }
}

async function loadPerfMetrics() {
  try {
    // 获取作业 TTFT 指标
    const res: any = await getJobMetrics(1, "ShaoGuan-DC-A", "infer_ttft")
    let ttftData = [120, 115, 130, 125, 140, 118] // 默认值
    
    if (res?.respCode === 0 && res?.respBody?.metrics) {
      const ttftMetric = res.respBody.metrics.find((m: any) => m.metric_types === "infer_ttft")
      if (ttftMetric) {
        // 模拟 6 个时间点的数据（实际应该从后端获取历史数据）
        const baseValue = ttftMetric.value_current || 120
        ttftData = [
          baseValue - 10,
          baseValue - 5,
          baseValue + 10,
          baseValue + 5,
          baseValue + 20,
          baseValue - 2
        ]
      }
    }
    
    charts[3]?.setOption({
      tooltip: { trigger: "axis" },
      xAxis: { type: "category", data: ["00:00", "04:00", "08:00", "12:00", "16:00", "20:00"] },
      yAxis: { type: "value", name: "TTFT(ms)" },
      series: [{
        type: "line",
        data: ttftData,
        smooth: true,
        areaStyle: { opacity: 0.3 },
        itemStyle: { color: '#409EFF' }
      }]
    })
  } catch (error: any) {
    console.error("加载性能指标失败:", error)
  }
}

async function refreshAllData() {
  loadClusterResource()
  loadGPUMetrics()
  loadTaskStats()
  loadPerfMetrics()
}

onMounted(() => {
  timer = setInterval(() => { currentTime.value = new Date().toLocaleString() }, 1000)
  loadTopology()
  
  const refs = [clusterChartRef, gpuChartRef, taskChartRef, perfChartRef]
  refs.forEach(r => {
    if (r.value) {
      const c = echarts.init(r.value)
      charts.push(c)
    }
  })
  
  // 初始化图表
  refreshAllData()
  
  // 每 10 秒刷新一次数据
  dataTimer = setInterval(refreshAllData, 10000)
})

onUnmounted(() => {
  clearInterval(timer)
  clearInterval(dataTimer)
  charts.forEach(c => c.dispose())
})
</script>

<style scoped lang="scss">
.datascreen-page {
  height: 100vh; background: #0a1628; color: #fff; display: flex; flex-direction: column; overflow: hidden;
}
.screen-header {
  height: 60px; display: flex; align-items: center; justify-content: space-between; padding: 0 24px;
  background: linear-gradient(180deg, #0f2a4a 0%, #0a1628 100%); border-bottom: 1px solid #1a3a5c;
  .header-center { text-align: center; h1 { font-size: 22px; margin: 0; background: linear-gradient(90deg, #4facfe, #00f2fe); -webkit-background-clip: text; -webkit-text-fill-color: transparent; } .time { font-size: 12px; color: #8899aa; } }
  .back-btn { cursor: pointer; color: #4facfe; }
}
.screen-body {
  flex: 1; display: flex; gap: 12px; padding: 12px;
  .screen-left, .screen-right { width: 28%; display: flex; flex-direction: column; gap: 12px; }
  .screen-center { flex: 1; display: flex; flex-direction: column; }
}
.screen-panel {
  background: #0f2a4a; border-radius: 8px; padding: 12px; border: 1px solid #1a3a5c; flex: 1;
  .panel-title { font-size: 14px; color: #4facfe; margin-bottom: 8px; padding-left: 8px; border-left: 3px solid #4facfe; }
  .panel-chart { height: calc(100% - 30px); }
}
</style>
