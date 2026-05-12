<template>
  <div class="topology-page">
    <div class="page-header">
      <h2>网络拓扑</h2>
      <el-button @click="refreshTopology" :loading="loading" icon="Refresh">刷新</el-button>
    </div>
    <el-card>
      <TopologyChart :nodes="topoNodes" :links="topoLinks" style="height: 500px" />
    </el-card>
    <el-row :gutter="16" style="margin-top: 16px">
      <el-col :span="24">
        <el-card header="光网链路列表">
          <el-table :data="linkList" stripe>
            <el-table-column prop="source" label="源节点" />
            <el-table-column prop="target" label="目的节点" />
            <el-table-column prop="bandwidth" label="带宽" />
            <el-table-column prop="latency" label="时延" />
            <el-table-column prop="status" label="状态">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : 'info'" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue"
import { ElMessage } from "element-plus"
import TopologyChart from "@/components/TopologyChart.vue"
import { getSimplifiedTopology } from "@/api/modules/network"

const loading = ref(false)
const topoNodes = ref<any[]>([])
const topoLinks = ref<any[]>([])
const linkList = ref<any[]>([])

// 节点映射（从后端动态获取）
const nodeMap = ref<Map<string, string>>(new Map())

// 从后端获取拓扑，构建节点映射
async function fetchNodeMap() {
  try {
    const res: any = await getNetworkTopology()
    console.log("拓扑页面 - 后端返回的拓扑数据:", res)
    
    if (res?.data?.networks?.[0]?.node) {
      const nodes = res.data.networks[0].node
      nodeMap.value = nodes.reduce((map: Map<string, string>, node: any) => {
        const nodeId = node["node-id"] || node["ietf-te-topology:te-node-id"]
        // 优先使用 label（如：韶关数据中心 1 号），其次使用 name（如：ShaoGuan-DC-1）
        const nodeName = node["label"] || node["name"] || nodeId
        map.set(nodeId, nodeName)
        return map
      }, new Map<string, string>())
      console.log("节点映射:", nodeMap.value)
      
      if (nodeMap.value.size === 0) {
        throw new Error("节点映射为空")
      }
    } else {
      throw new Error("返回数据格式不正确")
    }
  } catch (error: any) {
    console.error("获取拓扑失败:", error)
    // 如果获取失败，使用默认映射（降级方案）
    ElMessage.warning("获取节点映射失败，使用默认配置")
    
    // 默认节点映射（与后端 topology.py 保持一致）
    nodeMap.value = new Map<string, string>([
      ["10.10.10.1", "ShaoGuan-DC-1"],
      ["10.10.10.2", "ShaoGuan-DC-2"],
      ["10.10.10.3", "GuangZhou-DC-1"],
      ["10.10.10.4", "GuangZhou-DC-2"],
      ["10.10.10.5", "ShenZhen-DC-1"],
      ["10.10.10.6", "ShenZhen-DC-2"],
      ["10.10.10.7", "DongGuan-DC-1"],
      ["10.10.10.8", "FoShan-DC-1"],
      ["10.10.10.9", "ZhuHai-DC-1"],
      ["10.10.10.10", "HuiZhou-DC-1"]
    ])
    console.log("使用默认节点映射:", nodeMap.value)
  }
}

async function refreshTopology() {
  loading.value = true
  try {
    const topoRes: any = await getSimplifiedTopology()
    if (topoRes?.code === 0 && topoRes?.data) {
      const { nodes, links } = topoRes.data
      
      topoNodes.value = nodes.map((n: any) => ({
        name: n.label || n.name,
        category: 0,
        symbolSize: 50,
        nodeId: n["node-id"]
      }))
      
      topoLinks.value = links.map((l: any) => ({
        source: nodeMap.value.get(l["source-node"]) || l["source-node"],
        target: nodeMap.value.get(l["dest-node"]) || l["dest-node"],
        bandwidth: l["max-bandwidth"],
        supportOdu: l["support-odu"]
      }))
      
      linkList.value = links.map((l: any, idx: number) => ({
        id: l["link-id"],
        source: nodeMap.value.get(l["source-node"]) || l["source-node"],
        target: nodeMap.value.get(l["dest-node"]) || l["dest-node"],
        bandwidth: formatBandwidth(l["max-bandwidth"]),
        latency: "1.2ms",
        status: "active",
        supportOdu: l["support-odu"]
      }))
    }
  } catch (error: any) {
    console.error("获取拓扑失败:", error)
    ElMessage.error("获取拓扑失败：" + error.message)
  } finally {
    loading.value = false
  }
}

function formatBandwidth(bw: string): string {
  if (!bw) return "100G"
  const bwNum = parseInt(bw)
  if (bwNum >= 1000000) {
    return "1Tbps"
  } else if (bwNum >= 400000) {
    return "400Gbps"
  } else {
    return Math.round(bwNum / 1000) + "Gbps"
  }
}

onMounted(() => {
  // 先获取节点映射，再获取拓扑
  fetchNodeMap().then(() => {
    refreshTopology()
  }).catch(() => {
    refreshTopology()
  })
})
</script>

<style scoped lang="scss">
.topology-page {
  .page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
}
</style>
