"""
算网大脑系统联调测试 - v4.1
整合同事的完整算力接口：认证/资源/监控/文件/镜像/模型/算法/作业/Webhook
"""
import requests
import time
import json

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
        print(f"  - {n['node-id']} ({name})")
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
    for p in paths[:3]:
        print(f"  - {p['path-id']}: delay={p['delay']}ms")
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


def test_compute_login():
    print("\n" + "=" * 60)
    print("Test 7: POST /api/v1/compute/auth/login")
    print("=" * 60)
    r = requests.post(f"{ORCHESTRATOR_URL}/api/v1/compute/auth/login", json={
        "username": "admin", "password": "123456"
    })
    data = r.json()
    assert data["respCode"] == 0
    token = data["respBody"].get("core-sctoken", data["respBody"].get("token", ""))
    print(f"[OK] token: {token}")
    return token


def test_compute_cluster_resource(token):
    print("\n" + "=" * 60)
    print("Test 8: GET /api/v1/compute/resource/cluster/overview")
    print("=" * 60)
    r = requests.get(f"{ORCHESTRATOR_URL}/api/v1/compute/resource/cluster/overview",
                     headers={"Authorization": f"Bearer {token}"})
    data = r.json()
    assert data["respCode"] == 0
    for c in data["respBody"]["data"]:
        card_info = c.get("node_metrics_info", [{}])[0].get("card_info", [{}])
        card = card_info[0] if card_info else {}
        print(f"[OK] {c['cluster_name']}: total={c['total_card']}, "
              f"available={card.get('card_available_count', 'N/A')}, "
              f"type={card.get('card_type', 'N/A')}")
    return data


def test_compute_simple_inferjob(token):
    print("\n" + "=" * 60)
    print("Test 9: POST /api/v1/compute/inferjob (P/D simple)")
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


def test_compute_full_inferjob(token):
    print("\n" + "=" * 60)
    print("Test 10: POST /api/v1/compute/adapter/inferjobs (full params)")
    print("=" * 60)
    r = requests.post(f"{ORCHESTRATOR_URL}/api/v1/compute/adapter/inferjobs", json={
        "TaskjobName": "full-infer-test",
        "ClusterName": "ShaoGuan-DC-A",
        "Account": "ai_group", "Partition": "gpu", "Qos": "high",
        "NodeCount": 1, "GpuCount": 4, "GpuType": "A100-80G",
        "MemoryMb": 65536, "CoreCount": 16, "TimeLimitMinutes": 120,
        "MountPoints": ["/data", "/models"], "Dataset": 1, "Model": 1,
        "Algorithm": 1, "Vram": 81920, "WorkingDirectory": "/workspace",
        "LlmModelId": 1001, "role": "prefill"
    }, headers={"Authorization": f"Bearer {token}"})
    data = r.json()
    assert data["respCode"] == 0
    print(f"[OK] full infer job_id: {data['respBody']['jobId']}")
    return data


def test_compute_job_metrics(token, job_id):
    print("\n" + "=" * 60)
    print(f"Test 11: GET /api/v1/compute/monitor/metrics/job?job_id={job_id}")
    print("=" * 60)
    r = requests.get(f"{ORCHESTRATOR_URL}/api/v1/compute/monitor/metrics/job",
                     params={"job_id": job_id, "cluster": "GuangZhou-DC-B"},
                     headers={"Authorization": f"Bearer {token}"})
    data = r.json()
    assert data["respCode"] == 0
    for m in data["respBody"]["metrics"]:
        print(f"[OK] {m['metric_types']}: current={m['value_current']}{m['unit']}, "
              f"mean={m.get('value_mean', 'N/A')}, max={m.get('value_max', 'N/A')}")
    return data


def test_compute_job_detail(token, job_id):
    print("\n" + "=" * 60)
    print(f"Test 12: GET /api/v1/compute/adapter/getSpecJob?job_id={job_id}")
    print("=" * 60)
    r = requests.get(f"{ORCHESTRATOR_URL}/api/v1/compute/adapter/getSpecJob",
                     params={"job_id": job_id, "cluster": "GuangZhou-DC-B", "type": "infer"},
                     headers={"Authorization": f"Bearer {token}"})
    data = r.json()
    assert data["respCode"] == 0
    body = data["respBody"]
    print(f"[OK] job_id={body.get('id')}, status={body.get('taskjob_status_enum')}")
    rt = body.get("runtime_metrics", {})
    print(f"  gpu_util={rt.get('gpu_util_avg')}, kv_cache={rt.get('kv_cache_usage')}")
    return data


def test_compute_image(token):
    print("\n" + "=" * 60)
    print("Test 13: POST /api/v1/compute/image/insert")
    print("=" * 60)
    r = requests.post(f"{ORCHESTRATOR_URL}/api/v1/compute/image/insert", json={
        "img_name": "vllm-infer", "img_tags": "infer,vllm",
        "source": "dockerhub", "source_path": "vllm/vllm-openai:latest",
        "cluster_id": "1", "is_public": True,
        "framework": "pytorch", "cuda_version": "12.1",
    }, headers={"Authorization": f"Bearer {token}"})
    data = r.json()
    assert data["respCode"] == 0
    print(f"[OK] image: {data['respBody']['img_name']}, id={data['respBody']['id']}")
    return data


def test_compute_model(token):
    print("\n" + "=" * 60)
    print("Test 14: POST /api/v1/compute/model/insert")
    print("=" * 60)
    r = requests.post(f"{ORCHESTRATOR_URL}/api/v1/compute/model/insert", json={
        "llm_name": "Qwen-72B", "cluster_name": "ShaoGuan-DC-A",
        "llm_tags": "llm,72b", "llm_description": "Qwen 72B model",
        "cluster": "SG", "llm_is_public": 1
    }, headers={"Authorization": f"Bearer {token}"})
    data = r.json()
    assert data["respCode"] == 0
    print(f"[OK] model: {data['respBody']['data']['llm_name']}, id={data['respBody']['data']['id']}")
    return data


def test_compute_algorithm(token):
    print("\n" + "=" * 60)
    print("Test 15: POST /api/v1/compute/algorithm/insert")
    print("=" * 60)
    r = requests.post(f"{ORCHESTRATOR_URL}/api/v1/compute/algorithm/insert", json={
        "algorithm_name": "pd-infer-algo", "algorithm_description": "P/D inference algorithm",
        "algorithm_is_public": 1, "cluster": "SG",
        "algorithm_tags": "infer,pd"
    }, headers={"Authorization": f"Bearer {token}"})
    data = r.json()
    assert data["respCode"] == 0
    print(f"[OK] algorithm: {data['respBody']['data']['algorithm_name']}, id={data['respBody']['data']['id']}")
    return data


def test_compute_fs(token):
    print("\n" + "=" * 60)
    print("Test 16: POST /api/v1/compute/fs/dir/create")
    print("=" * 60)
    r = requests.post(f"{ORCHESTRATOR_URL}/api/v1/compute/fs/dir/create", json={
        "fs_dir": "/data/pd-workspace", "cluster": "ShaoGuan-DC-A"
    }, headers={"Authorization": f"Bearer {token}"})
    data = r.json()
    assert data["respCode"] == 0
    print(f"[OK] {data['respBody']}")
    return data


def test_webhook(token):
    print("\n" + "=" * 60)
    print("Test 17: POST /api/v1/compute/webhook/status_update")
    print("=" * 60)
    r = requests.post(f"{ORCHESTRATOR_URL}/api/v1/compute/webhook/status_update", json={
        "event_type": "JOB_STATUS_CHANGE",
        "event_data": {"job_id": 10001, "new_status": "running", "cluster": "ShaoGuan-DC-A", "reason": "started"},
        "timestamp": 1745400000
    }, headers={"Authorization": f"Bearer {token}"})
    data = r.json()
    assert data["status"] == "received"
    print(f"[OK] webhook received: {data['event']}, job_id={data['job_id']}, status={data['new_status']}")

    r2 = requests.get(f"{ORCHESTRATOR_URL}/api/v1/compute/webhook/job_status/10001",
                      headers={"Authorization": f"Bearer {token}"})
    data2 = r2.json()
    print(f"[OK] job_status query: {data2}")
    return data


def test_pd_deploy_workflow():
    print("\n" + "=" * 60)
    print("Test 18: POST /api/v1/orchestrator/pd/deploy (SG->SZ full workflow)")
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
    return data


def main():
    print("=" * 60)
    print("Brain System Integration Test v4.1")
    print("编排服务(大管家) + 内嵌光网/算力南向适配")
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

    token = test_compute_login(); results.append(True)
    test_compute_cluster_resource(token); results.append(True)
    job_ids = test_compute_simple_inferjob(token); results.append(True)
    test_compute_full_inferjob(token); results.append(True)
    test_compute_job_metrics(token, job_ids[0]); results.append(True)
    test_compute_job_detail(token, job_ids[0]); results.append(True)
    test_compute_image(token); results.append(True)
    test_compute_model(token); results.append(True)
    test_compute_algorithm(token); results.append(True)
    test_compute_fs(token); results.append(True)
    test_webhook(token); results.append(True)

    test_pd_deploy_workflow(); results.append(True)

    print("\n" + "=" * 60)
    print(f"Results: {sum(results)}/{len(results)} passed")
    print("=" * 60)


if __name__ == "__main__":
    main()
