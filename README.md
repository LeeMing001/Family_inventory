# 家庭物资管理系统

一个支持多用户的家庭物资管理系统，2-5人可以共享同一个房间，管理家庭物资。

## 功能特性

- ✅ 用户注册和登录
- ✅ 房间管理（创建房间、加入房间）
- ✅ 分区管理（一级分区和二级分区）
- ✅ 物品管理（添加、修改、删除、查看）
- ✅ 多用户协作（2-5人共享房间）
- ✅ 退出登录

## 技术栈

- **前端**: Vue 3 + TypeScript + Vite + Vue Router + Pinia + Axios
- **后端**: Python + FastAPI + SQLAlchemy + SQLite
- **认证**: JWT (JSON Web Token)

## 项目结构

```
family-inventory-system/
├── src/                          # 前端源码
│   ├── api/                      # API 调用
│   ├── components/               # 组件
│   ├── router/                   # 路由配置
│   ├── stores/                   # 状态管理
│   ├── views/                    # 页面视图
│   ├── App.vue                   # 根组件
│   └── main.ts                   # 入口文件
├── backend/                      # 后端源码
│   ├── models/                   # 数据库模型
│   ├── routers/                  # API 路由
│   ├── main.py                   # FastAPI 应用入口
│   ├── database.py               # 数据库配置
│   ├── auth.py                   # 认证逻辑
│   └── schemas.py                # Pydantic 模型
├── index.html                    # HTML 模板
├── package.json                  # 前端依赖
├── vite.config.ts                # Vite 配置
└── tsconfig.json                 # TypeScript 配置
```

## 使用说明

### 1. 启动服务

```bash
# 开发环境（同时启动前端和后端）
pnpm dev

# 或者分别启动
# 后端
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 5001

# 前端
pnpm dev --port 5000 --host
```

服务启动后：
- 前端访问: http://localhost:5000
- 后端 API: http://localhost:5001
- API 文档: http://localhost:5001/docs

### 2. 用户注册/登录

首次使用需要注册账号：
1. 访问 http://localhost:5000
2. 点击"注册"标签
3. 输入用户名和密码
4. 点击注册按钮

已有账号直接登录即可。

### 3. 创建房间

1. 登录后进入"我的房间"页面
2. 点击"创建房间"按钮
3. 输入房间名称和最大成员数（2-5人）
4. 点击创建

### 4. 加入房间

如果已有房间，可以通过邀请码加入：
1. 在"我的房间"页面点击"加入房间"按钮
2. 输入6位邀请码
3. 点击加入

### 5. 管理分区

1. 进入房间后，点击"创建分区"按钮创建一级分区
2. 点击分区旁边的"添加子分区"可以创建二级分区

### 6. 管理物品

1. 点击"添加物品"按钮
2. 填写物品名称、描述、数量，选择所属分区
3. 可以对已添加的物品进行编辑和删除

### 7. 退出登录

点击右上角的"退出登录"按钮即可退出当前账号。

## API 接口

### 认证接口

- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户登出
- `GET /api/auth/me` - 获取当前用户信息

### 房间接口

- `POST /api/rooms` - 创建房间
- `POST /api/rooms/join` - 加入房间
- `GET /api/rooms` - 获取我的房间列表
- `GET /api/rooms/{room_id}` - 获取房间详情
- `GET /api/rooms/{room_id}/members` - 获取房间成员列表

### 分区接口

- `POST /api/rooms/{room_id}/categories` - 创建分区
- `GET /api/rooms/{room_id}/categories` - 获取分区列表
- `GET /api/rooms/{room_id}/categories/all` - 获取所有分区及物品
- `PUT /api/rooms/{room_id}/categories/{category_id}` - 更新分区
- `DELETE /api/rooms/{room_id}/categories/{category_id}` - 删除分区

### 物品接口

- `POST /api/rooms/{room_id}/items` - 添加物品
- `GET /api/rooms/{room_id}/items` - 获取物品列表
- `GET /api/rooms/{room_id}/items/{item_id}` - 获取物品详情
- `PUT /api/rooms/{room_id}/items/{item_id}` - 更新物品
- `DELETE /api/rooms/{room_id}/items/{item_id}` - 删除物品

## 数据库

系统使用 SQLite 数据库，数据库文件位于 `backend/family_inventory.db`。

数据库模型：
- `users` - 用户表
- `rooms` - 房间表
- `room_members` - 房间成员表
- `categories` - 分区表
- `items` - 物品表

## 开发说明

### 安装依赖

```bash
# 前端依赖
pnpm install

# 后端依赖
cd backend
pip install -r requirements.txt
```

### 构建

```bash
# 构建前端
pnpm run build

# 生产环境运行
python -m uvicorn main:app --host 0.0.0.0 --port 5000
```

## 注意事项

- 房间邀请码是6位大写字母和数字组合
- 每个房间最多支持5名成员
- 删除分区前需要先删除该分区下的所有子分区和物品
- Token 有效期为 24 小时

## License

MIT
