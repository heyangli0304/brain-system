# 算网大脑 - 小白入门指南

## 一、这个项目是什么？

**算网大脑** = 光网络 + 算力 的"智能调度员"。

想象一个场景：你要在韶关的数据中心部署大模型的"P实例"（负责理解问题），在深圳的数据中心部署"D实例"（负责生成回答），两个实例之间需要一条高速光网专线连接。**算网大脑就是自动帮你完成这件事的系统**。

它的工作流程：
1. 查询光网拓扑（哪些城市之间有光纤）
2. 路径预计算（韶关到深圳有几条路？哪条最快？）
3. 创建 TE 隧道（在光网上建一条专用通道）
4. 返回 ODU 资源（告诉你这条通道有多少带宽可用）
5. 提交算力作业（在两个数据中心分别启动 P 和 D 实例）

---

## 二、代码框架（每个文件是干什么的？）

```
brain_system/                          <-- 项目根目录
|
|-- docker-compose.yml                 <-- 一键启动所有服务的配置文件
|-- test_system.py                     <-- 系统测试脚本（验证所有功能是否正常）
|
|-- network_adapter_service/           <-- 【光网适配服务】端口 8002
|   |-- main.py                        <--   服务启动入口
|   |-- requirements.txt               <--   Python 依赖包清单
|   |-- Dockerfile                     <--   Docker 打包文件
|   |-- api/
|   |   |-- actn_router.py             <--   接口路由（定义了所有光网 API）
|   |-- sdk/
|       |-- topology.py                <--   拓扑数据（10个城市的节点和链路）
|       |-- tunnel.py                  <--   TE 隧道管理（创建/查询/删除隧道）
|
|-- compute_adapter_service/           <-- 【算力适配服务】端口 8001
|   |-- main.py                        <--   服务启动入口
|   |-- requirements.txt               <--   Python 依赖包清单
|   |-- Dockerfile                     <--   Docker 打包文件
|   |-- api/
|   |   |-- compute_router.py          <--   接口路由（定义了所有算力 API）
|   |-- sdk/
|       |-- compute_sdk.py             <--   算力 Mock 数据（Token/集群/作业/监控）
|
|-- orchestrator_service/              <-- 【编排服务】端口 8080
|   |-- main.py                        <--   服务启动入口
|   |-- requirements.txt               <--   Python 依赖包清单
|   |-- Dockerfile                     <--   Docker 打包文件
|   |-- api/
|   |   |-- orchestrator_router.py     <--   北向接口（前端调用的 API）
|   |-- core/
|   |   |-- workflow.py                <--   核心工作流（P/D 分离部署全流程）
|   |-- clients/
|       |-- network_client.py          <--   光网客户端（调用光网适配服务）
|       |-- compute_client.py          <--   算力客户端（调用算力适配服务）
|
|-- api_gateway/                       <-- 【API 网关】端口 80
    |-- nginx.conf                     <--   Nginx 路由配置
    |-- index.html                     <--   系统首页
    |-- Dockerfile                     <--   Docker 打包文件
```

---

## 三、三个微服务的关系

```
前端 UI
  |
  v
编排服务 (8080)  <-- 大管家，负责协调光网和算力
  |          |
  v          v
光网适配(8002)  算力适配(8001)
  |                |
  v                v
真实光网控制器   真实算力控制器
(目前是Mock)    (目前是Mock)
```

- **编排服务**：大管家，决定"先建光网专线，再启动算力作业"
- **光网适配服务**：光网包工队，只管光网的事（查拓扑、建隧道）
- **算力适配服务**：算力包工队，只管算力的事（认证、提交作业）

---

## 四、运行步骤（手把手教你跑起来）

### 前提条件
- 已安装 Python 3.11+
- 已安装 pip

### 步骤 1：安装依赖（3 个服务各装一次）

打开 3 个终端窗口，分别执行：

**终端 1 - 光网适配服务：**
```bash
cd c:\Users\Lhy20\Desktop\brain\brain_system\network_adapter_service
pip install -r requirements.txt
```

**终端 2 - 算力适配服务：**
```bash
cd c:\Users\Lhy20\Desktop\brain\brain_system\compute_adapter_service
pip install -r requirements.txt
```

**终端 3 - 编排服务：**
```bash
cd c:\Users\Lhy20\Desktop\brain\brain_system\orchestrator_service
pip install -r requirements.txt
```

### 步骤 2：启动服务（3 个终端分别启动）

**终端 1 - 启动光网适配服务：**
```bash
cd c:\Users\Lhy20\Desktop\brain\brain_system\network_adapter_service
python -m uvicorn main:app --host 0.0.0.0 --port 8002
```
看到 `Uvicorn running on http://0.0.0.0:8002` 就成功了。

**终端 2 - 启动算力适配服务：**
```bash
cd c:\Users\Lhy20\Desktop\brain\brain_system\compute_adapter_service
python -m uvicorn main:app --host 0.0.0.0 --port 8001
```
看到 `Uvicorn running on http://0.0.0.0:8001` 就成功了。

**终端 3 - 启动编排服务：**
```bash
cd c:\Users\Lhy20\Desktop\brain\brain_system\orchestrator_service
python -m uvicorn main:app --host 0.0.0.0 --port 8080
```
看到 `Uvicorn running on http://0.0.0.0:8080` 就成功了。

### 步骤 3：运行测试

打开第 4 个终端：
```bash
cd c:\Users\Lhy20\Desktop\brain\brain_system
python test_system.py
```

看到 `Results: 11/11 passed` 就全部通过了！

### 步骤 4：查看 API 文档

在浏览器中打开：
- 编排服务：http://localhost:8080/docs
- 光网适配：http://localhost:8002/docs
- 算力适配：http://localhost:8001/docs

---

## 五、核心 API 接口说明

### 光网接口（前缀 /api/v1/actn）

| 接口 | 方法 | 功能 | 举例 |
|------|------|------|------|
| `/topology` | GET | 查询全网拓扑（真实格式） | 返回 10 个节点、18 条链路 |
| `/topology/simplified` | GET | 查询简化拓扑（前端友好） | 返回节点名和标签 |
| `/path/precompute` | POST | 路径预计算 | 韶关到深圳有 10 条路径 |
| `/te/tunnel` | POST | 创建 TE 隧道 | 返回 ODU 资源（ODU4:1个,100G） |
| `/te/tunnel/{name}` | GET | 查询隧道状态 | 隧道是 up 还是 down |
| `/te/tunnel/{name}` | DELETE | 删除隧道 | 释放 ODU 资源 |

### 算力接口（前缀 /api/v1/compute）

| 接口 | 方法 | 功能 | 举例 |
|------|------|------|------|
| `/auth/token` | POST | 获取认证 Token | 返回 compute-brain-token |
| `/resource/cluster/overview` | GET | 查询集群资源 | 韶关 8 卡可用 4，广州 8 卡可用 4 |
| `/inferjob` | POST | 提交推理作业 | 提交 proxy/prefill/decode |
| `/monitor/job/{id}` | GET | 查询作业监控 | ttft=150ms, tpot=20ms |

### 编排接口（前缀 /api/v1/orchestrator）

| 接口 | 方法 | 功能 |
|------|------|------|
| `/pd/deploy` | POST | P/D 分离部署全流程（一键部署） |
| `/pd/rollback` | POST | 全链路回滚（一键清理） |

---

## 六、10 个节点拓扑说明

```
韶关 DC-1 (10.10.10.1) ──── 广州 DC-1 (10.10.10.3) ──── 深圳 DC-1 (10.10.10.5)
    │                           │                           │
韶关 DC-2 (10.10.10.2) ──── 广州 DC-2 (10.10.10.4) ──── 深圳 DC-2 (10.10.10.6)
    │                           │                           │
东莞 DC-1 (10.10.10.7) ──── 佛山 DC-1 (10.10.10.8) ──── 珠海 DC-1 (10.10.10.9)
                                    │
                                惠州 DC-1 (10.10.10.10)
```

- 10 个节点 = 粤港澳大湾区 10 个数据中心
- 18 条链路 = 城市间的 OTN 光纤
- 100G 链路 = 主干线路（支持 ODU4/ODUFlex）
- 40G 链路 = 支线线路（支持 ODU0~ODU3）

---

## 七、P/D 分离部署全流程详解

当你调用 `POST /api/v1/orchestrator/pd/deploy` 时，系统自动执行：

```
步骤1: 路径预计算
  韶关(10.10.10.1) -> 深圳(10.10.10.5)
  找到 10 条路径，选择最小时延的：韶关->广州->深圳 (1000ms)

步骤2: 创建 TE 隧道
  在韶关->广州->深圳这条路径上建一条 OTN 专线
  隧道名称: tunnel-xxxxxxxx

步骤3: 返回 ODU 资源
  ODU0:  10 个可用, 1.25G/个
  ODU1:   8 个可用, 2.5G/个
  ODU2:   4 个可用, 10G/个
  ODU3:   2 个可用, 40G/个
  ODU4:   1 个可用, 100G/个    <-- 这就是 P/D 分离需要的 100G 带宽
  ODUFlex: 8 个可用, flex

步骤4: 获取算力 Token
  用 admin/123456 登录算力平台

步骤5: 提交 P/D 作业
  - 在韶关部署 P 实例 (prefill)
  - 在深圳部署 D 实例 (decode)
  - 在深圳部署 Proxy 实例

如果任何步骤失败 -> 自动回滚（删除已创建的隧道）
```

---

## 八、常见问题

**Q: 端口被占用怎么办？**
A: 修改 main.py 里的端口号，或者先杀掉占用端口的进程。

**Q: 数据是真实的吗？**
A: 目前是 Mock（模拟）数据。拓扑、ODU 资源、算力资源都是硬编码的。未来对接真实设备时，只需修改 sdk/ 目录下的代码。

**Q: 如何对接真实光网控制器？**
A: 修改 `network_adapter_service/sdk/topology.py` 和 `tunnel.py`，把硬编码数据替换为真实的 HTTP 请求。

**Q: 如何对接真实算力控制器？**
A: 修改 `compute_adapter_service/sdk/compute_sdk.py`，把 Mock 数据替换为真实的 API 调用。

**Q: Docker 怎么用？**
A: 安装 Docker Desktop 后，在项目根目录运行 `docker-compose up -d` 即可一键启动所有服务。

---

## 九、技术栈一览

| 技术 | 用途 |
|------|------|
| Python 3.11 | 编程语言 |
| FastAPI | Web 框架（自动生成 API 文档） |
| Uvicorn | ASGI 服务器（运行 FastAPI） |
| httpx | 异步 HTTP 客户端（服务间通信） |
| Pydantic | 数据验证（请求体校验） |
| Nginx | API 网关（路由转发） |
| Docker | 容器化部署 |
