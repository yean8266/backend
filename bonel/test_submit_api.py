"""
Bonel Project - 提交论文接口测试脚本
用于本地联调测试 POST /api/nominees 接口

⚠️ 前置条件：
1. 本地 FastAPI 服务已启动：
   cd D:\work\hku\创业\backend\backend\bonel
   python -m bonel.main
   
2. 已安装 requests 库：
   pip install requests

3. 当前目录下存在 dummy.pdf 文件（可以是任意 PDF，用于测试文件上传）
   如果没有，可以创建一个空 PDF：
   - Windows: 右键 -> 新建 -> 文本文档，重命名为 dummy.pdf
   - 或者使用 Python: 
     from fpdf import FPDF
     pdf = FPDF()
     pdf.add_page()
     pdf.set_font('Arial', 'B', 16)
     pdf.cell(40, 10, 'Test PDF for Bonel Project')
     pdf.output('dummy.pdf')

4. 已获取有效的 JWT Token（从 Supabase 登录后获取）
   - 在前端登录后，从浏览器 DevTools -> Application -> Local Storage 中复制 access_token
   - 或使用 Supabase Dashboard 生成测试 Token

使用方法：
    python test_submit_api.py
"""

import requests
import json
import os
from pathlib import Path

# ==================== 配置区域 ====================

# 本地服务地址
BASE_URL = "http://127.0.0.1:8000"
ENDPOINT = "/api/v1/nominees"

# ⚠️ 请替换为有效的 JWT Token
# 格式：从 Supabase 登录后获取的 access_token
JWT_TOKEN = "eyJhbGciOiJFUzI1NiIsImtpZCI6ImU5OTBlMWVjLTNhMjctNDUxZS1hYjFlLTkwMWJhYWM1NWZhYiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL3B3bWVveHZpeG1sdHN5cWxxbW5qLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiI3OTU0ZGZiOC02M2IzLTRkMWYtYjllNy1iN2RmNDZjNTdkOTkiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzczNDkwOTg1LCJpYXQiOjE3NzM0ODczODUsImVtYWlsIjoiMTM3NjQzMzM3MDhAMTYzLmNvbSIsInBob25lIjoiIiwiYXBwX21ldGFkYXRhIjp7InByb3ZpZGVyIjoiZ2l0aHViIiwicHJvdmlkZXJzIjpbImdpdGh1YiJdfSwidXNlcl9tZXRhZGF0YSI6eyJhdmF0YXJfdXJsIjoiaHR0cHM6Ly9hdmF0YXJzLmdpdGh1YnVzZXJjb250ZW50LmNvbS91LzEyNjQ0MjgwND92PTQiLCJlbWFpbCI6IjEzNzY0MzMzNzA4QDE2My5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6Ly9hcGkuZ2l0aHViLmNvbSIsInBob25lX3ZlcmlmaWVkIjpmYWxzZSwicHJlZmVycmVkX3VzZXJuYW1lIjoidW5hdmFpbGFibGVkYXZpZCIsInByb3ZpZGVyX2lkIjoiMTI2NDQyODA0Iiwic3ViIjoiMTI2NDQyODA0IiwidXNlcl9uYW1lIjoidW5hdmFpbGFibGVkYXZpZCJ9LCJyb2xlIjoiYXV0aGVudGljYXRlZCIsImFhbCI6ImFhbDEiLCJhbXIiOlt7Im1ldGhvZCI6Im9hdXRoIiwidGltZXN0YW1wIjoxNzczNDA0NDM2fV0sInNlc3Npb25faWQiOiJlNjk1MWVlYy04NzRkLTQzYjctOTI3ZS1kNmVhYzdiYjM4OGYiLCJpc19hbm9ueW1vdXMiOmZhbHNlfQ.Tapxxomf74dMS-wUg4BOEqBli5VCgopgw6La6MWDODSWsNEHWVMKIGs7VtfUuSMs9eidd0UFoc-UcoRzlTHEPQ"

# 测试数据 - 契合"贝诺尔奖"调性的灾难论文
TEST_DATA = {
    "title": "基于深度学习的无人机自主炸机系统",
    "author": "佚名研究员",
    "contact": "crash.test@bonel-awards.org",
    "abstract": """
本研究提出了一种创新的无人机"智能"坠毁方案。通过将YOLOv11目标检测模型
与随机数生成器相结合，我们的系统能够在复杂环境中精准识别"最不该撞的物体"，
并以99.7%的成功率完成撞击。实验结果表明，该系统在以下场景表现优异：
- 婚礼现场：优先锁定新娘
- 机场附近：专挑引擎进气口
- 高压线区域：自动寻找最细的电线

本研究为无人机"最后一程"提供了全新的技术路径，有望申请"贝诺尔终身成就奖"。
""".strip(),
    "link": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # 可选的外部证据链接
}

# 测试文件路径（相对于脚本所在目录）
PDF_FILE = "dummy.pdf"

# ==================== 测试脚本 ====================

def check_prerequisites():
    """检查前置条件"""
    # 检查 Token 是否已配置
    if JWT_TOKEN == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...":
        print("❌ 错误：请先在脚本中配置有效的 JWT_TOKEN")
        print("   提示：从前端登录后的 Local Storage 中复制 access_token")
        return False
    
    # 检查 PDF 文件是否存在
    pdf_path = Path(__file__).parent / PDF_FILE
    if not pdf_path.exists():
        print(f"❌ 错误：找不到测试文件 {PDF_FILE}")
        print(f"   期望路径: {pdf_path.absolute()}")
        print("   提示：请在脚本同目录下创建一个 dummy.pdf 文件")
        return False
    
    print(f"✅ 前置条件检查通过")
    print(f"   - Token 已配置: {JWT_TOKEN[:20]}...")
    print(f"   - 测试文件存在: {pdf_path.absolute()}")
    print(f"   - 目标接口: {BASE_URL}{ENDPOINT}")
    return True


def test_submit_nominee():
    """测试提交论文接口"""
    
    url = f"{BASE_URL}{ENDPOINT}"
    
    # 构造请求头
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}"
        # 注意：使用 requests 的 files 参数时，不需要手动设置 Content-Type
        # requests 会自动设置 multipart/form-data 并生成 boundary
    }
    
    # 构造表单数据
    # 注意：requests 会自动处理 FormData 编码
    data = {
        "title": TEST_DATA["title"],
        "author": TEST_DATA["author"],
        "contact": TEST_DATA["contact"],
        "abstract": TEST_DATA["abstract"],
        "link": TEST_DATA["link"]
    }
    
    # 构造文件数据
    pdf_path = Path(__file__).parent / PDF_FILE
    files = {
        # key: (filename, file_object, content_type)
        "file": (PDF_FILE, open(pdf_path, "rb"), "application/pdf")
    }
    
    print("\n" + "=" * 60)
    print("🚀 开始测试提交论文接口")
    print("=" * 60)
    print(f"\n📤 请求信息:")
    print(f"   URL: {url}")
    print(f"   Method: POST")
    print(f"   Headers: {json.dumps({k: v[:30] + '...' if len(v) > 30 else v for k, v in headers.items()}, indent=6, ensure_ascii=False)}")
    print(f"\n📝 表单数据:")
    for key, value in data.items():
        preview = value[:50] + "..." if len(value) > 50 else value
        print(f"   {key}: {preview}")
    print(f"\n📎 文件数据:")
    print(f"   file: {PDF_FILE} ({pdf_path.stat().st_size} bytes)")
    
    try:
        # 发送 POST 请求
        response = requests.post(
            url,
            headers=headers,
            data=data,
            files=files,
            timeout=30  # 设置超时时间（文件上传可能需要较长时间）
        )
        
        print("\n" + "=" * 60)
        print("📥 响应结果")
        print("=" * 60)
        print(f"\n✅ HTTP 状态码: {response.status_code}")
        
        # 尝试解析 JSON 响应
        try:
            response_data = response.json()
            print(f"\n📄 响应 JSON:")
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
            
            # 根据状态码判断结果
            if response.status_code == 201:
                print("\n🎉 测试成功！论文提交成功")
                print(f"   论文 ID: {response_data.get('id', 'N/A')}")
                print(f"   消息: {response_data.get('message', 'N/A')}")
            elif response.status_code == 401:
                print("\n⚠️ 鉴权失败 - Token 无效或已过期")
                print("   请重新获取 JWT Token")
            elif response.status_code == 400:
                print("\n⚠️ 请求参数错误")
                print(f"   详情: {response_data.get('detail', 'N/A')}")
            else:
                print(f"\n⚠️ 意外响应 (状态码: {response.status_code})")
                
        except json.JSONDecodeError:
            # 响应不是 JSON 格式
            print(f"\n⚠️ 响应不是 JSON 格式:")
            print(response.text[:500])  # 只打印前500字符
            
    except requests.exceptions.ConnectionError as e:
        print("\n❌ 连接错误")
        print(f"   无法连接到 {BASE_URL}")
        print(f"   请确保 FastAPI 服务已启动: python -m bonel.main")
        print(f"   错误详情: {e}")
        
    except requests.exceptions.Timeout:
        print("\n❌ 请求超时")
        print(f"   服务器在 {30} 秒内未响应")
        print("   可能原因：文件太大、服务器处理慢、或网络问题")
        
    except Exception as e:
        print("\n❌ 请求异常")
        print(f"   错误类型: {type(e).__name__}")
        print(f"   错误详情: {e}")
        
    finally:
        # 关闭文件句柄
        files["file"][1].close()
        print("\n" + "=" * 60)
        print("🏁 测试结束")
        print("=" * 60)


def test_without_file():
    """测试不带文件的提交（纯文本）"""
    
    url = f"{BASE_URL}{ENDPOINT}"
    
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}"
    }
    
    data = {
        "title": "【纯文本测试】没有PDF的论文提交",
        "author": "测试用户",
        "contact": "test@example.com",
        "abstract": "这是一个不带 PDF 文件的测试提交，验证接口在文件可选情况下的表现。",
        # link 是可选的，这里不提交
    }
    
    print("\n" + "=" * 60)
    print("🚀 开始测试【纯文本提交】（不带 PDF）")
    print("=" * 60)
    
    try:
        response = requests.post(
            url,
            headers=headers,
            data=data,
            timeout=10
        )
        
        print(f"\n✅ HTTP 状态码: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"\n📄 响应 JSON:")
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            print(f"\n⚠️ 响应内容:\n{response.text[:500]}")
            
    except Exception as e:
        print(f"\n❌ 请求失败: {e}")


if __name__ == "__main__":
    # 检查前置条件
    if not check_prerequisites():
        exit(1)
    
    # 测试带文件的提交
    test_submit_nominee()
    
    # 测试不带文件的提交（可选）
    # 取消下面这行的注释来测试纯文本提交
    # test_without_file()
