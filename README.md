# Clash For Anything 🚀

一站式科学上网解决方案：**傻瓜式配置生成** + VPS 一键部署

[![GitHub](https://img.shields.io/badge/GitHub-Kenny--BBDog-blue?style=flat-square&logo=github)](https://github.com/Kenny-BBDog/clash-for-anything)
[![GitHub Pages](https://img.shields.io/badge/在线工具-访问-green?style=flat-square)](https://kenny-bbdog.github.io/clash-for-anything/)

---

## 🎯 核心功能

### 1️⃣ 在线配置生成器（推荐）

**完全傻瓜式操作**，打开网页 → 粘贴链接 → 下载配置

🔗 **在线地址**: [https://kenny-bbdog.github.io/clash-for-anything/](https://kenny-bbdog.github.io/clash-for-anything/)

特点：
- ✅ **私人节点仓库 (Warehouse)**：节点永久保存，增量添加，不再需要每次寻找旧链接
- ✅ **全协议支持**：一键生成适用于 **Clash, Shadowrocket, Quantumult X, Surge** 的聚合订阅链接
- ✅ **转换中心 IP (VPS Hub)**：利用你私有的 VPS 引擎进行云端转换，安全且便携
- ✅ **双模式输出**：支持“云端订阅”（一键同步）与“本地文件下载”（离线备份）
- ✅ **住宅 IP (SOCKS5)**：完美集成住宅代理，AI 流量自动分流。
- ✅ **极简扁平 UI**：完全弃用花哨动效，回归纯粹的工业化工具体验。

### 2️⃣ VPS 一键部署

新服务器一条命令完成所有配置：

```bash
bash <(curl -Ls https://raw.githubusercontent.com/Kenny-BBDog/clash-for-anything/main/vps-setup/setup.sh)
```

自动完成：
- ✅ 创建 SWAP（保命内存）
- ✅ 启用 BBR + TCP 深度优化
- ✅ 自动安装工具并配置防火墙
- ✅ 自动安装 3x-ui 面板 (MHSanaei 版)
- ✅ 自动安装 NextTrace 路由测试工具

---

### 3️⃣ (推荐) 私有订阅中心安装
为了配合网页端的“私人仓库”功能实现全自动同步，建议在上述 VPS 上额外执行：

```bash
bash <(curl -Ls https://raw.githubusercontent.com/Kenny-BBDog/clash-for-anything/main/vps-setup/install-subconverter.sh)
```
- ✅ 一键开启私有 Subconverter 服务
- ✅ 自动配置 Systemd 守护进程
- ✅ 自动放行 25500 转换端口

---

## 🚀 快速开始

### 方法一：在线工具（最简单）

1. 打开 [在线配置生成器](https://kenny-bbdog.github.io/clash-for-anything/)
2. 在左侧粘贴节点链接，点击 **“存入我的私人仓库”**
3. （可选）配置住宅代理（SOCKS5）
4. 在右侧输入你的 **转换中心 IP (VPS Hub)** 
   *(需确保已执行上述第 3 步安装命令)*
5. 点击 **“生成并复制总订阅链接”**
6. 在 Clash 软件中新增订阅，粘贴链接即可！

### 方法二：命令行工具

```bash
# 下载转换脚本
curl -O https://raw.githubusercontent.com/Kenny-BBDog/clash-for-anything/main/clash-converter/convert.py

# 转换链接
python convert.py "vless://..." -o config.yaml

# 合并到现有配置
python convert.py "vless://..." -m existing_config.yaml
```

---

## 🏠 住宅 IP 配置说明

### 为什么需要住宅 IP？

Claude、ChatGPT 等 AI 服务会检测 IP 类型。
- **机房 IP** → 经常导致 403 或封号。
- **住宅 IP** → 模拟真实用户，极地封号风险（95% 以上防封成功率）。

### 本地化“热插拔”设计

在我们的在线工具中：
1. **完全热插拔**：你可以随时切换 IPRoyal、Oxylabs 或其他任何 Socks5 住宅代理。
2. **隐私保护**：你的代理账号密码**仅保存在浏览器本地 (localStorage)**。即便你 Fork 了仓库并公开，别人也看不到你的 IP 信息。
3. **傻瓜操作**：一旦在本地配置好，以后每次打开网页只需粘贴 VLESS 链接即可，“扔进去就出配置”。

---

## 📋 路由规则说明

生成的配置包含精心优化的路由规则：

| 规则类别 | 目标 | 数量 |
|---------|------|------|
| 国内应用直连 | 微信/抖音/淘宝/B站等 | 200+ 域名 |
| AI 应用住宅 IP | Claude/ChatGPT/Cursor 等 | 50+ 域名 |
| 特殊 .cn 例外 | googleapis.cn 等 | 10+ 域名 |
| Google 服务 | YouTube/Play Store 等 | 30+ 域名 |

规则持续更新，欢迎提 Issue 反馈！

---

## 📁 项目结构

```
clash-for-anything/
├── index.html                          # 🌐 在线配置生成器
├── README.md                           # 📖 本文件
├── vps-setup/
│   └── setup.sh                        # 🖥️ VPS 一键部署脚本
├── clash-converter/
│   ├── convert.py                      # 🐍 Python 转换工具
│   ├── convert.sh                      # 🐚 Shell 转换工具
│   ├── subscription_server.py          # 📡 订阅服务器
│   └── templates/
│       └── base-rules.yaml             # 📋 完整路由规则模板
└── configs/
    ├── DMIT_Local.yaml                 # 💾 Windows 配置示例
    └── DMIT_Android.yaml               # 💾 Android 配置示例
```

---

## ⚙️ 开启 GitHub Pages

如果你 Fork 了本项目，需要手动开启 Pages：

1. 进入仓库 Settings
2. 左侧菜单选择 Pages
3. Source 选择 "Deploy from a branch"
4. Branch 选择 "main"，文件夹选择 "/ (root)"
5. 点击 Save
6. 等待几分钟，访问 `https://你的用户名.github.io/clash-for-anything/`

---

## 🛠️ 常见问题

### Q: 微信图片/视频加载不出来？

规则已包含完整微信 CDN 域名。如仍有问题，请确保使用最新版规则。

### Q: Google Play 下载卡住？

检查是否有 `googleapis.cn` 的代理规则（在 `.cn` 直连规则之前）。

### Q: 如何更新路由规则？

重新使用在线工具生成配置，或下载最新的 `base-rules.yaml`。

---

## 📝 更新日志

### v3.1.0 (2026-01-23)
- 📦 **核心重构：私人节点仓库模式**。支持节点增量添加、可视化管理及永久保存。
- 🌍 **全协议适配**：一键导出为 Clash, Shadowrocket, Quantumult X, Surge, V2Ray 等多种订阅格式。
- 🎨 **UI 深度重塑**：改用极简扁平化现代设计，大幅提升操作效率。
- ⚙️ **逻辑链路优化**：明确“转换中心 IP”与“节点服务器 IP”的区别，支持 IP 自动提取。

### v1.2.0 (2026-01-23)
- 🚀 **私有订阅生成器**：VPS 脚本集成 Subconverter 引擎，支持云端自动同步。
- ✅ 路由规则升级为动态云端模式。

### v1.1.0 (2026-01-23)
- 🎉 新增在线配置生成器（纯前端）
- ✅ 支持住宅 IP 热插拔配置
- ✅ 改进傻瓜式操作体验

### v1.0.0 (2026-01-23)
- 🎉 首次发布
- ✅ VPS 一键部署脚本
- ✅ VLESS/VMess/SS 链接转换
- ✅ 完整路由规则模板

---

## 📄 许可证

MIT License - 随便用，记得给个 Star ⭐

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

特别欢迎：
- 新增国内应用域名规则
- 优化 AI 服务防封号策略
- 改进用户体验

---

**Made with ❤️ by Kenny-BBDog**
