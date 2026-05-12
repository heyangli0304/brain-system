<template>
  <div class="task-page">
    <div class="page-header">
      <h2>任务列表</h2>
      <el-button type="primary" icon="Plus" @click="router.push('/deploy')">新建部署</el-button>
    </div>
    <el-alert
      title="模型说明"
      type="info"
      :closable="false"
      style="margin-bottom: 16px"
    >
      <div>当前使用模型：<strong>LLaMA3-70B</strong>（模型 ID: 1001，后端固定）</div>
      <div>GPU 类型：A100-80G（每个节点最多 8 张）</div>
    </el-alert>
    <el-card>
      <el-table :data="taskList" stripe style="width: 100%">
        <el-table-column prop="taskId" label="任务 ID" width="140" />
        <el-table-column prop="taskName" label="任务名称" min-width="200" />
        <el-table-column label="GPU 类型" width="100">
          <template #default="{ row }">
            <el-tag type="info" size="small">A100-80G</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Prefill 实例" width="150">
          <template #default="{ row }">
            <div style="display: flex; flex-direction: column; gap: 4px">
              <el-tag type="primary" size="small">{{ row.pInstance?.node || "-" }}</el-tag>
              <span style="font-size: 12px; color: #999">{{ row.pInstance?.cluster }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Decode 实例" width="150">
          <template #default="{ row }">
            <div style="display: flex; flex-direction: column; gap: 4px">
              <el-tag type="success" size="small">{{ row.dInstance?.node || "-" }}</el-tag>
              <span style="font-size: 12px; color: #999">{{ row.dInstance?.cluster }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="Proxy 实例" width="150">
          <template #default="{ row }">
            <div style="display: flex; flex-direction: column; gap: 4px">
              <el-tag type="warning" size="small">{{ row.proxyInstance?.node || "-" }}</el-tag>
              <span style="font-size: 12px; color: #999">{{ row.proxyInstance?.cluster }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusMap[row.status] || 'info'" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="170" />
        <el-table-column label="操作" fixed="right" width="160">
          <template #default="{ row }">
            <el-button link type="primary" @click="showKvCache(row)">KVCache</el-button>
            <el-button link type="danger" v-if="row.status === 'RUNNING'" @click="handleCancel(row)">取消</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- KVCache 传输详情对话框 -->
    <el-dialog
      v-model="kvcacheDialogVisible"
      title="KVCache 传输详情"
      width="900px"
      :close-on-click-modal="false"
    >
      <div class="kvcache-content">
        <div class="kvcache-info">
          <el-alert
            title="KVCache 传输说明"
            type="info"
            :closable="false"
            style="margin-bottom: 16px"
          >
            <div>• <strong>Prefill 阶段</strong>：处理输入 prompt，生成 KVCache</div>
            <div>• <strong>Decode 阶段</strong>：接收 KVCache，自回归生成 token</div>
            <div>• <strong>传输路径</strong>：通过 OTN 专线（ODU4 100G）从 P 实例传输到 D 实例</div>
          </el-alert>
        </div>
        
        <div class="kvcache-diagram">
          <div class="diagram-title">KVCache 传输示意图</div>
          <div class="diagram-body">
            <div class="instance-box prefill">
              <div class="box-icon">P</div>
              <div class="box-info">
                <div class="box-title">Prefill 实例</div>
                <div class="box-detail">{{ currentTask?.pInstance?.node }}</div>
                <div class="box-detail">{{ currentTask?.pInstance?.cluster }}</div>
              </div>
            </div>
            
            <div class="transfer-arrow">
              <div class="arrow-line"></div>
              <div class="arrow-text">KVCache</div>
              <div class="arrow-subtext">{{ currentTask?.networkLink?.bandwidth || "100G" }}</div>
              <div class="arrow-subtext">{{ currentTask?.networkLink?.oduType || "ODU4" }}</div>
            </div>
            
            <div class="instance-box decode">
              <div class="box-icon">D</div>
              <div class="box-info">
                <div class="box-title">Decode 实例</div>
                <div class="box-detail">{{ currentTask?.dInstance?.node }}</div>
                <div class="box-detail">{{ currentTask?.dInstance?.cluster }}</div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="kvcache-metrics">
          <el-descriptions title="传输指标" :column="2" border>
            <el-descriptions-item label="源节点">{{ currentTask?.pInstance?.node }}</el-descriptions-item>
            <el-descriptions-item label="目的节点">{{ currentTask?.dInstance?.node }}</el-descriptions-item>
            <el-descriptions-item label="带宽">{{ currentTask?.networkLink?.bandwidth || "100G" }}</el-descriptions-item>
            <el-descriptions-item label="ODU 类型">{{ currentTask?.networkLink?.oduType || "ODU4" }}</el-descriptions-item>
            <el-descriptions-item label="时延">{{ currentTask?.networkLink?.latency || "~0.5ms" }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="currentTask?.status === 'RUNNING' ? 'success' : 'warning'" size="small">
                {{ currentTask?.status === 'RUNNING' ? '传输中' : '等待中' }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="kvcacheDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue"
import { useRouter } from "vue-router"
import { ElMessage, ElMessageBox } from "element-plus"
import { getTaskList, cancelTask } from "@/api/modules/task"
import { getNetworkTopology } from "@/api/modules/network"

const router = useRouter()
const taskList = ref<any[]>([])
const loading = ref(false)
const kvcacheDialogVisible = ref(false)
const currentTask = ref<any>(null)
const statusMap: Record<string, string> = {
  RUNNING: "success", PENDING: "warning", COMPLETED: "info", FAILED: "danger"
}

// 节点映射（从后端动态获取）
const nodeMap = ref<Record<string, string>>({})

// 从后端获取拓扑，构建节点映射
async function fetchNodeMap() {
  try {
    const res: any = await getNetworkTopology()
    console.log("任务列表 - 后端返回的拓扑数据:", res)
    
    if (res?.data?.networks?.[0]?.node) {
      const nodes = res.data.networks[0].node
      nodeMap.value = nodes.reduce((map: any, node: any) => {
        const nodeId = node["node-id"] || node["ietf-te-topology:te-node-id"]
        // 优先使用 label（如：韶关数据中心 1 号），其次使用 name（如：ShaoGuan-DC-1）
        const nodeName = node["label"] || node["name"] || nodeId
        map[nodeId] = nodeName
        return map
      }, {})
      console.log("节点映射:", nodeMap.value)
      
      if (Object.keys(nodeMap.value).length === 0) {
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
    nodeMap.value = {
      "10.10.10.1": "ShaoGuan-DC-1",
      "10.10.10.2": "ShaoGuan-DC-2",
      "10.10.10.3": "GuangZhou-DC-1",
      "10.10.10.4": "GuangZhou-DC-2",
      "10.10.10.5": "ShenZhen-DC-1",
      "10.10.10.6": "ShenZhen-DC-2",
      "10.10.10.7": "DongGuan-DC-1",
      "10.10.10.8": "FoShan-DC-1",
      "10.10.10.9": "ZhuHai-DC-1",
      "10.10.10.10": "HuiZhou-DC-1"
    }
    console.log("使用默认节点映射:", nodeMap.value)
  }
}

// 根据节点 ID 生成集群名称（使用动态 nodeMap）
function generateClusterName(nodeId: string): string {
  // 从 nodeMap 中获取节点名称
  const nodeName = nodeMap.value[nodeId] || nodeId
  
  // 如果节点名称包含 DC 信息，直接使用
  if (nodeName.includes("DC-") || nodeName.includes("dc-")) {
    return nodeName
  }
  
  // 否则尝试从名称中提取城市信息
  // 例如：ShaoGuan-DC-1 => ShaoGuan-DC-A
  const match = nodeName.match(/^(.+?)(-\d+)$/i)
  if (match) {
    const baseName = match[1]
    const num = match[2]
    const dcSuffix = (parseInt(num) % 2 === 1) ? "DC-A" : "DC-B"
    return `${baseName}-${dcSuffix}`
  }
  
  // 默认返回节点名称
  return nodeName
}

async function fetchTaskList() {
  loading.value = true
  try {
    const res: any = await getTaskList()
    console.log("任务列表 API 返回:", res)
    
    // 从 localStorage 获取部署历史（用于显示任务名称和光网配置）
    const deployHistory = JSON.parse(localStorage.getItem("deploy_history") || "[]")
    console.log("localStorage 中的部署历史:", deployHistory)
    
    if (res?.data && Array.isArray(res.data)) {
      // 将后端 TE 隧道数据转换为前端任务格式
      taskList.value = res.data.map((tunnel: any, index: number) => {
        const sourceNode = tunnel.source || ""
        const destNode = tunnel.destination || ""
        const tunnelName = tunnel["tunnel-name"] || ""
        
        console.log(`处理隧道 ${index + 1}:`, {
          tunnelName,
          source: sourceNode,
          destination: destNode,
          "te-bandwidth": tunnel["te-bandwidth"],
          delay: tunnel["delay"],
          latency: tunnel["latency"]
        })
        
        // 使用动态的节点名称映射
        const sourceNodeName = nodeMap.value[sourceNode] || sourceNode
        const destNodeName = nodeMap.value[destNode] || destNode
        
        // 根据节点 ID 生成集群名称（与后端保持一致）
        const pCluster = generateClusterName(sourceNode)
        const dCluster = generateClusterName(destNode)
        
        // 尝试从部署历史中查找任务名称和光网配置
        // 通过匹配 P/D 集群节点来关联
        const deployInfo = deployHistory.find((d: any) => {
          // 简单匹配：使用最近部署的 P/D 集群
          const match = d.pCluster === sourceNode && d.dCluster === destNode
          console.log(`  匹配部署历史：${d.pCluster} === ${sourceNode} && ${d.dCluster} === ${destNode} => ${match}`)
          return match
        })
        
        console.log("  找到的部署信息:", deployInfo)
        
        // 模型名称固定为 LLaMA3-70B
        const modelName = "LLaMA3-70B"
        const displayName = deployInfo?.taskName || tunnel["task-name"] || `P/D 推理服务-${index + 1}`
        console.log("  任务名称:", displayName)
        
        // 从后端返回的数据中提取 ODU 类型
        // 后端返回格式：te-bandwidth: {"ietf-otn-tunnel:odu-type": "ietf-otn-types:prot-ODU4"}
        const teBandwidth = tunnel["te-bandwidth"] || {}
        const backendOduType = teBandwidth["ietf-otn-tunnel:odu-type"] || ""
        
        // 将后端 ODU 类型转换为显示格式
        const backendOduDisplay = backendOduType.includes("ODU4") ? "ODU4" :
                                 backendOduType.includes("ODU3") ? "ODU3" :
                                 backendOduType.includes("ODU2") ? "ODU2" : "ODU4"
        
        // 从后端返回的数据中提取带宽（根据 ODU 类型推断）
        const backendBandwidth = backendOduType.includes("ODU4") ? "100G" :
                                backendOduType.includes("ODU3") ? "40G" :
                                backendOduType.includes("ODU2") ? "10G" : "100G"
        
        // 从后端返回的数据中提取时延（如果有的话）
        // 后端返回的时延单位是微秒 (us)，需要转换为毫秒 (ms)
        const backendLatency = tunnel["delay"] || tunnel["latency"] || 500  // 默认 500us
        const latencyMs = (backendLatency / 1000).toFixed(2)  // 转换为 ms，保留 2 位小数
        
        // 优先使用部署时设定的光网配置，其次使用后端返回的
        const networkBandwidth = deployInfo?.bandwidth ? 
                                (deployInfo.bandwidth === "100000" ? "100G" : 
                                 deployInfo.bandwidth === "50000" ? "50G" : 
                                 deployInfo.bandwidth === "10000" ? "10G" : "100G") :
                                backendBandwidth
        const networkOduType = deployInfo?.oduType ? 
                              (deployInfo.oduType.includes("ODU4") ? "ODU4" :
                               deployInfo.oduType.includes("ODU3") ? "ODU3" :
                               deployInfo.oduType.includes("ODU2") ? "ODU2" : "ODU4") :
                              backendOduDisplay
        
        return {
          taskId: tunnelName || `T${String(index + 1).padStart(3, "0")}`,
          taskName: displayName,
          modelName: modelName,
          pInstance: { 
            node: sourceNodeName,
            cluster: pCluster,
            status: "RUNNING"
          },
          dInstance: { 
            node: destNodeName,
            cluster: dCluster,
            status: "RUNNING"
          },
          proxyInstance: { 
            node: destNodeName,
            cluster: dCluster,
            status: "RUNNING"
          },
          networkLink: { 
            source: sourceNodeName, 
            target: destNodeName, 
            bandwidth: networkBandwidth,
            oduType: networkOduType,
            latency: latencyMs + "ms"  // ✅ 添加时延信息
          },
          status: tunnel["provisioning-state"] === "up" ? "RUNNING" : "PENDING",
          createdAt: formatTime(tunnel["create-time"])
        }
      })
      console.log("转换后的任务列表:", taskList.value)
    } else {
      taskList.value = []
    }
  } catch (error: any) {
    console.error("获取任务列表失败:", error)
    ElMessage.error("获取任务列表失败：" + (error.message || "网络错误"))
    taskList.value = []
  } finally {
    loading.value = false
  }
}

// 格式化时间
function formatTime(timeStr: string): string {
  if (!timeStr) return new Date().toLocaleString("zh-CN", { hour12: false }).replace(/\//g, "-")
  const timeWithoutZ = timeStr.replace("Z", "")
  const date = new Date(timeWithoutZ)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, "0")
  const day = String(date.getDate()).padStart(2, "0")
  const hours = String(date.getHours()).padStart(2, "0")
  const minutes = String(date.getMinutes()).padStart(2, "0")
  const seconds = String(date.getSeconds()).padStart(2, "0")
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

async function handleCancel(row: any) {
  try {
    await ElMessageBox.confirm("确定要取消该任务吗？取消后将删除 TE 隧道并释放资源。", "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning"
    })
    
    loading.value = true
    await cancelTask(row.taskId)
    ElMessage.success("任务已取消")
    await fetchTaskList()
  } catch (error: any) {
    if (error !== "cancel") {
      console.error("取消任务失败:", error)
      ElMessage.error("取消任务失败：" + (error.message || "网络错误"))
    }
  } finally {
    loading.value = false
  }
}

function showKvCache(row: any) {
  currentTask.value = row
  kvcacheDialogVisible.value = true
}

onMounted(() => {
  // 先获取节点映射，再获取任务列表
  fetchNodeMap().then(() => {
    fetchTaskList()
  }).catch(() => {
    fetchTaskList()
  })
})
</script>

<style scoped lang="scss">
.task-page {
  .page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
}

.kvcache-content {
  .kvcache-info {
    margin-bottom: 20px;
  }
  
  .kvcache-diagram {
    margin: 20px 0;
    
    .diagram-title {
      font-size: 16px;
      font-weight: bold;
      margin-bottom: 16px;
      color: #303133;
    }
    
    .diagram-body {
      display: flex;
      align-items: center;
      justify-content: space-around;
      padding: 30px 20px;
      background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
      border-radius: 8px;
      position: relative;
      
      .instance-box {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 16px 20px;
        background: #fff;
        border-radius: 8px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
        min-width: 180px;
        
        &.prefill {
          border-left: 4px solid #409EFF;
          
          .box-icon {
            background: #409EFF;
          }
        }
        
        &.decode {
          border-left: 4px solid #67C23A;
          
          .box-icon {
            background: #67C23A;
          }
        }
        
        .box-icon {
          width: 48px;
          height: 48px;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #fff;
          font-weight: bold;
          font-size: 20px;
          flex-shrink: 0;
        }
        
        .box-info {
          display: flex;
          flex-direction: column;
          gap: 4px;
          
          .box-title {
            font-weight: bold;
            font-size: 14px;
            color: #303133;
          }
          
          .box-detail {
            font-size: 12px;
            color: #909399;
          }
        }
      }
      
      .transfer-arrow {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 8px;
        position: relative;
        padding: 0 40px;
        
        .arrow-line {
          width: 120px;
          height: 3px;
          background: linear-gradient(90deg, #409EFF 0%, #E6A23C 50%, #67C23A 100%);
          position: relative;
          
          &::after {
            content: '';
            position: absolute;
            right: -8px;
            top: 50%;
            transform: translateY(-50%);
            border-left: 10px solid #67C23A;
            border-top: 6px solid transparent;
            border-bottom: 6px solid transparent;
          }
        }
        
        .arrow-text {
          font-weight: bold;
          color: #E6A23C;
          font-size: 14px;
          margin-top: 8px;
        }
        
        .arrow-subtext {
          font-size: 12px;
          color: #909399;
        }
      }
    }
  }
  
  .kvcache-metrics {
    margin-top: 20px;
  }
}
</style>
