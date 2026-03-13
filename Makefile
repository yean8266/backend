# 测试运行脚本

.PHONY: test test-unit test-integration test-coverage clean

# 运行所有测试
test:
	pytest

# 只运行单元测试
test-unit:
	pytest -m unit

# 只运行集成测试
test-integration:
	pytest -m integration -v

# 生成覆盖率报告
test-coverage:
	pytest --cov=app --cov-report=html --cov-report=term

# 清理测试缓存和报告
clean:
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf __pycache__
	rm -rf tests/__pycache__
	find . -name "*.pyc" -delete
