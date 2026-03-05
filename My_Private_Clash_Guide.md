# 🔐 我的私人 Clash 自动化手册 (Kenny 专属 v3.2)
  
这份文档针对你的 **DMIT 1Gbps+ 服务器** 和 **IPRoyal 住宅服务** 定制。
  
---
  
## 🏗️ 你的基础设施 (v3.2 升级版)
- **核心架构**: "Private Node Warehouse" (私人节点仓库模式)
- **主力 Hub**: DMIT VPS (既是高性能节点，也是你的私有订阅转换中心)。
- **数据隐私**: 所有节点信息只存在你的浏览器 LocalStorage 里，除了你自己的 VPS，没人知道你有哪些节点。

---
  
## 🚀 极速部署 (重装 VPS 时看这里)
  
如果你的 DMIT VPS 重装了系统，只需要执行 **这一条命令** 即可复原所有环境：
  
```bash
bash <(curl -Ls https://raw.githubusercontent.com/Kenny-BBDog/clash-for-anything/main/vps-setup/setup.sh)
```
  
**交互提示关键点**：
- 看到 `❓ 是否同时安装私有订阅转换中心 (Subconverter)? [Y/n]` 时，**直接回车** (默认 Yes)。
- 脚本跑完会给你一张大表，把里面的 `http://x.x.x.x:25500` 和 **3x-ui** 密码记下来。
  
---
  
## 🔄 你的日常操作流
  
### 1. 增量添加节点 (仓库模式)
以前你需要把所有节点存个 txt，现在不用了：
1. 打开 [我的控制面板](https://kenny-bbdog.github.io/clash-for-anything/)。
2. 有新的 DMIT 节点？直接扔进 `入库链接` 框，点 **添加**。
3. 它会自动进入下方的 **📦 我的节点仓库**。
4. **这个仓库是永久的**，哪怕你刷新页面，之前的节点也都还在。
  
### 2. 住宅 IP 换号了？
IPRoyal 的账号/密码变动时：
1. 在网页右侧 **🏠 住宅 IP 模块** 填新的。
2. 页面会自动保存你的新设置。
3. 直接点 **生成 & 复制总订阅链接**。
  
### 3. 多设备同步
你只需要维护这一份“在线订阅链接”。
- **Windows (Clash Verge)**: 右键订阅 -> 更新。
- **Android / iOS**: 下拉刷新。
- **原理**: 你的网页生成了最新的配置 -> 推送给你 VPS 上的 Subconverter -> VPS 生成最终订阅 -> 你的所有设备同步。
  
---
  
## 🛠️ 避坑指南
- **转换中心 IP (Hub IP)**: 这里永远填你的 **DMIT VPS 公网 IP**。因为你的 Subconverter 是装在那上面的。
- **端口**: 默认 **25500**，不要动。脚本已经帮你自动放行防火墙了。
- **防封验证**: 手机上开个 Claude，Clash 日志里如果显示 `Rule: AI-Application -> 住宅IP`，那就是稳的。
  
---
**状态**: ✅ 极简自动化 | ✅ IPRoyal 深度集成 | ✅ DMIT 1G 带宽跑满
