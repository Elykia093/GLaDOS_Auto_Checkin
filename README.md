# GLaDOS Auto Checkin

自动签到GLaDOS账户并通过Telegram通知

## 功能特性

- 每日自动签到（北京时间16:00）
- 实现无限白嫖
- 账户状态查询
- Telegram通知结果
- 失败时正确标记 Actions 运行失败
- 支持配置登录浏览器 User-Agent

## 配置指南

1. Fork本仓库
2. 登录 GLaDOS 后，从浏览器开发者工具的 Network 请求中复制完整 Cookie；新版认证需要包含 `gld:sess` 和 `gld:sess.sig`
3. 添加 GitHub Actions Secrets：
   - `GLADOS_EMAIL`: 你的 GLaDOS 注册邮箱
   - `GLADOS_COOKIE`: 完整 Cookie
   - `TG_BOT_TOKEN`: Telegram Bot Token
   - `TG_CHAT_ID`: 接收通知的 Chat ID
4. 如果签到仍提示“没有权限”或设备不匹配，重新登录后更新 Cookie，并在 Settings → Secrets and variables → Actions → Variables 中设置 `GLADOS_USER_AGENT` 为该浏览器的完整 User-Agent
5. 手动触发工作流测试；签到/状态查询失败会让 Actions 显示失败
