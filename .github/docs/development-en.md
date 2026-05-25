### Backend

```bash
make install
cp .env.example .env
uv run python -m axionara.main
```

后端默认监听：

```text
http://localhost:8080
```

后端 API 前缀默认为 `/api/v1`，本地 API 文档地址为：

```text
http://localhost:8080/docs
```

### Frontend

```bash
cd web
npm install
npm run dev
```

前端开发环境变量示例见 [web/.env.example](web/.env.example)：

```env
VITE_WEB_PORT=8000
VITE_API_BASE_URL=http://localhost:8080
```

开发模式下，Vite 会把 `/api` 请求代理到 `VITE_API_BASE_URL`。部署模式下，`VITE_API_BASE_URL` 通常设置为 `/`，由 Nginx 将 `/api/...` 转发给后端。

### Development Commands

```bash
poe run          # 启动后端服务
poe test         # 运行测试
poe check        # 运行格式化、lint、类型检查和 pre-commit
poe check-test   # 运行 check 后再运行测试
make deploy      # 使用 docker compose 构建并启动
make down        # 停止 docker compose 服务
```
