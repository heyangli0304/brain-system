<template>
  <div class="inference-page">
    <div class="page-header"><h2>多模态推理</h2></div>
    <el-row :gutter="16">
      <el-col :span="8">
        <el-card header="推理配置">
          <el-alert
            title="模型说明"
            type="info"
            :closable="false"
            style="margin-bottom: 16px"
          >
            <div>当前使用模型：<strong>LLaMA3-70B</strong></div>
            <div>模型 ID：1001（后端固定）</div>
          </el-alert>
          <el-form label-width="100px">
            <el-form-item label="选择服务">
              <el-select v-model="selectedJob" placeholder="选择已部署的推理服务" style="width: 100%">
                <el-option v-for="job in jobList" :key="job.id" :label="job.name" :value="job.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="模型">
              <el-input v-model="modelName" disabled />
            </el-form-item>
            <el-form-item label="GPU 类型">
              <el-input v-model="gpuType" disabled />
            </el-form-item>
            <el-form-item label="部署模式">
              <el-tag type="success">P/D 分离部署</el-tag>
            </el-form-item>
            <el-form-item label="输出模式">
              <el-radio-group v-model="streamMode">
                <el-radio value="true">流式输出</el-radio>
                <el-radio value="false">完整输出</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
      <el-col :span="16">
        <el-card header="对话">
          <div class="chat-container" ref="chatRef">
            <div v-for="(msg, idx) in messages" :key="idx" :class="['chat-msg', msg.role === 'user' ? 'msg-user' : 'msg-assistant']">
              <div class="msg-content">{{ msg.content }}</div>
            </div>
          </div>
          <div class="chat-input">
            <el-input v-model="inputText" placeholder="输入您的问题..." @keyup.enter="sendMessage" :disabled="!selectedJob">
              <template #append>
                <el-button @click="sendMessage" :disabled="!selectedJob || !inputText">发送</el-button>
              </template>
            </el-input>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted } from "vue"
import { ElMessage } from "element-plus"
import { getTaskList } from "@/api/modules/task"
import { getNetworkTopology } from "@/api/modules/network"

const selectedJob = ref("")
const modelName = ref("LLaMA3-70B")
const gpuType = ref("A100-80G")
const streamMode = ref("true")
const inputText = ref("")
const chatRef = ref<HTMLDivElement>()
const loading = ref(false)

// 从后端获取已部署的作业列表
const jobList = ref<any[]>([])

// 节点映射（从后端动态获取）
const nodeMap = ref<Record<string, string>>({})

const messages = ref<{ role: string; content: string }[]>([])

// 从后端获取拓扑，构建节点映射
async function fetchNodeMap() {
  try {
    const res: any = await getNetworkTopology()
    console.log("推理页面 - 后端返回的拓扑数据:", res)
    
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

async function fetchJobList() {
  try {
    // 调用后端接口获取已部署的作业列表
    const res: any = await getTaskList()
    if (res?.data) {
      // 解析后端返回的 TE 隧道数据，转换为作业列表
      jobList.value = res.data.map((tunnel: any, idx: number) => {
        // 使用节点 ID 获取映射后的名称
        const sourceNode = tunnel.source || ""
        const destNode = tunnel.destination || ""
        
        // 从动态获取的 nodeMap 中查找，如果没有则显示原始 ID
        const sourceCity = nodeMap.value[sourceNode] || sourceNode
        const destCity = nodeMap.value[destNode] || destNode
        
        // 使用任务名称（如果没有则使用默认名称）
        const taskName = tunnel["task-name"] || `P/D 推理服务 ${idx + 1}`
        
        return {
          id: tunnel["tunnel-name"] || `job-${idx}`,
          name: `${taskName} (${sourceCity} → ${destCity})`,
          tunnel: tunnel
        }
      })
    }
    
    // 如果没有数据，使用空数组（不显示模拟数据）
    if (jobList.value.length === 0) {
      console.log("暂无已部署的推理服务")
    }
  } catch (error: any) {
    console.error("获取作业列表失败:", error)
    ElMessage.error("获取作业列表失败：" + (error.message || "网络错误"))
    jobList.value = []
  }
}

async function sendMessage() {
  console.log("发送消息，selectedJob:", selectedJob.value, "inputText:", inputText.value)
  
  if (!inputText.value.trim()) {
    console.log("输入为空")
    return
  }
  if (!selectedJob.value) {
    ElMessage.warning("请先选择推理服务")
    return
  }
  
  messages.value.push({ role: "user", content: inputText.value })
  const userMsg = inputText.value
  inputText.value = ""
  loading.value = true
  
  console.log("消息已添加，当前消息数:", messages.value.length)
  
  await nextTick()
  if (chatRef.value) {
    chatRef.value.scrollTop = chatRef.value.scrollHeight
    console.log("滚动到顶部")
  }
  
  try {
    // 调用后端推理接口
    // 实际应该调用推理服务的 chat/completions 接口
    ElMessage.info("正在调用推理服务...")
    
    // 模拟响应（实际应该等待后端返回）
    setTimeout(() => {
      messages.value.push({ 
        role: "assistant", 
        content: `这是一个模拟响应。\n\n您问的是："${userMsg}"\n\n实际推理功能需要调用已部署的推理服务 API。` 
      })
      loading.value = false
      console.log("响应已添加，当前消息数:", messages.value.length)
      nextTick(() => {
        if (chatRef.value) chatRef.value.scrollTop = chatRef.value.scrollHeight
      })
    }, 1000)
  } catch (error: any) {
    ElMessage.error("推理请求失败：" + (error.message || "未知错误"))
    loading.value = false
  }
}

onMounted(() => {
  // 先获取节点映射，再获取作业列表
  fetchNodeMap().then(() => {
    fetchJobList()
  }).catch(() => {
    fetchJobList()
  })
})
</script>

<style scoped lang="scss">
.inference-page {
  padding: 20px;
  
  .page-header { 
    margin-bottom: 16px;
    h2 { margin: 0; }
  }
  
  .chat-container {
    height: 400px; 
    overflow-y: auto; 
    padding: 12px; 
    background: #f5f7fa; 
    border-radius: 8px;
    margin-bottom: 12px;
    
    .chat-msg { 
      margin-bottom: 12px; 
      display: flex;
      
      &.msg-user { 
        justify-content: flex-end; 
        
        .msg-content { 
          background: #409eff; 
          color: #fff; 
        } 
      }
      
      &.msg-assistant { 
        justify-content: flex-start; 
        
        .msg-content { 
          background: #fff; 
          border: 1px solid #e4e7ed; 
        } 
      }
      
      .msg-content { 
        padding: 8px 12px; 
        border-radius: 8px; 
        max-width: 70%; 
        line-height: 1.5; 
        word-wrap: break-word;
      }
    }
  }
  
  .chat-input { 
    margin-top: 12px;
    
    :deep(.el-input__wrapper) {
      border-radius: 4px;
    }
    
    :deep(.el-button) {
      margin-left: 8px;
    }
  }
}
</style>
