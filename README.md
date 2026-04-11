# 合同风险审核工具

AI 驱动的销售合同初审工具，支持规范格式文本输入、规则化风险审核、原文与审核结果联动展示。

## 功能特性

- 粘贴或上传 TXT / Markdown（`.md`）：规范格式（`<!-- N -->` 段落编号）的合同文本
- 规则化管理风险要素，灵活配置审核维度
- AI Agent：通过企业提供的 **OpenAI 兼容接口** 调用 **正泰私有化 DeepSeek**，按规则完成风险判断与原文定位
- 双栏界面：左侧原文预览 + 右侧审核结果，支持 `{{id:X-Y}}` 引用跳转
- 无本地模型部署，资源占用低

## 技术栈

- **后端**: Python 3.10+ / FastAPI
- **前端**: React 19 / TypeScript / Vite 7
- **大模型**: 正泰 `ai-model.chint.com`（DeepSeek，OpenAI 兼容 HTTP API；密钥与地址见环境变量）

## 快速开始

**请先在终端进入本仓库根目录**（包含 `backend`、`frontend` 的那一层）。若在用户主目录 `~` 下直接执行 `cd backend` 会报错 `no such file or directory`。

```bash
cd /path/to/sales-contract-audit   # 换成你本机克隆路径，例如 ~/Program/AIContractAudit/sales-contract-audit
```

### 1. 后端

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # 编辑 .env，填入正泰 AI 相关配置
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

若需被本机其他进程访问（例如内网穿透），请使用 `--host 0.0.0.0`。

### 2. 前端（新终端）

同样先 `cd` 到仓库根目录，再执行：

```bash
cd frontend
npm install
npm run dev
```

### 3. 访问

项目配置了 `base: '/sales-contract-audit/'`，开发地址为：

- 前端: http://localhost:5173/sales-contract-audit/
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

开发模式下，Vite 将 `/api` 代理到 `http://localhost:8000`（见 `frontend/vite.config.ts`）。

## 环境变量

### 后端 `backend/.env`

与 `backend/.env.example` 一致，核心项如下：

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxx
OPENAI_BASE_URL=https://ai-model.chint.com/api
OPENAI_MODEL=deepseek-v3
```

大模型调用方式（OpenAI 官方 SDK + `base_url`）请勿随意变更，需与正泰侧约定保持一致。

### 前端 `frontend/.env*`（可选）

见 `frontend/.env.example`。

| 变量 | 说明 |
|------|------|
| `VITE_API_BASE` | 后端 API 根地址，**不要**末尾斜杠。本地开发可留空，此时走 Vite 代理、与开发服务器同源。 |

生产构建或「公网静态页 + 远程后端」时，将 `VITE_API_BASE` 设为后端的完整 HTTPS 根地址（例如内网穿透或正式域名）。

## 给业务同事做联调 / 演示

### 方式 A：公网前端 + 本机后端（仅演示）

1. 本机启动后端（建议 `--host 0.0.0.0`），并用 **Cloudflare Tunnel、ngrok** 等将本机端口映射为 **HTTPS** 公网地址。
2. 复制 `frontend/.env.example` 为 `.env.production.local`，设置 `VITE_API_BASE=https://你的穿透域名`（无路径、无末尾 `/`）。
3. 在 `frontend` 执行 `npm run build`，将 `dist/` 部署到任意静态托管，把前端 URL 发给同事。
4. **本机需保持开机**，且穿透进程与 `uvicorn` 持续运行。穿透域名若变化，需重新构建前端并重新部署。

### 方式 B：前后端同在一台云主机

将构建产物与 FastAPI 一并部署（如火山引擎 ECS、其他云厂商轻量服务器），配置域名与 HTTPS；后端环境变量仍使用正泰接口，并确保服务器能访问 `https://ai-model.chint.com`（若对方有 IP 白名单需提前登记出口 IP）。

## 合同文本格式

文本需包含段落编号，格式示例：

```
<!-- 1 --> 产品采购合同（一体机）
<!-- 2 --> 合同编号：2114000011297
<!-- 3 --> 采购方（以下简称需方）：xxx
```

## 项目结构

```
sales-contract-audit/
├── backend/           # FastAPI 后端
│   ├── app/
│   │   ├── main.py
│   │   ├── routers/
│   │   ├── services/
│   │   └── models/
│   └── requirements.txt
├── frontend/          # React 前端
│   └── src/
│       ├── components/
│       └── api/
└── README.md
```
