# 🔐 我的私人 Clash 自动化手册 (Kenny 专属)

这份文档针对你的 **DMIT 1Gbps+ 服务器** 和 **IPRoyal 住宅服务** 定制。

---

## 🏗️ 你的基础设施
- **主力 VPS**: DMIT (建议作为 Subconverter 后端 IP)。
- **核心节点**: 
  - `DMIT_HK`: 低延迟，适合日常。
  - `JP-IIJ`: 适合日本特定服务。
- **住宅 IP**: IPRoyal Socks5 (用于 Claude/ChatGPT 防封)。

---

## 🔄 你的专属更新流程

### 1. 节点变动了怎么办？
当你从 DMIT 或者其他地方拿到新链接：
1. 打开 [我的控制面板](https://kenny-bbdog.github.io/clash-for-anything/)。
2. 粘贴新链接。
3. **关键点**：在右侧“落地转发节点”中，选一个带 `DMIT` 字样的节点。
   - *原因：住宅 IP 比较慢，用 DMIT 1Gbps 的带宽做跳板转发，可以极大提升 AI 的响应速度。*

### 2. 下个月更换 IPRoyal 账户时：
1. 别去改代码，直接在网页右侧的 **🏠 住宅 IP 模块** 填入新的 `Host:Port` 和 `User:Pass`。
2. 输入你的 DMIT VPS IP（用于在线订阅）。
3. 点击 **复制在线订阅链接**。
4. 在 Clash Verge 中找到你的订阅，右键 -> **更新**。

### 3. 性能深度优化 (你的专属设置)
你的 VPS 线路极好，如果发现下载不够快，登录 VPS 运行：
```bash
# 再次运行 setup.sh
bash <(curl -Ls https://raw.githubusercontent.com/Kenny-BBDog/clash-for-anything/main/vps-setup/setup.sh)
```
选 `[2]` 优化 BBR。我已经把缓冲区针对 1Gbps 调到了极限。

---

## 🚫 风险提示
- **不要把此文件 git add/push 到 GitHub**：它包含了你的操作偏好。
- **规则生效确认**：在桌面端 Clash 的“日志”里，看到 `Rule: AI-Application -> 住宅IP` 字样，说明防封号机制正在生效。

---
**Status: 已完成现代化改造 | 环境: Windows + Android 双端同步**
