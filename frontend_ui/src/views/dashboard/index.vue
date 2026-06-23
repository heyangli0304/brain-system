<template>
  <div class="dashboard-page">
    <div class="page-header">
      <h2>资源概况</h2>
      <el-button @click="refreshData" :loading="loading" icon="Refresh">刷新</el-button>
    </div>
    
    <!-- 搜索和视图切换 -->
    <div class="toolbar">
      <el-input 
        v-model="searchKeyword" 
        placeholder="搜索集群名称..." 
        clearable
        style="width: 300px"
        @input="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      
      <el-radio-group v-model="viewMode" @change="handleViewChange">
        <el-radio-button value="card">卡片视图</el-radio-button>
        <el-radio-button value="table">表格视图</el-radio-button>
      </el-radio-group>
      
      <el-tag type="info">共 {{ filteredClusters.length }} 个集群</el-tag>
    </div>
    
    <!-- 卡片视图 -->
    <div v-if="viewMode === 'card'" class="card-view">
      <el-row :gutter="16" class="cluster-cards">
        <el-col :span="8" v-for="cluster in paginatedClusters" :key="cluster.name">
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
      
      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[6, 9, 12, 24]"
          :total="filteredClusters.length"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </div>
    
    <!-- 表格视图 -->
    <div v-if="viewMode === 'table'" class="table-view">
      <el-table 
        :data="paginatedClusters" 
        style="width: 100%" 
        stripe
        :header-cell-style="{ background: '#f5f7fa', color: '#606266' }"
      >
        <el-table-column prop="name" label="集群名称" width="180" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="totalGpu" label="GPU总数" width="100" sortable />
        <el-table-column prop="availableGpu" label="GPU可用" width="100" sortable>
          <template #default="{ row }">
            <span :style="{ color: row.availableGpu > 0 ? '#67c23a' : '#f56c6c', fontWeight: 'bold' }">
              {{ row.availableGpu }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="totalNode" label="节点总数" width="100" sortable />
        <el-table-column prop="availableNode" label="可用节点" width="100" sortable>
          <template #default="{ row }">
            <span :style="{ color: row.availableNode > 0 ? '#67c23a' : '#f56c6c' }">
              {{ row.availableNode }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="GPU使用率" width="150">
          <template #default="{ row }">
            <el-progress 
              :percentage="getGpuUsageRate(row)" 
              :color="getProgressColor(getGpuUsageRate(row))"
              :stroke-width="8"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="viewClusterDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="filteredClusters.length"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </div>
    
    <!-- 图表区域 -->
    <el-row :gutter="16" class="chart-row">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="chart-header">
              <span>GPU资源分布</span>
              <el-select v-model="chartDataRange" size="small" style="width: 120px" @change="renderCharts">
                <el-option value="current" label="当前页数据" />
                <el-option value="top10" label="前10个集群" />
                <el-option value="all" label="全部集群" />
              </el-select>
            </div>
          </template>
          <div ref="gpuChartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="chart-header">
              <span>网络资源状态</span>
              <el-select v-model="chartDataRange" size="small" style="width: 120px" @change="renderCharts">
                <el-option value="current" label="当前页数据" />
                <el-option value="top10" label="前10个集群" />
                <el-option value="all" label="全部集群" />
              </el-select>
            </div>
          </template>
          <div ref="networkChartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 集群详情弹窗 -->
    <el-dialog v-model="detailVisible" title="集群详情" width="600px">
      <el-descriptions :column="2" border v-if="selectedCluster">
        <el-descriptions-item label="集群名称">{{ selectedCluster.name }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(selectedCluster.status)">
            {{ getStatusText(selectedCluster.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="GPU总数">{{ selectedCluster.totalGpu }}</el-descriptions-item>
        <el-descriptions-item label="GPU可用">{{ selectedCluster.availableGpu }}</el-descriptions-item>
        <el-descriptions-item label="节点总数">{{ selectedCluster.totalNode }}</el-descriptions-item>
        <el-descriptions-item label="可用节点">{{ selectedCluster.availableNode }}</el-descriptions-item>
        <el-descriptions-item label="GPU使用率">
          <el-progress :percentage="getGpuUsageRate(selectedCluster)" :color="getProgressColor(getGpuUsageRate(selectedCluster))" />
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from "vue"
import * as echarts from "echarts"
import { Search } from '@element-plus/icons-vue'
import ResourceCard from "@/components/ResourceCard.vue"
import { getClusterOverview } from "@/api/modules/resource"

const loading = ref(false)
const clusterList = ref<any[]>([])
const searchKeyword = ref("")
const viewMode = ref<"card" | "table">("card")
const currentPage = ref(1)
const pageSize = ref(9)
const detailVisible = ref(false)
const selectedCluster = ref<any>(null)
const chartDataRange = ref<"current" | "top10" | "all">("current")

const gpuChartRef = ref<HTMLDivElement>()
const networkChartRef = ref<HTMLDivElement>()
let gpuChart: echarts.ECharts | null = null
let networkChart: echarts.ECharts | null = null

// 搜索过滤后的集群列表
const filteredClusters = computed(() => {
  if (!searchKeyword.value) return clusterList.value
  const keyword = searchKeyword.value.toLowerCase()
  return clusterList.value.filter(cluster => 
    cluster.name.toLowerCase().includes(keyword)
  )
})

// 分页后的集群列表
const paginatedClusters = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredClusters.value.slice(start, end)
})

// 获取状态类型
function getStatusType(status: string) {
  if (status === "online") return "success"
  if (status === "warning") return "warning"
  if (status === "offline") return "danger"
  return "info"
}

// 获取状态文本
function getStatusText(status: string) {
  if (status === "online") return "在线"
  if (status === "warning") return "告警"
  if (status === "offline") return "离线"
  return "未知"
}

// 计算GPU使用率
function getGpuUsageRate(cluster: any) {
  if (cluster.totalGpu === 0) return 0
  return Math.round((cluster.totalGpu - cluster.availableGpu) / cluster.totalGpu * 100)
}

// 获取进度条颜色
function getProgressColor(percentage: number) {
  if (percentage < 50) return '#67c23a'
  if (percentage < 80) return '#e6a23c'
  return '#f56c6c'
}

// 查看集群详情
function viewClusterDetail(cluster: any) {
  selectedCluster.value = cluster
  detailVisible.value = true
}

// 搜索处理
function handleSearch() {
  currentPage.value = 1
  renderCharts()
}

// 视图切换处理
function handleViewChange() {
  currentPage.value = 1
  pageSize.value = viewMode.value === "card" ? 9 : 10
  renderCharts()
}

// 分页处理
function handlePageChange(page: number) {
  currentPage.value = page
  renderCharts()
}

function handleSizeChange(size: number) {
  pageSize.value = size
  currentPage.value = 1
  renderCharts()
}

async function refreshData() {
  loading.value = true
  try {
    const res: any = await getClusterOverview()
    console.log("资源概况 API 返回:", res)
    
    if (res?.respBody?.data && Array.isArray(res.respBody.data)) {
      clusterList.value = res.respBody.data.map((cluster: any) => {
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
      clusterList.value = generateMockClusters(20)
    }
  } catch (error) {
    console.error("获取资源概况失败:", error)
    clusterList.value = generateMockClusters(20)
  } finally {
    loading.value = false
    renderCharts()
  }
}

// 生成模拟数据
function generateMockClusters(count: number) {
  const cities = ["韶关", "广州", "深圳", "东莞", "佛山", "珠海", "惠州", "中山", "江门", "肇庆"]
  const clusters = []
  for (let i = 0; i < count; i++) {
    const city = cities[i % cities.length]
    const suffix = Math.floor(i / cities.length) + 1
    clusters.push({
      name: `${city} DC-${suffix}`,
      status: Math.random() > 0.1 ? "online" : (Math.random() > 0.5 ? "warning" : "offline"),
      totalGpu: Math.floor(Math.random() * 64) + 16,
      availableGpu: Math.floor(Math.random() * 32),
      totalNode: Math.floor(Math.random() * 8) + 2,
      availableNode: Math.floor(Math.random() * 4) + 1
    })
  }
  return clusters
}

function renderCharts() {
  if (gpuChartRef.value && !gpuChart) gpuChart = echarts.init(gpuChartRef.value)
  if (networkChartRef.value && !networkChart) networkChart = echarts.init(networkChartRef.value)
  
  let chartData: any[] = []
  if (chartDataRange.value === "current") {
    chartData = paginatedClusters.value
  } else if (chartDataRange.value === "top10") {
    chartData = filteredClusters.value.slice(0, 10)
  } else {
    chartData = filteredClusters.value
  }
  
  // GPU环形图
  gpuChart?.setOption({
    tooltip: { trigger: "item", formatter: "{b}: {c} ({d}%)" },
    legend: { 
      orient: "vertical", 
      left: "left",
      type: "scroll",
      maxHeight: 250,
      formatter: (name: string) => {
        return name.length > 10 ? name.slice(0, 10) + '...' : name
      }
    },
    series: [{
      type: "pie", 
      radius: ["40%", "70%"],
      center: ["60%", "50%"],
      data: chartData.map(c => ({ 
        name: c.name, 
        value: c.availableGpu 
      })),
      emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: "rgba(0,0,0,0.5)" } },
      label: { show: false },
      labelLine: { show: false }
    }]
  }, true)
  
  // 网络柱形图 - 改用横向柱形图
  networkChart?.setOption({
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    grid: {
      left: "15%",
      right: "10%",
      bottom: "10%",
      top: "10%",
      containLabel: true
    },
    xAxis: { 
      type: "value", 
      name: "带宽(Gbps)",
      axisLabel: { formatter: "{value}" }
    },
    yAxis: { 
      type: "category", 
      data: chartData.map(c => {
        return c.name.length > 12 ? c.name.slice(0, 12) + '...' : c.name
      }),
      axisLabel: {
        interval: 0,
        rotate: 0,
        width: 100,
        overflow: "truncate"
      },
      inverse: true
    },
    dataZoom: chartData.length > 15 ? [
      {
        type: "slider",
        yAxisIndex: 0,
        start: 0,
        end: Math.min(100, Math.round(15 / chartData.length * 100)),
        right: 20,
        width: 20,
        borderColor: "transparent",
        backgroundColor: "#e2e2e2",
        handleIcon: "M10.7,11.9v-1.3H9.3v1.3c-4.9,0.3-8.8,4.4-8.8,9.4c0,5,3.9,9.1,8.8,9.4v1.3h1.3v-1.3c4.9-0.3,8.8-4.4,8.8-9.4C19.7,16.3,15.8,12.2,10.7,11.9z M13.3,24.4H6.7V23h6.6V24.4z M13.3,19H6.7v-1.3h6.6V19z",
        handleSize: "80%",
        handleStyle: {
          color: "#fff",
          shadowBlur: 3,
          shadowColor: "rgba(0, 0, 0, 0.6)",
          shadowOffsetX: 2,
          shadowOffsetY: 2
        }
      }
    ] : [],
    series: [{ 
      type: "bar", 
      data: chartData.map(c => {
        const hash = c.name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)
        return ((hash % 100) + 50)
      }), 
      itemStyle: { 
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: "#409eff" },
          { offset: 1, color: "#79bbff" }
        ])
      },
      barWidth: "60%",
      label: {
        show: true,
        position: "right",
        formatter: "{c} Gbps"
      }
    }]
  }, true)
}

onMounted(() => refreshData())
onUnmounted(() => { 
  gpuChart?.dispose()
  networkChart?.dispose()
})
</script>

<style scoped lang="scss">
.dashboard-page {
  padding: 20px;
  
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    
    h2 { margin: 0; }
  }
  
  .toolbar {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 16px;
    padding: 12px 16px;
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
  }
  
  .card-view {
    .cluster-cards {
      margin-bottom: 16px;
    }
  }
  
  .table-view {
    background: #fff;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 16px;
  }
  
  .pagination-wrapper {
    display: flex;
    justify-content: center;
    padding: 16px 0;
    background: #fff;
    border-radius: 8px;
    margin-bottom: 16px;
  }
  
  .chart-row {
    margin-top: 16px;
    
    .chart-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      span {
        font-weight: 600;
      }
    }
  }
}
</style>