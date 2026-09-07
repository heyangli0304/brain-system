import http from "@/api"

export function submitInferJob(data: {
  TaskjobName: string
  ClusterName: string
  role: string
  GpuCount?: number
  GpuType?: string
  LlmModelId?: number
}) {
  return http.post<any>("/api/v1/compute/inferjob", data)
}

export function getJobDetail(job_id: number) {
  return http.get<any>(`/api/v1/compute/monitor/job/${job_id}`)
}

export function getJobMetrics(job_id: number, cluster: string) {
  return http.get<any>("/api/v1/compute/monitor/metrics/job", { job_id, cluster })
}
