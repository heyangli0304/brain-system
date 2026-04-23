"""
系统部署验证脚本
检查所有必需文件和服务配置是否正确
"""
import os
import sys
from pathlib import Path

def check_file(path: str, description: str) -> bool:
    """检查文件是否存在"""
    exists = Path(path).exists()
    status = "[OK]" if exists else "[FAIL]"
    print(f"{status} {description}: {path}")
    return exists

def main():
    print("=" * 60)
    print("算网大脑系统部署验证")
    print("=" * 60)
    print()
    
    base_dir = Path(__file__).parent
    all_ok = True
    
    # 检查根目录文件
    print("根目录文件:")
    all_ok &= check_file(base_dir / "docker-compose.yml", "Docker Compose 配置")
    all_ok &= check_file(base_dir / "README.md", "项目文档")
    all_ok &= check_file(base_dir / "test_system.py", "系统测试脚本")
    print()
    
    # 检查 API 网关
    print("API 网关服务:")
    gateway_dir = base_dir / "api_gateway"
    all_ok &= check_file(gateway_dir / "Dockerfile", "网关 Dockerfile")
    all_ok &= check_file(gateway_dir / "nginx.conf", "Nginx 配置")
    all_ok &= check_file(gateway_dir / "index.html", "首页")
    print()
    
    # 检查编排服务
    print("编排服务:")
    orch_dir = base_dir / "orchestrator_service"
    all_ok &= check_file(orch_dir / "Dockerfile", "编排服务 Dockerfile")
    all_ok &= check_file(orch_dir / "main.py", "服务入口")
    all_ok &= check_file(orch_dir / "requirements.txt", "依赖配置")
    all_ok &= check_file(orch_dir / "api" / "orchestrator_router.py", "API 路由")
    all_ok &= check_file(orch_dir / "core" / "workflow.py", "核心编排逻辑")
    all_ok &= check_file(orch_dir / "clients" / "network_client.py", "光网客户端")
    all_ok &= check_file(orch_dir / "db" / "database.py", "数据库配置")
    all_ok &= check_file(orch_dir / "db" / "models.py", "数据模型")
    print()
    
    # 检查光网适配服务
    print("光网适配服务:")
    net_dir = base_dir / "network_adapter_service"
    all_ok &= check_file(net_dir / "Dockerfile", "光网服务 Dockerfile")
    all_ok &= check_file(net_dir / "main.py", "服务入口")
    all_ok &= check_file(net_dir / "requirements.txt", "依赖配置")
    all_ok &= check_file(net_dir / "api" / "internal_router.py", "API 路由")
    all_ok &= check_file(net_dir / "sdk" / "topology.py", "拓扑管理")
    all_ok &= check_file(net_dir / "sdk" / "virtual_network.py", "虚拟网络管理")
    all_ok &= check_file(net_dir / "test_network_service.py", "单元测试")
    print()
    
    # 总结
    print("=" * 60)
    if all_ok:
        print("[OK] 所有文件检查通过！系统已就绪")
        print()
        print("下一步:")
        print("  1. 运行：docker-compose up -d")
        print("  2. 访问：http://localhost")
        print("  3. 测试：python test_system.py")
    else:
        print("[FAIL] 部分文件缺失，请检查部署")
        sys.exit(1)
    print("=" * 60)

if __name__ == "__main__":
    main()
