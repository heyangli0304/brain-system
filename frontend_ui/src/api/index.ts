import axios, { AxiosInstance, AxiosRequestConfig, InternalAxiosRequestConfig, AxiosResponse } from "axios"
import { ElMessage } from "element-plus"
import router from "@/router"

interface CustomAxiosRequestConfig extends InternalAxiosRequestConfig {
  loading?: boolean
}

const config = {
  baseURL: "",
  timeout: 30000,
  withCredentials: true
}

class RequestHttp {
  service: AxiosInstance
  constructor(config: AxiosRequestConfig) {
    this.service = axios.create(config)
    this.service.interceptors.request.use(
      (config: CustomAxiosRequestConfig) => {
        const token = localStorage.getItem("brain_token")
        if (token && config.headers && typeof config.headers.set === "function") {
          config.headers.set("Authorization", `Bearer ${token}`)
        }
        return config
      },
      error => Promise.reject(error)
    )
    this.service.interceptors.response.use(
      (response: AxiosResponse) => {
        const { data } = response
        if (data.respCode !== undefined && data.respCode !== 0) {
          ElMessage.error(data.respError || "请求失败")
          if (data.respCode === 401) {
            localStorage.removeItem("brain_token")
            router.replace("/login")
          }
          return Promise.reject(data)
        }
        return data
      },
      error => {
        if (error.message.indexOf("timeout") !== -1) ElMessage.error("请求超时")
        if (error.message.indexOf("Network Error") !== -1) ElMessage.error("网络错误")
        if (error.response) {
          const status = error.response.status
          if (status === 401) {
            localStorage.removeItem("brain_token")
            router.replace("/login")
          } else if (status === 403) {
            router.replace("/403")
          } else if (status === 500) {
            router.replace("/500")
          }
        }
        return Promise.reject(error)
      }
    )
  }
  get<T>(url: string, params?: object, _object = {}): Promise<T> {
    return this.service.get(url, { params, ..._object })
  }
  post<T>(url: string, params?: object, _object = {}): Promise<T> {
    return this.service.post(url, params, _object)
  }
  put<T>(url: string, params?: object, _object = {}): Promise<T> {
    return this.service.put(url, params, _object)
  }
  delete<T>(url: string, params?: any, _object = {}): Promise<T> {
    return this.service.delete(url, { params, ..._object })
  }
}

export default new RequestHttp(config)
