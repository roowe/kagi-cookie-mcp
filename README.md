# Kagi Cookie MCP

这是一个基于 MCP（Model Context Protocol）的 Kagi Assistant 服务端。

项目通过浏览器 Cookie 访问 Kagi 的 `assistant/prompt` 接口，并对外提供一个 MCP 工具：

- `kagi_chat`：向 Kagi Assistant 提问

当前实现是一个做过简化的版本，只保留最核心的问答能力，默认使用 `ki_quick` 模型。

这样设计的主要动机，是给 Agent 提供一个简单、稳定、可直接调用的搜索助理。

- 不开放指定模型，是为了让 Agent 不必自己做模型选择；同时 Kagi 模型更新较快，额外做一层模型适配和策略维护，成本也更高。
- 不使用 `research`，是因为它通常意味着更高成本和更长耗时；如果要稳定支持，还需要进一步处理重试、重连、续传等更复杂的请求逻辑。

## 功能说明

### `kagi_chat`

`kagi_chat` 是项目唯一暴露的 MCP 工具，主要用于：

- 向 Kagi Assistant 发送问题
- 复用同一个会话上下文继续追问
- 通过 `new_conversation=True` 开启新话题

当前参数：

- `prompt`：用户输入的问题或指令
- `new_conversation`：是否重置当前会话，默认 `False`

### 会话行为

服务端会在内存中维护：

- `thread_id`
- `message_id`

当你继续同一话题时，会自动带上已有会话信息；当你传入 `new_conversation=True` 时，会清空这两个状态，重新开始一个新会话。

## 安装

### 环境要求

- Python 3.14 或更高版本
- 一个可用的 Kagi 账号
- 可用的 Kagi 登录 Cookie

### 安装依赖

推荐使用 `uv`：

```bash
uv sync
```

## 配置

项目通过环境变量 `KAGI_COOKIE` 读取 Cookie。

你可以在项目根目录创建 `.env` 文件：

```env
KAGI_COOKIE=你的完整_cookie
KAGI_MCP_HOST=0.0.0.0
KAGI_MCP_PORT=7001
```

其中：

- `KAGI_COOKIE` 为必填
- `KAGI_MCP_HOST` 和 `KAGI_MCP_PORT` 为可选，用于控制 MCP 服务监听地址和端口

### 如何获取 Cookie

1. 登录 [https://kagi.com](https://kagi.com)
2. 打开浏览器开发者工具
3. 进入 Network（网络）面板
4. 刷新页面
5. 找到任意发往 `kagi.com` 的请求
6. 在请求头中复制完整的 `Cookie` 字符串

注意：

- 这里需要的是完整 Cookie 字符串，不只是某一个字段
- Cookie 过期后需要重新获取

## 启动服务

```bash
uv run python kagi.py
```

如果没有设置 `KAGI_COOKIE`，服务会直接退出，不会启动。

当前代码中，MCP 服务使用：

- `streamable-http` 传输
- 默认绑定地址：`0.0.0.0`
- 默认端口：`7001`
- 可通过 `.env` 中的 `KAGI_MCP_HOST` / `KAGI_MCP_PORT` 覆盖

## 项目结构

```text
.
├── kagi.py          # 主服务与 Kagi 客户端实现
├── pyproject.toml   # 项目配置
├── uv.lock          # 依赖锁文件
└── README.md
```

## 实现说明

当前版本有这些特征：

- 默认固定使用 `ki_quick`
- 不包含多模型选择逻辑
- 不包含缓存逻辑
- 不包含 lens 参数
- 使用 `requests` 发起普通 HTTP 请求
- 从响应文本中提取 `thread.json` 和 `new_message.json`

这意味着它更偏向“简单可用”的实现，而不是完整复刻 Kagi 前端的流式协议行为。

## 注意事项

- 本项目依赖浏览器 Cookie，本质上是非官方接入方式
- Kagi 页面和接口行为变化后，可能需要同步调整代码
- 请自行评估并遵守 Kagi 的使用条款

## 许可证

本项目使用 MIT License。
