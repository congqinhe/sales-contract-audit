# 合同风险审核工具

AI 驱动的销售合同初审工具，支持规范格式文本输入、规则化风险审核、原文与审核结果联动展示。

**当前版本仅支持在本机部署，用于开发与功能验证。** 未提供生产环境或公网部署说明。

## 功能特性

- 粘贴或上传 TXT / Markdown（`.md`）：规范格式（`<!-- N -->` 段落编号）的合同文本
- 规则化管理风险要素，灵活配置审核维度
- AI Agent：通过 **OpenAI 兼容 HTTP API** 调用大模型，按规则完成风险判断与原文定位
- 双栏界面：左侧原文预览 + 右侧审核结果，支持 `{{id:X-Y}}` 引用跳转
- 无本地模型部署，资源占用低

## 技术栈

- **后端**: Python 3.10+ / FastAPI
- **前端**: React 19 / TypeScript / Vite 7
- **大模型**: OpenAI 兼容接口（密钥、地址、模型名由环境变量配置，见下文）

## 快速开始

在终端进入本仓库根目录（包含 `backend`、`frontend` 的那一层）：

```bash
cd /path/to/sales-contract-audit
```

### 1. 后端

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env # 按「环境变量」一节编辑 .env
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 2. 前端（新终端）

```bash
cd frontend
npm install
npm run dev
```

### 3. 访问

项目 `base` 为 `/sales-contract-audit/`，本地开发地址：

- 前端: http://localhost:5173/sales-contract-audit/
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

开发模式下，Vite 将 `/api` 代理到 `http://localhost:8000`（见 `frontend/vite.config.ts`）。

## 环境变量

从仓库内的 `.env.example` 复制为 `.env` 后按需填写。

### 后端 `backend/.env`

| 变量 | 说明 |
|------|------|
| `OPENAI_API_KEY` | 大模型 API 密钥（OpenAI 兼容接口） |
| `OPENAI_BASE_URL` | 接口根地址，需带路径前缀（如厂商要求 `/api` 则一并写入） |
| `OPENAI_MODEL` | 模型名称，与网关或厂商文档一致 |
| `AUDIT_CHUNK_SIZE` | 可选。长合同按段落切片审核时，每段包含的段落数上限；不设则默认 `300` |
| `AUDIT_CHUNK_OVERLAP` | 可选。相邻切片重叠段落数，利于跨段条款；不设则默认 `10` |

示例（占位值请替换为实际配置）：

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxx
OPENAI_BASE_URL=https://example.com/api
OPENAI_MODEL=deepseek-v3
# AUDIT_CHUNK_SIZE=300
# AUDIT_CHUNK_OVERLAP=10
```

### 前端 `frontend/.env`（可选）

本地联调后端时一般**不需要**创建该文件：留空即走 Vite 代理，请求会转到本机 `8000` 端口。

| 变量 | 说明 |
|------|------|
| `VITE_API_BASE` | 后端 API 根地址，**不要**末尾 `/`。仅当需要把前端指向非默认代理地址时设置；本地开发通常不设置 |

详见 `frontend/.env.example`。

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
