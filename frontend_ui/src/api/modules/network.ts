import http from "@/api"

export function getNetworkTopology() {
  return http.get<any>("/api/v1/actn/topology")
}

export function getSimplifiedTopology() {
  return http.get<any>("/api/v1/actn/topology/simplified")
}

export function precomputePath(data: {
  request_id: string
  source_node: string
  destination_node: string
  odu_type?: string
  bandwidth?: string
}) {
  return http.post<any>("/api/v1/actn/path/precompute", data)
}

export function createTeTunnel(data: {
  tunnel_name: string
  source: string
  destination: string
  path_id: string
  odu_type?: string
}) {
  return http.post<any>("/api/v1/actn/te/tunnel", data)
}

export function deleteTeTunnel(tunnel_name: string) {
  return http.delete<any>(`/api/v1/actn/te/tunnel/${tunnel_name}`)
}

export function getTeTunnelDetail(tunnel_name: string) {
  return http.get<any>(`/api/v1/actn/te/tunnel/${tunnel_name}`)
}
