# Clash For Anything 🚀

一站式科学上网解决方案：VPS 一键部署 + VLESS 链接转 Clash 配置

[![GitHub](https://img.shields.io/badge/GitHub-Kenny--BBDog-blue?style=flat-square&logo=github)](https://github.com/Kenny-BBDog/clash-for-anything)

## ✨ 功能特性

### 🖥️ VPS 一键部署
- 自动创建 SWAP（保命内存）
- BBR + TCP 深度优化（跨海传输调优）
- 3x-ui 面板自动安装
- NextTrace 路由测试工具
- 防火墙自动配置

### 🔄 VLESS 链接转换
- 支持 VLESS / VMess / Shadowsocks 链接
- 自动生成 Clash YAML 配置
- 支持 Reality / TLS / WebSocket / gRPC
- 可合并到现有配置文件

### 📡 订阅服务（进阶）
- 自建订阅服务器
- 节点健康检查
- 自动更新配置

### 📋 路由规则模板
- 国内应用完整直连规则（微信/抖音/淘宝等）
- AI 应用强制住宅 IP（防 Claude/ChatGPT 封号）
- Google Play Store 专用规则
- 持续更新优化

---

## 🚀 快速开始

### 1. VPS 一键部署

在新服务器上执行：

```bash
bash <(curl -Ls https://raw.githubusercontent.com/Kenny-BBDog/clash-for-anything/main/vps-setup/setup.sh)
```

脚本将自动完成：
- ✅ 创建 1-2GB SWAP
- ✅ 启用 BBR 并优化 TCP 参数
- ✅ 安装必备工具（curl, socat, wget, htop, vim）
- ✅ 安装 NextTrace（路由测试）
- ✅ 安装 3x-ui 面板
- ✅ 配置防火墙

### 2. VLESS 链接转 Clash 配置

#### 方法 A: 在线转换（推荐）

```bash
# 下载转换脚本
curl -O https://raw.githubusercontent.com/Kenny-BBDog/clash-for-anything/main/clash-converter/convert.sh

# 转换链接
bash convert.sh "vless://your-link-here#节点名称"
```

#### 方法 B: Python 脚本（功能更全）

```bash
# 下载脚本
curl -O https://raw.githubusercontent.com/Kenny-BBDog/clash-for-anything/main/clash-converter/convert.py

# 转换单个链接
python convert.py "vless://xxx...#节点名称"

# 转换并保存到文件
python convert.py "vless://xxx..." -o node.yaml

# 合并到现有配置
python convert.py "vless://xxx..." -m existing_config.yaml

# 转换多个链接
python convert.py "vless://...#节点1" "vmess://...#节点2" -m config.yaml
```

### 3. 使用路由规则模板

下载最新规则模板：

```bash
curl -O https://raw.githubusercontent.com/Kenny-BBDog/clash-for-anything/main/clash-converter/templates/base-rules.yaml
```

将 `rules` 部分复制到你的 Clash 配置中。

---

## 📁 项目结构

```
clash-for-anything/
├── README.md                           # 本文件
├── vps-setup/
│   └── setup.sh                        # VPS 一键部署脚本
├── clash-converter/
│   ├── convert.py                      # Python 转换工具
│   ├── convert.sh                      # Shell 转换工具
│   ├── subscription_server.py          # 订阅服务器（进阶）
│   └── templates/
│       └── base-rules.yaml             # 路由规则模板
└── configs/
    └── (你的配置文件备份)
```

---

## 🔧 进阶功能

### 自建订阅服务

在你的服务器上运行：

```bash
# 下载订阅服务器
curl -O https://raw.githubusercontent.com/Kenny-BBDog/clash-for-anything/main/clash-converter/subscription_server.py
curl -O https://raw.githubusercontent.com/Kenny-BBDog/clash-for-anything/main/clash-converter/templates/base-rules.yaml
mkdir -p templates && mv base-rules.yaml templates/

# 启动服务
python subscription_server.py --port 8080
```

客户端订阅地址：
- Windows: `http://your-server:8080/clash/windows`
- Android: `http://your-server:8080/clash/android`

### 节点健康检查

```bash
curl http://your-server:8080/health
```

---

## 📋 路由规则说明

### 规则优先级

1. **私有网络直连** - 本地网络
2. **国内应用直连** - 微信/抖音/淘宝等 200+ 域名
3. **特殊 .cn 例外** - googleapis.cn 等被墙的 .cn 域名
4. **AI 应用住宅 IP** - Claude/ChatGPT 防封号
5. **Google 服务代理** - Play Store 等
6. **兜底规则** - 其他走代理

### AI 应用防封号

以下 AI 服务强制使用住宅 IP：
- Claude / Claude Code / Anthropic API
- ChatGPT / OpenAI API
- Antigravity / Cursor AI
- GitHub Copilot
- Gemini / Google AI

> ⚠️ 如果没有住宅 IP，请将规则中的 `住宅IP` 改为 `🚀 代理选择`

---

## 🛠️ 常见问题

### Q: 微信图片/视频加载不出来？

规则模板已包含完整的微信 CDN 域名，请更新到最新版本。

### Q: Google Play 下载卡住？

检查是否有 `googleapis.cn` 的代理规则（在 `.cn` 直连规则之前）。

### Q: 如何添加新节点到现有配置？

```bash
python convert.py "vless://新节点链接" -m 现有配置.yaml
```

---

## 📝 更新日志

### v1.0.0 (2026-01-23)
- 🎉 首次发布
- ✅ VPS 一键部署脚本
- ✅ VLESS/VMess/SS 链接转换
- ✅ 订阅服务器
- ✅ 完整路由规则模板

---

## 📄 许可证

MIT License - 随便用，记得给个 Star ⭐

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**Made with ❤️ by Kenny-BBDog**
