# DocMind 企业知识库智能问答系统

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.5+-42b883.svg)](https://vuejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-6.0+-3178c6.svg)](https://www.typescriptlang.org/)

> DocMind 是一款基于大语言模型（LLM）的企业知识库智能问答系统，支持多轮对话、流式输出和多模型切换。

## 目录

- [项目简介](#项目简介)
- [功能特性](#功能特性)
- [技术架构](#技术架构)
- [快速开始](#快速开始)
- [功能演示](#功能演示)
- [配置说明](#配置说明)
- [部署指南](#部署指南)
- [License](#license)
- [联系方式](#联系方式)

---

## 项目简介

DocMind 是一款 AI 驱动的企业知识库智能问答系统，采用前后端分离架构设计。后端基于 Python FastAPI 构建，前端采用 Vue3 + TypeScript 开发，支持多种大语言模型的灵活切换。

系统支持 PDF、Word 等常见文档格式的上传和解析，通过向量数据库实现语义检索，结合 LLM 生成准确答案。

## 功能特性

- **智能问答**：基于 RAG（检索增强生成）架构，结合向量检索和 LLM 生成精准答案
- **多轮对话**：支持上下文理解，实现连贯的多轮问答交互
- **流式输出**：实时流式响应，打字机效果提升用户体验
- **多模型切换**：支持 DeepSeek、智谱 GLM 等多种大语言模型
- **智能路由**：基于 LLM 意图识别自动分类问题（PERSONNEL/TECHNICAL/CHAT），精准路由到对应知识库
- **向量嵌入**：基于智谱 Embedding-3 模型实现文档向量化存储与检索
- **文档解析**：支持 PDF、DOC/DOCX 等格式文档的智能解析
- **知识库管理**：创建和管理多个知识库，便捷的文档上传功能
- **会话管理**：支持会话历史记录管理

## 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                      前端 (Vue3)                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ 知识库管理 │  │ 智能问答  │  │ 会话管理  │             │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘             │
│       │             │             │                     │
│       └─────────────┴─────────────┘                     │
│                     │                                   │
│              ┌──────┴──────┐                            │
│              │  Axios API │                            │
│              └──────┬──────┘                            │
└─────────────────────┼───────────────────────────────────┘
                      │ HTTP / WebSocket
┌─────────────────────┼───────────────────────────────────┐
│                     │       后端 (FastAPI)               │
│              ┌──────┴──────┐                            │
│              │  API Routes │                            │
│              └──────┬──────┘                            │
│       ┌────────────┼────────────┐                      │
│  ┌────┴────┐  ┌────┴────┐  ┌────┴────┐               │
│  │ LLM 接口 │  │ 向量存储 │  │ 会话管理 │               │
│  │(多模型)  │  │ (Chroma)│  │ (Redis) │               │
│  └─────────┘  └─────────┘  └─────────┘               │
└─────────────────────────────────────────────────────────┘
```

### 技术栈

**后端**
- Python 3.9+
- FastAPI - 高性能 Web 框架
- LangChain - LLM 应用开发框架
- Chroma - 向量数据库（文档向量化存储与检索）
- Redis - 会话存储（聊天历史持久化）
- **智谱 Embedding-3** - 文档向量化嵌入
- **DeepSeek Chat** - LLM 对话生成
- **Phoenix 2.0 + OpenTelemetry** - 链路追踪与可观测性

### 可观测性

项目集成了 **Phoenix 2.0** 用于 LLM 应用的可观测性监控：

- **链路追踪**：通过 OpenTelemetry 自动追踪 LangChain 调用链路
- **LangChain Instrumentor**：自动捕获 LLM 调用、检索过程等关键span
- **可视化面板**：访问 Phoenix 控制台查看追踪详情

> Phoenix 默认连接地址：`http://127.0.0.1:6006`

**前端**
- Vue 3.5+ (组合式 API)
- TypeScript 6.0+
- Vite 8.0+ - 构建工具
- Element Plus 2.x - UI 组件库
- Axios - HTTP 客户端

## 快速开始

### 环境要求

- Python 3.9+
- Node.js 18+
- Redis 服务
- LLM API Key（DeepSeek / 智谱 GLM）

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd DocMind
```

### 2. 后端配置

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.bak .env
# 编辑 .env 文件，填入你的 API Key
```

`.env` 配置文件示例：

```env
# LLM API Keys
DEEPSEEK_API_KEY=your_deepseek_api_key
ZHIPU_API_KEY=your_zhipu_api_key

# Redis 配置
REDIS_URL=redis://:password@host:port/0
SESSION_TTL=3600

# HuggingFace（可选）
HF_ENDPOINT=https://hf-mirror.com
HF_HOME=/path/to/huggingface/cache
```

### 3. 启动后端服务

```bash
cd backend
python main.py
```

后端服务默认运行在 `http://localhost:8000`

### 4. 启动前端服务

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务默认运行在 `http://localhost:5173`

### 5. 访问系统

打开浏览器访问 `http://localhost:5173`，即可开始使用 DocMind 智能问答系统。

## 功能演示

### 知识库管理

1. 创建新的知识库
2. 上传 PDF 或 Word 文档
3. 系统自动解析文档内容并存储

### 智能问答

1. 输入问题
2. LLM 意图识别（分类为 PERSONNEL/TECHNICAL/CHAT）
3. 根据意图从对应分类知识库检索相关文档片段
4. 结合历史对话上下文 + 检索结果生成答案
5. 流式返回答案并存储到会话历史

### 多轮对话

1. 基于当前会话继续提问
2. 系统从 Redis 加载历史对话记忆
3. 结合历史上下文理解问题
4. 实现连贯的多轮交互

## 配置说明

### 环境变量

| 变量名 | 说明 | 必填 |
|--------|------|------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | 是 |
| `ZHIPU_API_KEY` | 智谱 GLM API 密钥 | 是 |
| `REDIS_URL` | Redis 连接地址 | 是 |
| `SESSION_TTL` | 会话过期时间（秒） | 否 |
| `HF_ENDPOINT` | HuggingFace 镜像地址 | 否 |
| `LANGCHAIN_TRACING_V2` | 启用 LangChain 追踪 | 否 |
| `LANGCHAIN_ENDPOINT` | LangSmith API 端点 | 否 |
| `LANGCHAIN_API_KEY` | LangSmith API 密钥 | 否 |

### 支持的 LLM 模型

系统支持多种 LLM 模型的灵活切换，配置方式通过环境变量或代码中的模型选择器实现。

### 文档处理

系统使用 `RecursiveCharacterTextSplitter` 进行文档分块：

| 参数 | 值 | 说明 |
|------|-----|------|
| `chunk_size` | 500 | 每个文本块约 500 字符 |
| `chunk_overlap` | 100 | 块与块之间 100 字符重叠，保持上下文连续性 |

分块后的文档携带 `category` 元数据存储到 Chroma 向量数据库，检索时可根据分类过滤。

### 检索增强 (RAG)

系统采用**两阶段检索**策略：

**阶段 1：粗排 (向量海选)**
- 通过 Chroma 向量数据库进行相似度检索
- 初步筛选出 Top-K 个相关片段

**阶段 2：精排 (Rerank 重排)**
- 基于智谱 Rerank-3 模型进行语义重排
- 从粗排结果中精选 Top-N 个最相关的片段
- 提升检索精度，确保 LLM 获取高质量上下文

## 部署指南

### 生产环境部署

1. **后端部署**

```bash
cd backend

# 使用 uvicorn 运行（推荐使用 gunicorn）
pip install uvicorn[standard]
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

2. **前端构建**

```bash
cd frontend

# 构建生产版本
npm run build

# 构建产物在 dist 目录
```

4. **进程管理**

建议使用 systemd 或 supervisor 管理后端进程，确保服务稳定运行。

### Phoenix 可观测性

项目集成了 Phoenix 2.0 用于 LLM 应用的链路追踪：

1. **启动 Phoenix**

```bash
# 直接使用 Python 启动 Phoenix
python -m phoenix.server.main serve
```

2. **访问 Phoenix 控制台**

打开浏览器访问 `http://localhost:6006`，查看 LLM 调用链路追踪。

3. **查看追踪数据**

- LangChainInstrumentor 自动捕获 LLM 调用
- 可查看每次问答的完整调用链路
- 支持查看检索（Retrieval）和生成（Generation）过程的详细span

## License

本项目基于 [MIT License](https://opensource.org/licenses/MIT) 开源。

## 联系方式

- 提交 Issue：[GitHub Issues](https://github.com/your-repo/docmind/issues)

---

Made with ❤️ by DocMind Team
