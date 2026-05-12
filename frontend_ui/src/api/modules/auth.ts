import http from "@/api"

export function loginApi(username: string, password: string) {
  // 前端 Mock 登录：不依赖后端，直接在前端判断角色
  // 支持任意密码登录
  return new Promise<any>((resolve, reject) => {
    // 模拟网络延迟
    setTimeout(() => {
      if (!username) {
        reject({ message: "请输入用户名" })
        return
      }
      
      // 根据用户名判断角色
      const role = username === "admin" ? "admin" : "user"
      
      resolve({
        respCode: 0,
        respMessage: "success",
        respBody: {
          token: `mock-token-${username}-${Date.now()}`,
          username: username,
          role: role
        }
      })
    }, 500)
  })
}

export function getAuthMenuListApi() {
  return http.get<any[]>("/api/v1/orchestrator/auth/menu/list")
}

export function getAuthButtonListApi() {
  return http.get<any>("/api/v1/orchestrator/auth/buttons")
}

export function logoutApi() {
  return http.post<any>("/api/v1/orchestrator/auth/logout")
}
