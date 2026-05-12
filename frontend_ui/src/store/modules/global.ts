import { defineStore } from "pinia"

export const useGlobalStore = defineStore({
  id: "brain-global",
  state: () => ({
    isCollapse: false,
    isDark: false,
    maximize: false,
    tabsList: [] as any[],
    breadcrumb: true,
    footer: true
  }),
  actions: {
    setCollapse(val: boolean) {
      this.isCollapse = val
    },
    setDark(val: boolean) {
      this.isDark = val
    },
    setMaximize(val: boolean) {
      this.maximize = val
    },
    addTab(tab: any) {
      if (!this.tabsList.find(t => t.path === tab.path)) {
        this.tabsList.push(tab)
      }
    },
    removeTab(path: string) {
      this.tabsList = this.tabsList.filter(t => t.path !== path)
    }
  },
  persist: true
})
