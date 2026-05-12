import { defineStore } from "pinia"

export const useUserStore = defineStore({
  id: "brain-user",
  state: () => ({
    token: localStorage.getItem("brain_token") || "",
    username: "",
    role: "user" as "admin" | "user",
    avatar: ""
  }),
  getters: {
    isAdmin: state => state.role === "admin"
  },
  actions: {
    setToken(token: string) {
      this.token = token
      localStorage.setItem("brain_token", token)
    },
    setUserInfo(info: { username: string; role: "admin" | "user"; avatar?: string }) {
      this.username = info.username
      this.role = info.role
      this.avatar = info.avatar || ""
    },
    logout() {
      this.token = ""
      this.username = ""
      this.role = "user"
      localStorage.removeItem("brain_token")
    }
  },
  persist: true
})
