import http from "@/api"

export function getClusterOverview(cluster_names?: string, region?: string) {
  return http.get<any>("/api/v1/compute/resource/cluster/overview", { cluster_names, region })
}

export function getClusterResource(cluster_names?: string, region?: string) {
  return http.get<any>("/api/v1/compute/resource/cluster/overview", { cluster_names, region })
}

export function getJobMetrics(job_id: number, cluster: string, metric_types?: string, start_time?: string, end_time?: string) {
  return http.get<any>("/api/v1/compute/adapter/getPDJobMonitorMetrics", {
    jobId: job_id,
    cluster,
    metricTypes: metric_types,
    startTime: start_time,
    endTime: end_time,
  })
}

export function getJobMetricsLegacy(job_id: number) {
  return http.get<any>(`/api/v1/compute/monitor/job/${job_id}`)
}
