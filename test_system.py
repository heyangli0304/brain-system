"""
算网大脑系统联调测试 - v4.0
架构重构后：编排服务（大管家）内嵌光网/算力适配器，统一 8080 端口
核心流程：路径预计算 -> 选择路径 -> 创建TE隧道 -> 获取ODU资源 -> 提交P/D作业
"""
import requests
import time

ORCHESTRATOR_URL = "http://localhost:8080"


def wait_for_service(url, name, timeout=30):
    print(f"waiting {name}...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(f"{url}/health", timeout=3)
            if r.status_code == 200:
                print(f"[OK] {name} ready")
                return True
        except Exception:
            pass
        time.sleep(1)
    print(f"[FAIL] {name} timeout")
    return False


def test_topology():
    print("\n" + "=" * 60)
    print("Test 1: GET /api/v1/actn/topology (ietf-te-topology)")
    print("=" * 60)
    r = requests.get(f"{ORCHESTRATOR_URL}/api/v1/actn/topology")
    data = r.json()
    assert data["code"] == 0
    net = data["data"]["ietf-network:networks"]["network"][0]
    nodes = net["node"]
    links = net["ietf-network-topology:link"]
    print(f"[OK] network-id: {net['network-id']}")
    print(f"[OK] nodes: {len(nodes)}, links: {len(links)}")
    for n in nodes:
        name = n["ietf-te-topology:te"]["te-node-attributes"]["name"]
        tp_count = len(n["ietf-network-topology:termination-point"])
        print(f"  - {n['node-id']} ({name}): {tp_count} TPs")
    return data


def test_simplified_topology():
    print("\n" + "=" * 60)
    print("Test 2: GET /api/v1/actn/topology/simplified")
    print("=" * 60)
    r = requests.get(f"{ORCHESTRATOR_URL}/api/v1/actn/topology/simplified")
    data = r.json()
    assert data["code"] == 0
    topo = data["data"]
    print(f"[OK] nodes: {len(topo['nodes'])}, links: {len(topo['links'])}")
    for n in topo["nodes"]:
        print(f"  - {n['node-id']} ({n['label']})")
    return data


def test_path_precompute():
    print("\n" + "=" * 60)
    print("Test 3: POST /api/v1/actn/path/precompute (SG->SZ)")
    print("=" * 60)
    r = requests.post(f"{ORCHESTRATOR_URL}/api/v1/actn/path/precompute", json={
        "request_id": "req-test-001",
        "source_node": "10.10.10.1",
        "destination_node": "10.10.10.5",
        "odu_type": "ietf-otn-types:prot-ODU4",
        "bandwidth": "100000"
    })
    data = r.json()
    assert data["code"] == 0
    paths = data["data"]["path-list"]
    print(f"[OK] path-count: {data['data']['path-count']}")
    for p in paths:
        print(f"  - {p['path-id']}: {p['node-list']}, delay={p['delay']}ms, odu={p['support-odu']}")
    return data


def test_create_tunnel():
    print("\n" + "=" * 60)
    print("Test 4: POST /api/v1/actn/te/tunnel (SG->GZ, ODU resource)")
    print("=" * 60)
    r = requests.post(f"{ORCHESTRATOR_URL}/api/v1/actn/te/tunnel", json={
        "tunnel_name": "tunnel-sg-gz-001",
        "source": "10.10.10.1",
        "destination": "10.10.10.3",
        "path_id": "PATH-10.10.10.1-10.10.10.3",
        "encoding": "ietf-te-types:lsp-encoding-oduk",
        "switching_type": "ietf-te-types:switching-otn",
        "te_bandwidth": {"ietf-otn-tunnel:odu-type": "ietf-otn-types:prot-ODU4"},
        "protection": {"enable": True, "protection-type": "bidir-1-to-1"}
    })
    data = r.json()
    assert data["code"] == 0
    tunnel = data["data"]
    print(f"[OK] tunnel-name: {tunnel['tunnel-name']}")
    print(f"[OK] provisioning-state: {tunnel['provisioning-state']}")
    print(f"[OK] odu-resource-info:")
    for odu in tunnel["odu-resource-info"]:
        print(f"  - {odu['odu-type']}: count={odu['available-count']}, bw={odu['bandwidth']}")
    return data


def test_get_tunnel():
    print("\n" + "=" * 60)
    print("Test 5: GET /api/v1/actn/te/tunnel/tunnel-sg-gz-001")
    print("=" * 60)
    r = requests.get(f"{ORCHESTRATOR_URL}/api/v1/actn/te/tunnel/tunnel-sg-gz-001")
    data = r.json()
    assert data["code"] == 0
    print(f"[OK] tunnel-name: {data['data']['tunnel-name']}, state: {data['data']['provisioning-state']}")
    return data


def test_delete_tunnel():
    print("\n" + "=" * 60)
    print("Test 6: DELETE /api/v1/actn/te/tunnel/tunnel-sg-gz-001")
    print("=" * 60)
    r = requests.delete(f"{ORCHESTRATOR_URL}/api/v1/actn/te/tunnel/tunnel-sg-gz-001")
    data = r.json()
    assert data["code"] == 0
    print(f"[OK] {data['data']['tunnel-name']}: {data['data']['status']}")
    return data


def test_compute_auth():
    print("\n" + "=" * 60)
    print("Test 7: POST /api/v1/compute/auth/token")
    print("=" * 60)
    r = requests.post(f"{ORCHESTRATOR_URL}/api/v1/compute/auth/token", json={
        "username": "admin", "password": "123456"
    })
    data = r.json()
    assert data["respCode"] == 0
    token = data["respBody"]["core-sctoken"]
    print(f"[OK] token: {token}")
    return token


def test_compute_resource(token):
    print("\n" + "=" * 60)
    print("Test 8: GET /api/v1/compute/resource/cluster/overview")
    print("=" * 60)
    r = requests.get(f"{ORCHESTRATOR_URL}/api/v1/compute/resource/cluster/overview",
                     headers={"Authorization": f"Bearer {token}"})
    data = r.json()
    assert data["respCode"] == 0
    for c in data["respBody"]["data"]:
        print(f"[OK] {c['cluster_name']}: total={c['total_card']}, available={c['card_info'][0]['card_available_count']}")
    return data


def test_compute_inferjob(token):
    print("\n" + "=" * 60)
    print("Test 9: POST /api/v1/compute/inferjob (P/D)")
    print("=" * 60)
    roles = ["proxy", "prefill", "decode"]
    job_ids = []
    for role in roles:
        r = requests.post(f"{ORCHESTRATOR_URL}/api/v1/compute/inferjob", json={
            "TaskjobName": f"pd-{role}-test",
            "ClusterName": "GuangZhou-DC-B",
            "role": role, "GpuCount": 1, "GpuType": "A100-80G", "LlmModelId": 1001
        }, headers={"Authorization": f"Bearer {token}"})
        data = r.json()
        assert data["respCode"] == 0
        job_id = data["respBody"]["jobId"]
        print(f"[OK] {role} job_id: {job_id}")
        job_ids.append(job_id)
    return job_ids


def test_compute_metrics(token, job_id):
    print("\n" + "=" * 60)
    print(f"Test 10: GET /api/v1/compute/monitor/job/{job_id}")
    print("=" * 60)
    r = requests.get(f"{ORCHESTRATOR_URL}/api/v1/compute/monitor/job/{job_id}",
                     headers={"Authorization": f"Bearer {token}"})
    data = r.json()
    assert data["respCode"] == 0
    for m in data["respBody"]["metrics"]:
        print(f"[OK] {m['metric_types']}: {m['value_current']}{m['unit']}")
    return data


def test_pd_deploy_workflow():
    print("\n" + "=" * 60)
    print("Test 11: POST /api/v1/orchestrator/pd/deploy (SG->SZ full workflow)")
    print("=" * 60)
    r = requests.post(f"{ORCHESTRATOR_URL}/api/v1/orchestrator/pd/deploy", json={
        "source_node": "10.10.10.1",
        "dest_node": "10.10.10.5",
        "odu_type": "ietf-otn-types:prot-ODU4",
        "bandwidth": "100000",
        "p_cluster": "ShaoGuan-DC-A",
        "d_cluster": "GuangZhou-DC-B"
    })
    data = r.json()
    print(f"[OK] status: {data.get('status')}")
    if data.get("steps"):
        for step, info in data["steps"].items():
            print(f"  - {step}: {info.get('status', info)}")
    if data.get("status") == "success" and data.get("steps", {}).get("tunnel_create"):
        odu_info = data["steps"]["tunnel_create"].get("odu_resource_info", [])
        print(f"  - ODU resources:")
        for odu in odu_info:
            print(f"    {odu['odu-type']}: count={odu['available-count']}, bw={odu['bandwidth']}")
    return data


def main():
    print("=" * 60)
    print("Brain System Integration Test v4.0")
    print("编排服务(大管家) + 内嵌光网/算力适配器")
    print("=" * 60)

    if not wait_for_service(ORCHESTRATOR_URL, "orchestrator"):
        print(f"\n[FAIL] orchestrator not ready, abort")
        return

    results = []

    test_topology(); results.append(True)
    test_simplified_topology(); results.append(True)
    test_path_precompute(); results.append(True)
    test_create_tunnel(); results.append(True)
    test_get_tunnel(); results.append(True)
    test_delete_tunnel(); results.append(True)

    token = test_compute_auth(); results.append(True)
    test_compute_resource(token); results.append(True)
    job_ids = test_compute_inferjob(token); results.append(True)
    test_compute_metrics(token, job_ids[0]); results.append(True)

    test_pd_deploy_workflow(); results.append(True)

    print("\n" + "=" * 60)
    print(f"Results: {sum(results)}/{len(results)} passed")
    print("=" * 60)


if __name__ == "__main__":
    main()
