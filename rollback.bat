@echo off
chcp 65001 >nul
REM Bonel Project - 回退脚本
REM 如果需要放弃当前修改，恢复到原始状态

echo ========================================
echo 🔄 Bonel Project 回退工具
echo ========================================
echo.

echo 当前分支: feature/bonel-votes-api
echo.
echo 可选操作:
echo   [1] 软回退 - 保留修改到 stash，切换到 main 分支
echo   [2] 硬回退 - 完全删除所有修改，恢复到 main 分支原始状态
echo   [3] 取消 - 不做任何操作
echo.

set /p choice="请选择 (1/2/3): "

if "%choice%"=="1" (
    echo.
    echo 📝 执行软回退...
    git add -A
    git stash push -m "临时保存 bonel 修改"
    git checkout main
    echo.
    echo ✅ 已切换到 main 分支
    echo 💡 你的修改已保存在 stash 中，可以随时恢复
    echo    恢复命令: git stash pop
)

if "%choice%"=="2" (
    echo.
    echo ⚠️  警告: 这将删除所有未提交的修改！
    set /p confirm="确定要继续吗? (yes/no): "
    
    if "%confirm%"=="yes" (
        git checkout main
        git branch -D feature/bonel-votes-api
        echo.
        echo ✅ 已完全回退到 main 分支
        echo 🗑️  feature/bonel-votes-api 分支已删除
    ) else (
        echo.
        echo ❌ 操作已取消
    )
)

if "%choice%"=="3" (
    echo.
    echo ❌ 操作已取消
)

echo.
echo ========================================
pause
