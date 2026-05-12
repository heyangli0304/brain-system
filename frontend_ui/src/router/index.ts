import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router"
import NProgress from "nprogress"
import "nprogress/nprogress.css"

NProgress.configure({ showSpinner: false })

const staticRouter: RouteRecordRaw[] = [
  {
    path: "/",
    redirect: "/dashboard"
  },
  {
    path: "/login",
    name: "login",
    component: () => import("@/views/login/index.vue"),
    meta: { title: "登录" }
  },
  {
    path: "/layout",
    name: "layout",
    component: () => import("@/layouts/index.vue"),
    redirect: "/dashboard",
    children: [
      {
        path: "/dashboard",
        name: "dashboard",
        component: () => import("@/views/dashboard/index.vue"),
        meta: { title: "资源概况", icon: "Monitor", affix: true }
      },
      {
        path: "/task",
        name: "task",
        component: () => import("@/views/task/index.vue"),
        meta: { title: "任务列表", icon: "List", roles: ["admin", "user"] }
      },
      {
        path: "/task/detail/:id",
        name: "taskDetail",
        component: () => import("@/views/task/detail.vue"),
        meta: { title: "任务详情", icon: "Document", isHide: true, activeMenu: "/task", roles: ["admin", "user"] }
      },
      {
        path: "/deploy",
        name: "deploy",
        component: () => import("@/views/deploy/index.vue"),
        meta: { title: "部署任务", icon: "Upload", roles: ["admin"] }
      },
      {
        path: "/inference",
        name: "inference",
        component: () => import("@/views/inference/index.vue"),
        meta: { title: "多模态推理", icon: "ChatDotRound", roles: ["admin", "user"] }
      },
      {
        path: "/topology",
        name: "topology",
        component: () => import("@/views/topology/index.vue"),
        meta: { title: "网络拓扑", icon: "Connection", roles: ["admin", "user"] }
      }
    ]
  },
  {
    path: "/403",
    name: "403",
    component: () => import("@/components/ErrorMessage/403.vue"),
    meta: { title: "无权限" }
  },
  {
    path: "/404",
    name: "404",
    component: () => import("@/components/ErrorMessage/404.vue"),
    meta: { title: "页面不存在" }
  },
  {
    path: "/500",
    name: "500",
    component: () => import("@/components/ErrorMessage/500.vue"),
    meta: { title: "服务器错误" }
  },
  {
    path: "/:pathMatch(.*)*",
    redirect: "/404"
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes: staticRouter,
  strict: false,
  scrollBehavior: () => ({ left: 0, top: 0 })
})

router.beforeEach((to, from, next) => {
  NProgress.start()
  const token = localStorage.getItem("brain_token")
  if (to.path === "/login") {
    if (token) return next(from.fullPath)
    return next()
  }
  if (!token) return next({ path: "/login", replace: true })
  document.title = to.meta.title ? `${to.meta.title} - 算网大脑` : "算网大脑"
  next()
})

router.afterEach(() => {
  NProgress.done()
})

export default router
