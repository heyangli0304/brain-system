<template>
  <div class="deploy-page">
    <div class="page-header"><h2>P/D 分离部署</h2></div>
    <el-card>
      <el-alert
        title="P/D 分离部署说明"
        type="info"
        :closable="false"
        style="margin-bottom: 16px"
      >
        <div>• 模型：后端固定使用 LLaMA3-70B 模型（LlmModelId: 1001）</div>
        <div>• Prefill 实例：部署在 P 集群的 GPU 上</div>
        <div>• Decode 实例：部署在 D 集群的 GPU 上</div>
        <div>• Proxy 实例：自动部署在 D 集群，负责请求转发</div>
        <div>• 集群名称：根据选择的节点自动生成（如：ShaoGuan-DC-A）</div>
        <div>• GPU 数量：仅用于前端显示，不影响实际部署</div>
      </el-alert>
      
      <el-form :model="deployForm" :rules="rules" ref="formRef" label-width="140px" style="max-width: 700px">
        <el-form-item label="任务名称" prop="taskName">
          <el-input v-model="deployForm.taskName" placeholder="如：LLaMA3-PD 部署" />
        </el-form-item>
        
        <el-divider content-position="left">Prefill 阶段（P 实例）</el-divider>
        <el-form-item label="P 集群节点" prop="pCluster">
          <el-select v-model="deployForm.pCluster" placeholder="选择 Prefill 集群节点" style="width: 100%">
            <el-option 
              v-for="node in nodeList" 
              :key="node.id" 
              :label="`${node.label} (${node.name})`" 
              :value="node.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="P 实例 GPU 数量" prop="pGpuCount">
          <el-input-number v-model="deployForm.pGpuCount" :min="1" :max="64" />
          <span class="form-tip">每个节点最多 8 张 A100-80G 显卡（仅显示用）</span>
        </el-form-item>
        
        <el-divider content-position="left">Decode 阶段（D 实例）</el-divider>
        <el-form-item label="D 集群节点" prop="dCluster">
          <el-select v-model="deployForm.dCluster" placeholder="选择 Decode 集群节点" style="width: 100%">
            <el-option 
              v-for="node in nodeList" 
              :key="node.id" 
              :label="`${node.label} (${node.name})`" 
              :value="node.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="D 实例 GPU 数量" prop="dGpuCount">
          <el-input-number v-model="deployForm.dGpuCount" :min="1" :max="64" />
          <span class="form-tip">每个节点最多 8 张 A100-80G 显卡（仅显示用）</span>
        </el-form-item>
        
        <el-divider content-position="left">光网配置</el-divider>
        <el-form-item label="ODU 类型">
          <el-select v-model="deployForm.oduType">
            <el-option label="ODU4 (100G)" value="ietf-otn-types:prot-ODU4" />
            <el-option label="ODU3 (40G)" value="ietf-otn-types:prot-ODU3" />
            <el-option label="ODU2 (10G)" value="ietf-otn-types:prot-ODU2" />
          </el-select>
          <span class="form-tip">OTN 专线类型，决定带宽上限</span>
        </el-form-item>
        <el-form-item label="带宽需求">
          <el-select v-model="deployForm.bandwidth">
            <el-option label="100Gbps" value="100000" />
            <el-option label="50Gbps" value="50000" />
            <el-option label="10Gbps" value="10000" />
          </el-select>
          <span class="form-tip">P/D 间 KVCache 传输所需带宽</span>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleSubmit">提交部署</el-button>
          <el-button @click="router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue"
import { useRouter } from "vue-router"
import { ElMessage } from "element-plus"
import { submitPDDeploy } from "@/api/modules/task"
import { getNetworkTopology } from "@/api/modules/network"

const router = useRouter()
const formRef = ref()
const loading = ref(false)

// 节点列表（从后端动态获取）
const nodeList = ref<any[]>([])

// 从后端获取拓扑，构建节点列表
async function fetchNodeList() {
  try {
    const res: any = await getNetworkTopology()
    console.log("后端返回的拓扑数据:", res)
    
    if (res?.data?.networks?.[0]?.node) {
      const nodes = res.data.networks[0].node
      nodeList.value = nodes.map((node: any) => {
        const nodeId = node["node-id"] || node["ietf-te-topology:te-node-id"]
        const nodeName = node["name"] || node["label"] || nodeId
        const nodeLabel = node["label"] || node["name"] || nodeId
        return {
          id: nodeId,
          name: nodeName,      // 用于显示：ShaoGuan-DC-1
          label: nodeLabel     // 用于显示：韶关数据中心 1 号（如果有）
        }
      })
      console.log("节点列表:", nodeList.value)
      
      if (nodeList.value.length === 0) {
        throw new Error("节点列表为空")
      }
    } else {
      throw new Error("返回数据格式不正确")
    }
  } catch (error: any) {
    console.error("获取拓扑失败:", error)
    // 如果获取失败，使用默认节点列表（降级方案）
    ElMessage.warning("获取节点列表失败，使用默认配置")
    
    // 默认节点配置（与后端 topology.py 保持一致）
    nodeList.value = [
      { id: "10.10.10.1", name: "SG-DC-1", label: "ShaoGuan-DC-1" },
      { id: "10.10.10.2", name: "SG-DC-2", label: "ShaoGuan-DC-2" },
      { id: "10.10.10.3", name: "GZ-DC-1", label: "GuangZhou-DC-1" },
      { id: "10.10.10.4", name: "GZ-DC-2", label: "GuangZhou-DC-2" },
      { id: "10.10.10.5", name: "SZ-DC-1", label: "ShenZhen-DC-1" },
      { id: "10.10.10.6", name: "SZ-DC-2", label: "ShenZhen-DC-2" },
      { id: "10.10.10.7", name: "DG-DC-1", label: "DongGuan-DC-1" },
      { id: "10.10.10.8", name: "FS-DC-1", label: "FoShan-DC-1" },
      { id: "10.10.10.9", name: "ZH-DC-1", label: "ZhuHai-DC-1" },
      { id: "10.10.10.10", name: "HZ-DC-1", label: "HuiZhou-DC-1" }
    ]
    console.log("使用默认节点列表:", nodeList.value)
  }
}

const deployForm = reactive({
  taskName: "",
  pCluster: "",
  pGpuCount: 4,
  dCluster: "",
  dGpuCount: 4,
  oduType: "ietf-otn-types:prot-ODU4",
  bandwidth: "100000"
})

const rules = {
  taskName: [{ required: true, message: "请输入任务名称", trigger: "blur" }],
  pCluster: [{ required: true, message: "请选择 P 集群节点", trigger: "change" }],
  dCluster: [{ required: true, message: "请选择 D 集群节点", trigger: "change" }]
}

async function handleSubmit() {
  await formRef.value?.validate()
  loading.value = true
  try {
    // 根据用户选择的节点 ID 生成集群名称
    // 节点 ID 格式：10.10.10.1-10.10.10.10
    // 集群名称格式：城市名-DC-A/DC-B
    const pClusterName = generateClusterName(deployForm.pCluster)
    const dClusterName = generateClusterName(deployForm.dCluster)
    
    // 提交给后端的数据，严格匹配后端 PDDeployRequest
            const deployData = {
              source_node: deployForm.pCluster,    // 源节点 ID (如：10.10.10.1)
              dest_node: deployForm.dCluster,      // 目的节点 ID (如：10.10.10.3)
              odu_type: deployForm.oduType,        // ODU 类型
              bandwidth: deployForm.bandwidth,     // 带宽
              p_cluster: pClusterName,             // Prefill 集群名称 (如：ShaoGuan-DC-A)
              d_cluster: dClusterName              // Decode 集群名称 (如：GuangZhou-DC-B)
            }
            
            await submitPDDeploy(deployData)
            
            // 保存部署信息到 localStorage（用于前端显示任务名称和光网配置）
            // 因为后端不返回 task-name 和 odu-type，所以前端自行存储
            const deployInfo = {
              taskName: deployForm.taskName,
              pCluster: deployForm.pCluster,
              dCluster: deployForm.dCluster,
              pGpuCount: deployForm.pGpuCount,
              dGpuCount: deployForm.dGpuCount,
              oduType: deployForm.oduType,      // 保存 ODU 类型
              bandwidth: deployForm.bandwidth,  // 保存带宽
              timestamp: Date.now()
            }
            
            // 获取已有的部署历史
            const deployHistory = JSON.parse(localStorage.getItem("deploy_history") || "[]")
            deployHistory.push(deployInfo)
            localStorage.setItem("deploy_history", JSON.stringify(deployHistory))
    
    ElMessage.success("P/D 部署任务已提交，自动创建 Prefill/Decode/Proxy 三个作业实例")
    router.push("/task")
  } catch (error: any) {
    ElMessage.error(error.message || "提交失败")
  } finally {
    loading.value = false
  }
}

// 根据节点 ID 生成集群名称（使用动态 nodeMap）
function generateClusterName(nodeId: string): string {
  // 从 nodeList 中查找节点名称
  const node = nodeList.value.find(n => n.id === nodeId)
  const nodeName = node?.name || nodeId
  
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

onMounted(() => {
  fetchNodeList()
})
</script>

<style scoped lang="scss">
.deploy-page {
  .page-header { margin-bottom: 16px; }
  .form-tip {
    margin-left: 12px;
    font-size: 12px;
    color: #909399;
  }
}
</style>
