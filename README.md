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
- ✅ **(可选) 交互式安装私有订阅转换中心**

> 💡 **提示**：脚本执行过程中会询问是否安装 `Subconverter`，建议输入 **Y** 以解锁网页端的完整功能。

---

## 🛠️ 部署自检表 (必读)

执行完脚本后，请确认以下状态：

| 检查项 | 验证方式 | 预期结果 | 备注 |
| :--- | :--- | :--- | :--- |
| **基础环境** | 脚本末尾表格 | 状态显示为 `正常` | 包含 BBR 与 SWAP |
| **管理后台** | 浏览器访问 `http://IP:2053` | 出现 3x-ui 登录页面 | 默认账号 admin/admin |
| **转换中心** | 浏览器访问 `http://IP:25500/version` | 显示 subconverter 版本号 | 若超时请检查防火墙 |

---

## 🚀 极速上手 (傻瓜步骤)

### 第一步：节点采集
- 在你的 VPS 3x-ui 面板里创建一个入站（如 VLESS-Reality），并复制链接。
- 或者直接使用机场提供的节点链接。

### 第二步：私人仓库管理
1. 打开 [配置生成器](https://kenny-bbdog.github.io/clash-for-anything/)。
2. 将节点链接粘贴到左侧框，点 **“存入仓库”**（支持多服务器增量添加）。

### 第三步：一键生成订阅
1. 在右侧 **“转换中心 IP (VPS Hub)”** 填入你的服务器 IP。
2. 点击 **“生成并复制总订阅链接”**。
3. 导入 Clash。以后你只要在网页改了节点，Clash 里点“更新”就能同步。

---

## 💡 必知必会 (避坑指南)

- **Q: 为什么生成的链接打不开？**
  A: 99% 是因为你的 VPS 端口没开。请确保已执行 `install-subconverter.sh` 且脚本末尾显示“正常”。
- **Q: 忘记 3x-ui 密码怎么办？**
  A: 在 VPS 终端输入 `x-ui` 命令，选 `7` 修改密码，选 `6` 修改端口。
- **Q: 住宅 IP 到底怎么配置？**
  A: 代理商发你的通常是 `ip:port:user:pass`，填到网页右侧的住宅代理模块即可。AI 流量会自动走这里。

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

### 本地化“热插拔”设计 (System Advantage)

这是系统的核心优势：**下个月换 IPRoyal 账号时，不需要重启也不需要改配置文件。**

1.  **完全热插拔**：直接在网页右侧“住宅 IP 模块”里直接把旧的账号密码删掉，填入新的。
2.  **隐私保护**：你的代理账号密码**仅保存在浏览器本地 (localStorage)**。即便你 Fork 了仓库并公开，别人打开网页也看不到你的 IP 信息。
3.  **瞬间生效**：点击“生成订阅”并在客户端更新后，AI 流量会立刻无缝切换到新的住宅 IP 通道。

---

## 💡 必知必会 (避坑指南)

- **Q: 为什么生成的链接打不开？**
  A: 99% 是因为你的 VPS 端口没开。请确保已执行 `install-subconverter.sh` 且脚本末尾显示“正常”。
- **Q: 为什么生成的链接地址是 http://我的IP:25500/...？**
  A: 因为这是直接请求你 VPS 上的转换引擎，不经过任何第三方，绝对保护你的节点隐私。
- **Q: 网页里的信息刷新会丢吗？**
  A: 不会。信息保存在你浏览器的 `localStorage` 里，除非你手动清除浏览器缓存。
- **Q: AI 真的会自动走住宅 IP 吗？**
  A: 是的。只要你开启了住宅 IP 模块并选择了落地节点，系统生成的规则会自动拦截 ChatGPT/Claude 等域名并导向该通道。
- **Q: 忘记 3x-ui 密码怎么办？**
  A: 在 VPS 终端输入 `x-ui` 命令，选 `7` 修改密码，选 `6` 修改端口。
- **Q: 住宅 IP 到底怎么配置？**
  A: 代理商发你的通常是 `ip:port:user:pass`，填到网页右侧的住宅代理模块即可。AI 流量会自动走这里。
- **Q: 微信图片/视频加载不出来？**
  A: 规则已包含完整微信 CDN 域名。如仍有问题，请确保使用最新版规则。
- **Q: Google Play 下载卡住？**
  A: 检查是否有 `googleapis.cn` 的代理规则（在 `.cn` 直连规则之前）。
- **Q: 如何更新路由规则？**
  A: 重新使用在线工具生成配置，或下载最新的 `base-rules.yaml`。


### 方法二：命令行工具 (可选)

```bash
# 下载转换脚本 & 规则模板
curl -O https://raw.githubusercontent.com/Kenny-BBDog/clash-for-anything/main/clash-converter/convert.py

# 转换链接
python convert.py "vless://..." -o config.yaml
```

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
