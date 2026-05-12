import { createApp } from "vue"
import App from "./App.vue"
import "element-plus/dist/index.css"
import ElementPlus from "element-plus"
import * as Icons from "@element-plus/icons-vue"
import router from "./router"
import { createPinia } from "pinia"
import piniaPluginPersistedstate from "pinia-plugin-persistedstate"
import "@/styles/reset.scss"

const app = createApp(App)

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

Object.keys(Icons).forEach(key => {
  app.component(key, Icons[key as keyof typeof Icons])
})

app.use(ElementPlus).use(router).use(pinia).mount("#app")
