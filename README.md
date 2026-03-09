# 合同风险审核工具

AI 驱动的销售合同初审工具，支持规范格式文本输入、规则化风险审核、原文与审核结果联动展示。

## 功能特性

- 粘贴或上传 TXT：规范格式（`<!-- N -->` 段落编号）的合同文本
- 规则化管理风险要素，灵活配置审核维度
- AI Agent（智谱云端）精准定位原文、基于规则进行风险判断
- 双栏界面：左侧原文预览 + 右侧审核结果，支持 `{{id:X-Y}}` 引用跳转
- 无本地模型部署，资源占用低

## 技术栈

- **后端**: Python 3.10+ / FastAPI
- **前端**: React 18 / TypeScript / Vite
- **大模型**: 智谱AI（云端 API，无本地部署）

## 快速开始

### 1. 后端

```bash
cd /Users/hecongqin/Program/sales-contract-audit   # 先进入项目目录
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # 编辑 .env 填入智谱AI API Key
uvicorn app.main:app --reload
```

### 2. 前端（新终端）

```bash
cd frontend
npm install
npm run dev
```

### 3. 访问

- 前端: http://localhost:5173
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

开发时前端会通过 Vite 代理将 `/api` 请求转发到后端。

## 环境变量

```env
OPENAI_API_KEY=你的智谱AI-API-Key
OPENAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4
OPENAI_MODEL=glm-4-flash   # 或 glm-4、glm-4-air
```

在 [智谱AI开放平台](https://open.bigmodel.cn/) 获取 API Key。

### 合同文本格式

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
