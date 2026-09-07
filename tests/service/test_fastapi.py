import os
import sys
import pytest
from fastapi.testclient import TestClient

# 1. 🎯 导入你实现的 FastAPI 实例
# 因为 api.py 在 service 文件夹下，所以使用 service.api
from service.api import app

# 2. 创建测试客户端
client = TestClient(app)


# 3. 🧪 编写你的测试用例
def test_example_route():
    """你的第一个接口测试用例"""
    # 替换为你在 service/api.py 中写好的真实路径（例如 "/users"）
    response = client.get("/your-endpoint")
    
    # 验证状态码
    assert response.status_code == 200


# 4. 🚀 main 函数
if __name__ == "__main__":
    print("🚀 开始运行 FastAPI 接口测试...\n")

    # 🔍 核心技巧：自动将项目根目录加入 sys.path，防止找不到 service 模块
    # 当前文件在 project/tests/service/test_fastapi.py
    # 我们需要把 project/ 目录加进去
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "../../"))
    
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # 使用 pytest 自动执行本文件中的测试
    exit_code = pytest.main(["-v", __file__])

    if exit_code == 0:
        print("\n✅ 所有测试用例通过！")
    else:
        print("\n❌ 测试未能通过，请检查上方错误信息。")
