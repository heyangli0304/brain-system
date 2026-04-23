"""
光网拓扑管理模块
数据格式严格匹配真实 ACTN 控制器返回的 ietf-te-topology 结构
10 个节点，模拟韶关/广州/深圳/东莞/佛山等粤港澳大湾区 DC 互联
"""
from typing import Dict, Any, List, Optional

PROVIDER_ID = 5555
CLIENT_ID = 6666
TOPOLOGY_ID = 100
UNDERLAY_TOPO_ID = 33
NETWORK_ID = f"providerId-{PROVIDER_ID}-clientId-{CLIENT_ID}-topologyId-{TOPOLOGY_ID}"
UNDERLAY_REF = f"providerId-{PROVIDER_ID}-clientId-{CLIENT_ID}-topologyId-{UNDERLAY_TOPO_ID}"

NODE_DEFS = [
    {"node-id": "10.10.10.1", "name": "SG-DC-1",  "label": "ShaoGuan-DC-1"},
    {"node-id": "10.10.10.2", "name": "SG-DC-2",  "label": "ShaoGuan-DC-2"},
    {"node-id": "10.10.10.3", "name": "GZ-DC-1",  "label": "GuangZhou-DC-1"},
    {"node-id": "10.10.10.4", "name": "GZ-DC-2",  "label": "GuangZhou-DC-2"},
    {"node-id": "10.10.10.5", "name": "SZ-DC-1",  "label": "ShenZhen-DC-1"},
    {"node-id": "10.10.10.6", "name": "SZ-DC-2",  "label": "ShenZhen-DC-2"},
    {"node-id": "10.10.10.7", "name": "DG-DC-1",  "label": "DongGuan-DC-1"},
    {"node-id": "10.10.10.8", "name": "FS-DC-1",  "label": "FoShan-DC-1"},
    {"node-id": "10.10.10.9", "name": "ZH-DC-1",  "label": "ZhuHai-DC-1"},
    {"node-id": "10.10.10.10","name": "HZ-DC-1",  "label": "HuiZhou-DC-1"},
]

LINK_DEFS = [
    {"src": "10.10.10.1", "dst": "10.10.10.3", "src-tp": "1",  "dst-tp": "1",  "bw": "1000000", "odu": ["ODU0","ODU1","ODU2","ODU3","ODU4","ODUFlex"]},
    {"src": "10.10.10.1", "dst": "10.10.10.7", "src-tp": "2",  "dst-tp": "1",  "bw": "1000000", "odu": ["ODU0","ODU1","ODU2","ODU3","ODU4","ODUFlex"]},
    {"src": "10.10.10.2", "dst": "10.10.10.4", "src-tp": "1",  "dst-tp": "1",  "bw": "1000000", "odu": ["ODU0","ODU1","ODU2","ODU3","ODU4","ODUFlex"]},
    {"src": "10.10.10.2", "dst": "10.10.10.8", "src-tp": "2",  "dst-tp": "1",  "bw": "400000",  "odu": ["ODU0","ODU1","ODU2","ODU3"]},
    {"src": "10.10.10.3", "dst": "10.10.10.4", "src-tp": "2",  "dst-tp": "2",  "bw": "1000000", "odu": ["ODU0","ODU1","ODU2","ODU3","ODU4","ODUFlex"]},
    {"src": "10.10.10.3", "dst": "10.10.10.5", "src-tp": "3",  "dst-tp": "1",  "bw": "1000000", "odu": ["ODU0","ODU1","ODU2","ODU3","ODU4","ODUFlex"]},
    {"src": "10.10.10.3", "dst": "10.10.10.7", "src-tp": "4",  "dst-tp": "2",  "bw": "400000",  "odu": ["ODU0","ODU1","ODU2","ODU3"]},
    {"src": "10.10.10.4", "dst": "10.10.10.6", "src-tp": "3",  "dst-tp": "1",  "bw": "1000000", "odu": ["ODU0","ODU1","ODU2","ODU3","ODU4","ODUFlex"]},
    {"src": "10.10.10.4", "dst": "10.10.10.8", "src-tp": "4",  "dst-tp": "2",  "bw": "400000",  "odu": ["ODU0","ODU1","ODU2","ODU3"]},
    {"src": "10.10.10.5", "dst": "10.10.10.6", "src-tp": "2",  "dst-tp": "2",  "bw": "1000000", "odu": ["ODU0","ODU1","ODU2","ODU3","ODU4","ODUFlex"]},
    {"src": "10.10.10.5", "dst": "10.10.10.9", "src-tp": "3",  "dst-tp": "1",  "bw": "400000",  "odu": ["ODU0","ODU1","ODU2","ODU3"]},
    {"src": "10.10.10.6", "dst": "10.10.10.10","src-tp": "3",  "dst-tp": "1",  "bw": "400000",  "odu": ["ODU0","ODU1","ODU2","ODU3"]},
    {"src": "10.10.10.7", "dst": "10.10.10.8", "src-tp": "3",  "dst-tp": "3",  "bw": "400000",  "odu": ["ODU0","ODU1","ODU2","ODU3"]},
    {"src": "10.10.10.8", "dst": "10.10.10.9", "src-tp": "4",  "dst-tp": "2",  "bw": "400000",  "odu": ["ODU0","ODU1","ODU2","ODU3"]},
    {"src": "10.10.10.9", "dst": "10.10.10.10","src-tp": "3",  "dst-tp": "2",  "bw": "400000",  "odu": ["ODU0","ODU1","ODU2","ODU3"]},
    {"src": "10.10.10.1", "dst": "10.10.10.2", "src-tp": "3",  "dst-tp": "3",  "bw": "1000000", "odu": ["ODU0","ODU1","ODU2","ODU3","ODU4","ODUFlex"]},
    {"src": "10.10.10.5", "dst": "10.10.10.10","src-tp": "4",  "dst-tp": "3",  "bw": "400000",  "odu": ["ODU0","ODU1","ODU2","ODU3"]},
    {"src": "10.10.10.3", "dst": "10.10.10.8", "src-tp": "5",  "dst-tp": "5",  "bw": "400000",  "odu": ["ODU0","ODU1","ODU2","ODU3"]},
]

ODU_RESOURCE_MAP = {
    "1000000": [
        {"odu-type": "ODU0", "available-count": 10, "bandwidth": "1.25G"},
        {"odu-type": "ODU1", "available-count": 8,  "bandwidth": "2.5G"},
        {"odu-type": "ODU2", "available-count": 4,  "bandwidth": "10G"},
        {"odu-type": "ODU3", "available-count": 2,  "bandwidth": "40G"},
        {"odu-type": "ODU4", "available-count": 1,  "bandwidth": "100G"},
        {"odu-type": "ODUFlex", "available-count": 8, "bandwidth": "flex"}
    ],
    "400000": [
        {"odu-type": "ODU0", "available-count": 6, "bandwidth": "1.25G"},
        {"odu-type": "ODU1", "available-count": 4, "bandwidth": "2.5G"},
        {"odu-type": "ODU2", "available-count": 2, "bandwidth": "10G"},
        {"odu-type": "ODU3", "available-count": 1, "bandwidth": "40G"}
    ]
}


def _build_tp(tp_id: str, node_ref: str, tp_ref: str, slot: int, port: int) -> Dict:
    return {
        "supporting-termination-point": [
            {"network-ref": UNDERLAY_REF, "node-ref": node_ref, "tp-ref": tp_ref}
        ],
        "ietf-eth-te-topology:svc": {
            "client-facing": True,
            "supported-classification": {"transparent": True}
        },
        "ietf-te-topology:te": {
            "admin-status": "up",
            "interface-switching-capability": [
                {
                    "encoding": "ietf-te-types:lsp-encoding-oduk",
                    "max-lsp-bandwidth": [{"priority": 7, "te-bandwidth": {"ietf-otn-topology:odu-type": "ietf-otn-types:prot-ODU4"}}],
                    "switching-capability": "ietf-te-types:switching-otn"
                }
            ],
            "name": f"PhysicalInfo{{rack-id=0, shelf-id=0, subcard-id=0, slot-id={slot}, port-id={port}}}",
            "oper-status": "up",
            "physical-info": {"port-id": port, "rack-id": 0, "shelf-id": 0, "slot-id": slot, "subcard-id": 0}
        },
        "ietf-te-topology:te-tp-id": int(tp_id),
        "tp-id": tp_id
    }


def _build_node(ndef: Dict, tp_list: List[Dict]) -> Dict:
    return {
        "node-id": ndef["node-id"],
        "ietf-te-topology:te": {
            "oper-status": "up",
            "te-node-attributes": {
                "admin-status": "up",
                "is-abstract": "null",
                "name": ndef["name"],
                "underlay-topology": {"network-ref": UNDERLAY_REF}
            }
        },
        "ietf-te-topology:te-node-id": ndef["node-id"],
        "ietf-network-topology:termination-point": tp_list
    }


def _build_link(ldef: Dict, idx: int) -> Dict:
    link_id = f"teNodeId-{ldef['src']}-teTpId-{ldef['src-tp']}"
    return {
        "link-id": link_id,
        "source": {"source-node": ldef["src"], "source-tp": ldef["src-tp"]},
        "destination": {"dest-node": ldef["dst"], "dest-tp": ldef["dst-tp"]},
        "supporting-link": [
            {"link-ref": f"teNodeId-{ldef['src']}-teTpId-{ldef['src-tp']}", "network-ref": UNDERLAY_REF}
        ],
        "ietf-te-topology:te": {
            "oper-status": "up",
            "te-link-attributes": {
                "access-type": "point-to-point",
                "admin-status": "up",
                "max-link-bandwidth": {
                    "te-bandwidth": {"ietf-otn-topology:odu-type": "ietf-otn-types:prot-ODU4"}
                },
                "name": link_id,
                "unreserved-bandwidth": [
                    {"priority": 7, "te-bandwidth": {"ietf-otn-topology:odu-type": "ietf-otn-types:prot-ODU4"}}
                ]
            }
        }
    }


def _build_topology() -> Dict:
    node_map = {n["node-id"]: n for n in NODE_DEFS}
    tp_counter = {}

    for n in NODE_DEFS:
        tp_counter[n["node-id"]] = 100000

    node_tps = {n["node-id"]: [] for n in NODE_DEFS}

    for ldef in LINK_DEFS:
        src, dst = ldef["src"], ldef["dst"]
        src_tp_id = ldef["src-tp"]
        dst_tp_id = ldef["dst-tp"]
        slot = (hash(src + src_tp_id) % 15) + 1
        port = (hash(dst + dst_tp_id) % 20) + 1

        node_ref = f"0.{hash(src) % 256}.{hash(src_tp_id) % 256}.{(hash(src) // 256) % 256}"
        tp_ref = str(tp_counter[src])
        tp_counter[src] += 1
        node_tps[src].append(_build_tp(src_tp_id, node_ref, tp_ref, slot, port))

        node_ref2 = f"0.{hash(dst) % 256}.{hash(dst_tp_id) % 256}.{(hash(dst) // 256) % 256}"
        tp_ref2 = str(tp_counter[dst])
        tp_counter[dst] += 1
        node_tps[dst].append(_build_tp(dst_tp_id, node_ref2, tp_ref2, slot + 1, port + 1))

    nodes = [_build_node(ndef, node_tps[ndef["node-id"]]) for ndef in NODE_DEFS]
    links = [_build_link(ldef, i) for i, ldef in enumerate(LINK_DEFS)]

    return {
        "ietf-network:networks": {
            "network": [{
                "ietf-te-topology:client-id": CLIENT_ID,
                "ietf-te-topology:provider-id": PROVIDER_ID,
                "ietf-te-topology:te-topology-id": NETWORK_ID,
                "network-id": NETWORK_ID,
                "network-types": {
                    "ietf-te-topology:te-topology": {
                        "ietf-otn-topology:otn-topology": {}
                    }
                },
                "node": nodes,
                "ietf-network-topology:link": links
            }]
        }
    }


MOCK_TOPOLOGY = _build_topology()

SIMPLIFIED_NODES = [
    {"node-id": n["node-id"], "name": n["name"], "label": n["label"]}
    for n in NODE_DEFS
]

SIMPLIFIED_LINKS = [
    {
        "link-id": f"teNodeId-{l['src']}-teTpId-{l['src-tp']}",
        "source-node": l["src"], "source-tp": l["src-tp"],
        "dest-node": l["dst"], "dest-tp": l["dst-tp"],
        "max-bandwidth": l["bw"],
        "support-odu": l["odu"]
    }
    for l in LINK_DEFS
]


def _find_adjacent_links(node_id: str) -> List[Dict]:
    result = []
    for l in LINK_DEFS:
        if l["src"] == node_id or l["dst"] == node_id:
            result.append(l)
    return result


def precompute_path(source_node: str, dest_node: str, odu_type: str = None) -> List[Dict]:
    results = []
    visited = set()

    def dfs(current: str, path_nodes: List[str], path_links: List[Dict], total_delay: int):
        if current == dest_node:
            all_odu = set()
            for pl in path_links:
                for o in pl["odu"]:
                    all_odu.add(o)
            if odu_type:
                odu_short = odu_type.split(":")[-1].replace("prot-", "")
                if odu_short not in all_odu:
                    return
            path_id = f"PATH-{'-'.join(path_nodes)}"
            results.append({
                "path-id": path_id,
                "node-list": list(path_nodes),
                "hop-count": len(path_nodes),
                "delay": total_delay,
                "link-id-list": [f"teNodeId-{pl['src']}-teTpId-{pl['src-tp']}" for pl in path_links],
                "support-odu": sorted(list(all_odu))
            })
            return

        for link in _find_adjacent_links(current):
            next_node = link["dst"] if link["src"] == current else link["src"]
            if next_node in visited:
                continue
            if len(path_nodes) >= 5:
                continue
            visited.add(next_node)
            dfs(next_node, path_nodes + [next_node], path_links + [link], total_delay + 500)
            visited.discard(next_node)

    visited.add(source_node)
    dfs(source_node, [source_node], [], 0)
    results.sort(key=lambda p: p["delay"])
    return results[:10]


def get_odu_resource_for_link(link_id: str) -> List[Dict]:
    for l in LINK_DEFS:
        lid = f"teNodeId-{l['src']}-teTpId-{l['src-tp']}"
        if lid == link_id:
            return ODU_RESOURCE_MAP.get(l["bw"], [])
    return []


def get_topology() -> Dict:
    return MOCK_TOPOLOGY


def get_simplified_topology() -> Dict:
    return {
        "network-id": NETWORK_ID,
        "provider-id": PROVIDER_ID,
        "client-id": CLIENT_ID,
        "te-topology-id": NETWORK_ID,
        "nodes": SIMPLIFIED_NODES,
        "links": SIMPLIFIED_LINKS
    }
