"""
Bonel Project - API 测试脚本
用于测试4个接口是否正常工作
"""

import asyncio
import httpx
import sys
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000/api/v1"

async def test_health():
    """测试健康检查接口"""
    print("\n🧪 测试 /health")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health")
            data = response.json()
            assert response.status_code == 200
            assert data["status"] == "ok"
            assert "timestamp" in data
            print(f"  ✅ 通过 - 状态: {data['status']}, 时间戳: {data['timestamp']}")
            return True
    except Exception as e:
        print(f"  ❌ 失败 - {e}")
        return False

async def test_stats():
    """测试统计接口"""
    print("\n🧪 测试 /stats")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/stats")
            data = response.json()
            assert response.status_code == 200
            assert "total_nominees" in data
            assert "total_votes" in data
            print(f"  ✅ 通过 - 候选人: {data['total_nominees']}, 总票数: {data['total_votes']}")
            return True
    except Exception as e:
        print(f"  ❌ 失败 - {e}")
        return False

async def test_leaderboard():
    """测试排行榜接口"""
    print("\n🧪 测试 /leaderboard")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/leaderboard?page=1&page_size=5")
            data = response.json()
            assert response.status_code == 200
            assert "items" in data
            assert "total" in data
            print(f"  ✅ 通过 - 总数: {data['total']}, 返回条目: {len(data['items'])}")
            return True
    except Exception as e:
        print(f"  ❌ 失败 - {e}")
        return False

async def test_vote_status_without_auth():
    """测试投票状态接口（未登录）"""
    print("\n🧪 测试 /votes/status (未登录)")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/votes/status")
            # 应该返回 401
            assert response.status_code == 401
            print(f"  ✅ 通过 - 正确返回 401 未授权")
            return True
    except Exception as e:
        print(f"  ❌ 失败 - {e}")
        return False

async def test_papers():
    """测试文章列表接口"""
    print("\n🧪 测试 /papers")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/papers?sort=hot&page=1")
            data = response.json()
            assert response.status_code == 200
            assert "papers" in data
            assert "user_status" in data
            print(f"  ✅ 通过 - 文章数: {len(data['papers'])}, 用户登录: {data['user_status']['is_logged_in']}")
            return True
    except Exception as e:
        print(f"  ❌ 失败 - {e}")
        return False

async def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("🚀 Bonel Project API 测试")
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔗 测试地址: {BASE_URL}")
    print("=" * 50)
    
    tests = [
        test_health,
        test_stats,
        test_leaderboard,
        test_vote_status_without_auth,
        test_papers,
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"  ❌ 测试异常 - {e}")
            results.append(False)
    
    # 统计结果
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    if passed == total:
        print("🎉 所有测试通过！")
    else:
        print(f"⚠️  {total - passed} 个测试失败")
    print("=" * 50)
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
