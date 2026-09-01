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

export interface PDInferJobRequest {
  TaskjobName: string
  ClusterName: string
  Account: string
  Partition: string
  NodeCount: number
  CoreCount: number
  Role?: "" | "Prefill" | "Decode" | "Proxy"
  Qos?: string
  GpuCount?: number
  GpuType?: string
  MemoryMb?: number
  TimeLimitMinutes?: number
  MountPoints?: string[]
  Dataset?: string
  Model?: string
  Algorithm?: string
  Vram?: number
  DataDir?: string
  WorkingDirectory?: string
  LlmModelId?: number
  PrefillerHosts?: string
  PrefillerPorts?: string
  DecoderHosts?: string
  DecoderPorts?: string
}

export function submitPDInferJob(data: PDInferJobRequest) {
  return http.post<any>("/api/v1/compute/adapter/pdinferjobs", data)
}

export function getJobDetail(job_id: number) {
  return http.get<any>("/api/v1/compute/adapter/getSpecPDJob", { jobId: job_id })
}

export function getJobMetrics(job_id: number, cluster: string) {
  return http.get<any>("/api/v1/compute/adapter/getPDJobMonitorMetrics", { jobId: job_id, cluster })
}

export function submitChatCompletion(
  jobId: string,
  data: {
    model: string
    messages: any[]
    stream?: boolean | string
    max_tokens?: number
  }
) {
  return http.post<any>(
    `/api/v1/compute/modelProxy/${encodeURIComponent(jobId)}/v1/chat/completions`,
    data
  )
}

export function submitDirectChatCompletion(
  inferenceAddr: string,
  data: {
    model: string
    messages: any[]
    stream?: boolean
    max_tokens?: number
  }
) {
  return http.post<any>("/api/v1/compute/inference/chat/completions", {
    inferenceAddr,
    ...data,
  })
}

export function cancelPDJob(jobId: number, cluster?: string) {
  return http.delete<any>("/api/v1/compute/adapter/CancelSpecPDJob", { jobId, cluster })
}

export function queryPDJobTimeLimit(jobId: number, cluster?: string) {
  return http.get<any>("/api/v1/compute/adapter/queryPDJobTimeLimit", { jobId, cluster })
}

export function changePDJobTimeLimit(JobId: number, DeltaMinutes: number, Cluster?: string) {
  return http.post<any>("/api/v1/compute/adapter/changePDJobTimeLimit", { JobId, DeltaMinutes, Cluster })
}
