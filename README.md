# 算网大脑调度系统（Brain System）v3.0

基于 ACTN 标准的光网络+算力协同调度系统。编排服务作为**大管家/算网中枢**，内嵌光网南向适配和算力南向适配，统一管控和调度算力与光网络资源。

核心流程：**路径预计算 → 选择路径 → 创建TE隧道 → 获取ODUk资源 → 提交P/D推理作业**

## 系统架构

```
                        外部调用方
                           |
                    API Gateway (Nginx:80)
                    统一入口，只代理编排服务
                           |
              ┌────────────┼────────────┐
              |            |            |
     /api/orchestrator  /api/actn  /api/compute
              |            |            |
              └────────────┼────────────┘
                           |
              ┌────────────────────────────┐
              │   编排服务 Orchestrator     │  ← 大管家 / 算网中枢
              │         (8080)             │
              │                            │
              │  ┌──── 南向适配层 ────┐    │
              │  │                    │    │
              │  │  光网适配(ACTN)    │    │  ← 编排服务管控下的子模块
              │  │  - 拓扑查询        │    │     不对外暴露
              │  │  - 路径预计算      │    │
              │  │  - TE隧道+ODU资源  │    │
              │  │                    │    │
              │  │  算力适配(Compute)  │    │
              │  │  - 认证Token       │    │
              │  │  - 集群资源        │    │
              │  │  - 推理作业        │    │
              │  │  - 性能监控        │    │
              │  └────────────────────┘    │
              │                            │
              │  编排核心                   │
              │  - P/D分离部署工作流       │
              │  - 全链路回滚              │
              └────────────────────────────┘
```

**架构要点：编排服务是管控和收集算力与光网络的大管家，不是和二者并排的关系。**

## 服务清单

| 服务 | 端口 | 说明 | 对外暴露 |
|------|------|------|---------|
| **api-gateway** | 80 | Nginx 网关，统一入口 | ✅ |
| **orchestrator** | 8080 | 编排服务（大管家），内嵌光网+算力适配 | ✅ |
| 光网适配 | - | ACTN 标准光网南向适配（编排内部模块） | ❌ |
| 算力适配 | - | 算力北向接口南向适配（编排内部模块） | ❌ |

## 核心流程

### 1. 光网调度：路径预计算 → TE隧道 → ODU资源

```
1. GET    /api/v1/actn/topology              → 查询拓扑（10节点18链路）
2. GET    /api/v1/actn/topology/simplified    → 简化拓扑（前端友好）
3. POST   /api/v1/actn/path/precompute       → 路径预计算，返回多条可选路径
4. POST   /api/v1/actn/te/tunnel             → 创建TE隧道，返回ODU资源
5. GET    /api/v1/actn/te/tunnel/{name}      → 查询隧道状态
6. DELETE /api/v1/actn/te/tunnel/{name}      → 删除隧道
```

### 2. 算力调度：认证 → 资源 → 作业 → 监控

```
1. POST /api/v1/compute/auth/token               → 获取Token
2. GET  /api/v1/compute/resource/cluster/overview → 查询集群资源
3. POST /api/v1/compute/inferjob                  → 提交推理作业(proxy/prefill/decode)
4. GET  /api/v1/compute/monitor/job/{jobId}       → 查询作业监控
```

### 3. P/D分离部署全流程（一键编排）

```
POST /api/v1/orchestrator/pd/deploy
→ 路径预计算 → 选择最优路径(最小时延) → 创建TE隧道 → 获取ODU资源 → 提交P/D作业
```

## 接口规范

### 光网接口 - 响应格式：`{code, message, data}`

#### 拓扑查询
- **GET** `/api/v1/actn/topology`
- 响应：`{code:0, message:"success", data:{ietf-network:networks:{network:[{node, link}]}}}`

#### 简化拓扑
- **GET** `/api/v1/actn/topology/simplified`
- 响应：`{code:0, data:{network-id, nodes:[{node-id, name, label}], links:[...]}}`

#### 路径预计算
- **POST** `/api/v1/actn/path/precompute`
- 请求：`{request_id, source_node, destination_node, odu_type, bandwidth}`
- 响应：`{code:0, data:{path-count, path-list:[{path-id, node-list, delay, support-odu}]}}`

#### 创建TE隧道（核心：返回ODU资源）
- **POST** `/api/v1/actn/te/tunnel`
- 请求：`{tunnel_name, source, destination, path_id, encoding, switching_type, te_bandwidth, protection}`
- 响应：`{code:0, data:{tunnel-name, provisioning-state:"up", odu-resource-info:[{odu-type, available-count, bandwidth}]}}`

#### 查询/删除TE隧道
- **GET** `/api/v1/actn/te/tunnel/{tunnel-name}`
- **DELETE** `/api/v1/actn/te/tunnel/{tunnel-name}`

### 算力接口 - 响应格式：`{respCode, respMessage, respBody}`

#### 认证
- **POST** `/api/v1/compute/auth/token`
- 请求：`{username, password}`
- 响应：`{respCode:0, respBody:{core-sctoken}}`

#### 集群资源
- **GET** `/api/v1/compute/resource/cluster/overview`
- Header：`Authorization: Bearer {token}`
- 响应：`{respCode:0, respBody:{data:[{cluster_name, total_card, card_info}]}}`

#### 推理作业
- **POST** `/api/v1/compute/inferjob`
- 请求：`{TaskjobName, ClusterName, role, GpuCount, GpuType, LlmModelId}`
- 响应：`{respCode:0, respBody:{jobId}}`

#### 作业监控
- **GET** `/api/v1/compute/monitor/job/{jobId}`
- 响应：`{respCode:0, respBody:{jobId, metrics:[{metric_types, value_current, unit}]}}`

## 快速启动

### 方式一：本地开发（推荐新手）

```bash
# 只需启动一个服务！编排服务内嵌了所有适配器
cd orchestrator_service
pip install -r requirements.txt
python main.py
```

服务启动后访问 http://localhost:8080/docs 查看 API 文档

### 方式二：Docker Compose

```bash
docker-compose up -d
```

### 运行测试

```bash
cd brain_system
python test_system.py
```

## 测试结果

```
Brain System Integration Test v4.0
编排服务(大管家) + 内嵌光网/算力适配器

Test 1:  GET  /api/v1/actn/topology           [OK] 10 nodes, 18 links
Test 2:  GET  /api/v1/actn/topology/simplified [OK] 10 nodes, 18 links
Test 3:  POST /api/v1/actn/path/precompute     [OK] path-count: 10
Test 4:  POST /api/v1/actn/te/tunnel           [OK] ODU0:10, ODU4:1, ODUFlex:8
Test 5:  GET  /api/v1/actn/te/tunnel/{name}    [OK] state: up
Test 6:  DELETE /api/v1/actn/te/tunnel/{name}  [OK] deleted
Test 7:  POST /api/v1/compute/auth/token       [OK] token acquired
Test 8:  GET  /api/v1/compute/resource/...     [OK] 2 clusters
Test 9:  POST /api/v1/compute/inferjob         [OK] proxy/prefill/decode
Test 10: GET  /api/v1/compute/monitor/job/...  [OK] ttft=150ms, tpot=20ms
Test 11: POST /api/v1/orchestrator/pd/deploy   [OK] full workflow success
Results: 11/11 passed
```

## 目录结构

```
brain_system/
├── docker-compose.yml              # Docker 编排（编排服务 + 网关）
├── test_system.py                  # 系统联调测试（11个用例）
├── start.bat                       # Windows 快速启动脚本
├── stop.bat                        # Windows 停止脚本
├── api_gateway/                    # API 网关（Nginx）
│   ├── Dockerfile
│   ├── nginx.conf                  # 只代理编排服务
│   └── index.html                  # 系统首页
└── orchestrator_service/           # 【核心】编排服务（大管家/算网中枢）
    ├── Dockerfile
    ├── requirements.txt
    ├── main.py                     # 统一入口，注册所有路由
    ├── api/
    │   └── orchestrator_router.py  # 北向接口（编排核心API）
    ├── core/
    │   └── workflow.py             # P/D分离部署工作流
    ├── clients/
    │   ├── network_client.py       # 光网客户端（本地调用SDK）
    │   └── compute_client.py       # 算力客户端（本地调用SDK）
    ├── adapters/                   # 南向适配层（编排服务管控下的子模块）
    │   ├── network/                # 光网南向适配（ACTN标准）
    │   │   ├── api/
    │   │   │   └── actn_router.py  # 光网接口路由
    │   │   └── sdk/
    │   │       ├── topology.py     # 拓扑管理（10节点18链路）
    │   │       └── tunnel.py       # TE隧道+ODU资源管理
    │   └── compute/                # 算力南向适配（北向接口规范）
    │       ├── api/
    │       │   └── compute_router.py # 算力接口路由
    │       └── sdk/
    │           └── compute_sdk.py  # 认证/资源/作业/监控
    └── db/                         # 数据库（预留）
```

## 核心函数清单

### 光网适配（adapters/network/sdk/）
| 函数 | 功能 | 对应规范 |
|------|------|---------|
| `get_topology()` | 查询ietf-te-topology格式拓扑 | ACTN 模块1 |
| `get_simplified_topology()` | 简化拓扑（前端友好） | ACTN 模块1 |
| `precompute_path()` | DFS路径预计算，返回多条路径 | ACTN 模块2 |
| `TETunnelManager.create_tunnel()` | 创建TE隧道+返回ODU资源 | ACTN 模块3 |
| `TETunnelManager.get_tunnel()` | 查询隧道状态 | ACTN 模块3 |
| `TETunnelManager.delete_tunnel()` | 删除隧道 | ACTN 模块3 |

### 算力适配（adapters/compute/sdk/）
| 函数 | 功能 | 对应规范 |
|------|------|---------|
| `get_token()` | 获取认证Token | 算力 模块1 |
| `get_cluster_resource()` | 查询集群资源概览 | 算力 模块2 |
| `submit_infer_job()` | 提交推理作业(P/D) | 算力 模块3 |
| `get_job_metrics()` | 查询作业监控指标 | 算力 模块4 |

### 编排核心（core/）
| 函数 | 功能 |
|------|------|
| `PDWorkflow.pd_deploy_workflow()` | P/D分离部署全流程（5步编排） |
| `PDWorkflow.full_rollback()` | 全链路回滚 |

## 拓扑节点

10个节点模拟粤港澳大湾区DC互联：

| 节点ID | 名称 | 位置 |
|--------|------|------|
| 10.10.10.1 | SG-DC-1 | 韶关 |
| 10.10.10.2 | SG-DC-2 | 韶关 |
| 10.10.10.3 | GZ-DC-1 | 广州 |
| 10.10.10.4 | GZ-DC-2 | 广州 |
| 10.10.10.5 | SZ-DC-1 | 深圳 |
| 10.10.10.6 | SZ-DC-2 | 深圳 |
| 10.10.10.7 | DG-DC-1 | 东莞 |
| 10.10.10.8 | FS-DC-1 | 佛山 |
| 10.10.10.9 | ZH-DC-1 | 珠海 |
| 10.10.10.10 | HZ-DC-1 | 惠州 |

## API 文档

- 编排服务（统一入口）：http://localhost:8080/docs
- 系统首页（Nginx）：http://localhost

## 技术栈

- **后端**：FastAPI + Uvicorn
- **网关**：Nginx
- **容器化**：Docker + Docker Compose
- **光网标准**：ACTN (ietf-te-topology / ietf-otn-topology)
- **算力标准**：算力网络北向接口规范
