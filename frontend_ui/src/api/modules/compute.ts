import http from "@/api"

export function createDirectory(fs_dir: string, cluster: string) {
  return http.post<any>("/api/v1/compute/fs/dir/create", { fs_dir, cluster })
}

export function subscribeEvents(event_types: string[], description?: string) {
  return http.post<any>("/api/v1/compute/notification/webhook/subscribe", { event_types, description })
}

export function unsubscribeEvents(subscription_id?: string) {
  return http.delete<any>("/api/v1/compute/notification/webhook/unsubscribe", { subscription_id })
}

export function notificationStreamUrl() {
  return "/api/v1/compute/notification/stream"
}

export function getWebhookJobStatus(job_id: number) {
  return http.get<any>(`/api/v1/compute/webhook/job_status/${job_id}`)
}

export function getWebhookNotifications() {
  return http.get<any>("/api/v1/compute/webhook/notifications")
}
