#!/bin/bash
set -e

# 启动后端服务（后台运行）
cd /workspace/projects/family-inventory-system/backend
python -m uvicorn main:app --host 0.0.0.0 --port 5001 > /app/work/logs/bypass/backend.log 2>&1 &

# 等待后端启动
sleep 2

# 启动前端服务（前台运行）
cd /workspace/projects/family-inventory-system
exec pnpm run dev -- --port 5000 --host
