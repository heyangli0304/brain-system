import http from "@/api"

export function submitPDDeploy(data: {
  source_node: string
  dest_node: string
  model_name: string
  task_name: string
  odu_type?: string
  bandwidth?: string
  p_cluster?: string
  d_cluster?: string
}) {
  return http.post<any>("/api/v1/orchestrator/pd/deploy", data)
}

export function rollbackPDDeploy(tunnel_name: string) {
  return http.post<any>("/api/v1/orchestrator/pd/rollback", { tunnel_name })
}

export function cancelTask(tunnel_name: string) {
  // 调用删除 TE 隧道接口
  return http.delete<any>(`/api/v1/actn/te/tunnel/${tunnel_name}`)
}

export function getTaskList() {
  // 调用光网 TE 隧道列表接口
  return http.get<any>("/api/v1/actn/te/tunnels")
}

export function getTaskDetail(tunnel_name: string) {
  return http.get<any>(`/api/v1/actn/te/tunnel/${tunnel_name}`)
}
