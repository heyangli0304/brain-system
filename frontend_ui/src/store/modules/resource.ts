import { defineStore } from "pinia"

export const useResourceStore = defineStore({
  id: "brain-resource",
  state: () => ({
    clusterData: [] as any[],
    networkTopology: null as any,
    lastUpdateTime: ""
  }),
  actions: {
    setClusterData(data: any[]) {
      this.clusterData = data
      this.lastUpdateTime = new Date().toLocaleString()
    },
    setNetworkTopology(data: any) {
      this.networkTopology = data
    }
  },
  persist: true
})
