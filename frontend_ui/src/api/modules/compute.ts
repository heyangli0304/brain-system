import http from "@/api"

export function createDirectory(fs_dir: string, cluster: string) {
  return http.post<any>("/api/v1/compute/fs/dir/create", { fs_dir, cluster })
}

export function subscribeEvents(event_types: string[], description?: string) {
  return http.post<any>("/api/v1/compute/notification/subscribe", { event_types, description })
}

export function getWebhookJobStatus(job_id: number) {
  return http.get<any>(`/api/v1/compute/webhook/job_status/${job_id}`)
}

export function getWebhookNotifications() {
  return http.get<any>("/api/v1/compute/webhook/notifications")
}
