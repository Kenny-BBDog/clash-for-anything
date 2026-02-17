---
name: Clash Sub Hub Management
description: Expert system for managing, debugging, and scaling Clash subscription proxies and 3x-ui backends.
---

# Clash Sub Hub Management Excellence

This skill codifies the best practices for building a robust private proxy management system, specifically focusing on the "Pool-Plan" architecture for multi-user support and the operational maintenance of 3x-ui databases.

## 核心架构：池化与方案 (Pool-Plan Architecture)

在构建高可用的订阅中心时，应遵循以下原则：

1. **节点池 (Node Pool)**：将所有源（3x-ui、节点链接、第三方订阅）作为原始资源，不直接暴露给用户。
2. **订阅方案 (Plan)**：通过 Token 进行隔离。一个方案由“名称 + 节点选择 + 过滤规则”组成。
3. **按需分发**：根据 Token 动态过滤池子中的节点，生成轻量级的 YAML。

## 故障排查手册

### 1. Clash 订阅校验失败 (Key Errors)
- **behavior 缺失**：所有 `rule-providers` 必须声明 `behavior` (classical, domain, or ipcidr)。
- **重复名称**：Clash 的 `proxies` 和 `proxy-groups` 内的 `name` 必须全局唯一。
- **缺失组引用**：`rules` 中引用的组名必须在 `proxy-groups` 中定义。

### 2. 3x-ui 数据库崩溃或报错
当 3x-ui 无法访问或重启失败时，通常是 `x-ui.db` 损坏：
- **恶意/重复 Remark**：检查 `inbounds` 表，删除带有非法字符或重复备注的行。
- **空设置**：确保 `settings` 字段为有效的 JSON，否则 Go 后端解析会 Panics。

### 3. 后端服务 (Sub Bridge) 响应截断/无限加载
当使用 Clash/代理 访问 Dashboard 时，如果出现 HTML 只加载头部、API 返回空数据或页面无限转圈 (Spinner)，通常是 **HTTP 协议完整性** 问题：
- **Content-Length 缺失**：代理软件（中间件）在转发 HTTP/1.1 时，如果没看到 `Content-Length` 且是非 chunked 传输，可能会在收到第一个 TCP 包后误判响应结束，从而掐断连接。
  - **修复**：在 `wfile.write()` 前必须计算 body 长度并 `send_header('Content-Length', str(len(body)))`。
- **缓冲区滞留**：Python 的 `wfile` 可能缓冲数据。
  - **修复**：每次 `write()` 后必须调用 `wfile.flush()`。
- **并发阻塞**：单线程 `HTTPServer` 会被长连接的 Proxy 独占。
  - **修复**：必须混入 `ThreadingMixIn`。

### 4. 静态资源加载 404
- **Favicon 报错**：浏览器默认请求 `/favicon.ico`，如果未处理会产生 404 噪音。建议返回 204 No Content。
- **网络回环**：如果 VPS 上的服务访问 127.0.0.1 异常，尝试通过公网 IP 或配置 Clash 规则绕过拦截。

## 开发规范 (Web Dashboard)
- **无依赖优先**：优先使用标准 HTML/CSS/JS 以确保极速部署和跨系统兼容。
- **UI 风格**：采用 Outfit 字体、Glassmorphism (卡片悬浮/毛玻璃) 效果，提升“高级感”。
- **多 Tab 隔离**：将基础配置、业务逻辑和访客管理解耦在不同视图中。
- **Clipboard 兼容性**：由于 `navigator.clipboard` 仅在 HTTPS 环境下工作，在私有部署（HTTP 访问）时必须提供 `textarea` 降级方案，以确保订阅链接能够点击复制。

## 常用工具脚本
- [repair_3x_ui.py](scripts/repair_3x_ui.py): 快速清理 3x-ui 数据库中的脏数据。
- [base_rules.yaml](resources/base_rules.yaml): 预置了 AI、流媒体分流逻辑的 Clash 黄金模板。
- [DEPLOYMENT_CHECKLIST.md](examples/DEPLOYMENT_CHECKLIST.md): 部署与验证的标准自检流程。
## 隐私与凭据管理 (Private Credentials)

为了安全地管理多个 VPS 的访问权限，本 Skill 支持在 `private/` 目录下存储敏感信息：

- **私有配置**：存放在 `private/vps_config.json`，用于自动化运维任务（如 `repair_3x_ui.py`）。
- **Git 忽略**：`.gitignore` 已配置为忽略所有 `private/` 目录和 `.pem` 文件，确保凭据不会被提交。

## 进阶特性：独立出口链 (Independent Egress Chaining)

为了实现不同国家/地区的节点拥有各自独立的落地 IP，系统引入了 `chains` 列表机制：

1. **多链支持**：订阅配置中不再使用单一的 `external_proxy`，而是使用 `chains` 数组，每个对象包含独立的 `server`, `port`, `dialer_name`（或 `dialer_id`）。
2. **精准分流**：
   - **按 ID 筛选**：优先匹配 `dialer_id` 确保稳定性。
   - **词缀匹配**：通过 `dialer_name` 模糊匹配（如 `DMIT` 或 `JP`）自动关联底座节点。
3. **组优先级管理**：系统自动将链式代理（landing IPs）置于 Clash 代理分组的首位，确保运营人员能够直观选择“安全通道”。
4. **GeoSite 兼容性**：优先使用 `google`, `openai`, `telegram` 等标准分类。**避免使用**非标准的 `gplay` 分类以防旧版 Clash 核心校验失败。

### 示例格式
在 `config.json` 的订阅对象中：
```json
"chains": [
  { "name": "🇺🇸 专线", "server": "...", "port": 10003, "dialer_name": "DMIT_us" },
  { "name": "🇯🇵 专线", "server": "...", "port": 10010, "dialer_name": "JP_IIJ" }
]
```

### 示例格式 (private/vps_config.json)
```json
{
  "vps": [
    { "name": "...", "ip": "...", "user": "...", "ssh_key": "..." }
  ]
}
```
