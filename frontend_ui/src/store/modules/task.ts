import { defineStore } from "pinia"

export const useTaskStore = defineStore({
  id: "brain-task",
  state: () => ({
    taskList: [] as any[],
    currentTask: null as any,
    taskNetworkInfo: null as any
  }),
  actions: {
    setTaskList(list: any[]) {
      this.taskList = list
    },
    setCurrentTask(task: any) {
      this.currentTask = task
    },
    setTaskNetworkInfo(info: any) {
      this.taskNetworkInfo = info
    }
  }
})
