import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"
import path from "path"

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src")
    }
  },
  server: {
    port: 5173,
    host: "0.0.0.0",
    proxy: {
      "/api/v1/orchestrator": {
        target: "http://localhost:8080",
        changeOrigin: true
      },
      "/api/v1/actn": {
        target: "http://localhost:8080",
        changeOrigin: true
      },
      "/api/v1/compute": {
        target: "http://localhost:8080",
        changeOrigin: true
      }
    }
  }
})
