<template>
  <div ref="chartRef" class="topology-chart">
    <div class="kvcache-legend" v-if="showKvCache">
      <div class="legend-item">
        <span class="legend-dot kvcache"></span>
        <span class="legend-text">KVCache 传输</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from "vue"
import * as echarts from "echarts"

const props = defineProps<{
  nodes: any[]
  links: any[]
  showKvCache?: boolean  // 是否显示 KVCache 传输
  pInstanceNode?: string  // Prefill 实例所在节点
  dInstanceNode?: string  // Decode 实例所在节点
}>()

const chartRef = ref<HTMLDivElement>()
let chartInstance: echarts.ECharts | null = null
let animationFrameId: number | null = null

function renderChart() {
  if (!chartRef.value) return
  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }
  
  const option: any = {
    tooltip: {
      formatter: (params: any) => {
        if (params.dataType === 'edge') {
          const link = params.data
          return `<div style="padding: 8px">
            <div style="font-weight: bold; margin-bottom: 4px">${link.source} → ${link.target}</div>
            <div>带宽：${formatBandwidth(link.bandwidth)}</div>
            <div>ODU: ${link.supportOdu ? link.supportOdu.join(', ') : ''}</div>
          </div>`
        }
        return params.name
      }
    },
    series: [{
      type: "graph",
      layout: "force",
      roam: true,
      label: { show: true, fontSize: 11, position: 'bottom' },
      force: { repulsion: 500, edgeLength: [120, 250], gravity: 0.1 },
      data: props.nodes,
      links: props.links,
      categories: [
        { name: "数据中心" },
        { name: "P 实例" },
        { name: "D 实例" },
        { name: "光网节点" }
      ],
      itemStyle: { 
        borderColor: "#fff", 
        borderWidth: 2,
        color: (params: any) => {
          const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C']
          return colors[params.category] || colors[0]
        }
      },
      lineStyle: {
        width: 2,
        color: '#909399',
        curveness: 0.1
      },
      emphasis: {
        focus: 'adjacency',
        lineStyle: {
          width: 4,
          color: '#409EFF'
        }
      }
    }]
  }
  
  // 如果显示 KVCache 传输，添加动态效果
  if (props.showKvCache && props.pInstanceNode && props.dInstanceNode) {
    // 添加 KVCache 传输的动态粒子效果
    const kvcacheLines = [{
      coords: [
        getNodeCoords(props.pInstanceNode, props.nodes),
        getNodeCoords(props.dInstanceNode, props.nodes)
      ],
      lineStyle: {
        color: '#E6A23C',
        width: 3,
        type: 'dashed'
      }
    }]
    
    option.series.push({
      type: 'lines',
      coordinateSystem: 'cartesian2d',
      zlevel: 2,
      effect: {
        show: true,
        period: 2,
        trailLength: 0.7,
        color: '#E6A23C',
        symbolSize: 8,
        symbol: 'circle'
      },
      lineStyle: {
        color: '#E6A23C',
        width: 0,
        curveness: 0.2
      },
      data: kvcacheLines
    })
    
    // 添加文字标注
    option.series.push({
      type: 'custom',
      coordinateSystem: 'cartesian2d',
      zlevel: 3,
      renderItem: (params: any, api: any) => {
        const point = api.coord([
          (getNodeCoords(props.pInstanceNode!, props.nodes)[0] + getNodeCoords(props.dInstanceNode!, props.nodes)[0]) / 2,
          (getNodeCoords(props.pInstanceNode!, props.nodes)[1] + getNodeCoords(props.dInstanceNode!, props.nodes)[1]) / 2
        ])
        return {
          type: 'text',
          style: {
            text: 'KVCache',
            fill: '#E6A23C',
            font: 'bold 14px sans-serif',
            x: point[0],
            y: point[1] - 20
          }
        }
      },
      data: [{}]
    })
  }
  
  chartInstance.setOption(option)
}

function getNodeCoords(nodeName: string, nodes: any[]): [number, number] {
  // 简单返回节点在力导向图中的位置
  // 实际需要从 ECharts 获取渲染后的坐标
  return [0, 0]
}

function formatBandwidth(bw: string): string {
  if (!bw) return ''
  const bwNum = parseInt(bw)
  if (bwNum >= 1000000) {
    return "1Tbps"
  } else if (bwNum >= 400000) {
    return "400Gbps"
  } else {
    return bwNum + "Mbps"
  }
}

onMounted(() => renderChart())
watch(() => [props.nodes, props.links, props.showKvCache], () => renderChart(), { deep: true })
onUnmounted(() => {
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId)
  }
  chartInstance?.dispose()
})
</script>

<style scoped lang="scss">
.topology-chart { 
  width: 100%; 
  height: 100%; 
  min-height: 400px;
  position: relative;
  
  .kvcache-legend {
    position: absolute;
    top: 10px;
    right: 10px;
    background: rgba(255, 255, 255, 0.9);
    padding: 8px 12px;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    z-index: 10;
    
    .legend-item {
      display: flex;
      align-items: center;
      gap: 6px;
      
      .legend-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        
        &.kvcache {
          background: #E6A23C;
          animation: pulse 1.5s infinite;
        }
      }
      
      .legend-text {
        font-size: 12px;
        color: #606266;
        font-weight: 500;
      }
    }
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.6;
    transform: scale(1.2);
  }
}
</style>
