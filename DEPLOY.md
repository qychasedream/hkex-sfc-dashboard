# 免费实时更新方案说明

本项目提供 **两种完全免费的实时更新方案**，按推荐顺序排列：

---

## 方案一：GitHub Actions 高频定时更新（推荐，零成本）

### 原理
- 使用 GitHub Actions 每 15 分钟自动运行一次 `src/update_data.py`
- 抓取 SFC / HKEX 官方数据后自动提交到仓库
- 前端页面打开时自动刷新 JSON（带时间戳防缓存），显示最新数据

### 已配置
文件：`.github/workflows/daily-update.yml`

```yaml
schedule:
  - cron: '*/15 * * * *'
```

### 优点
- 完全免费（public 仓库 GitHub Actions 无限制）
- 无需额外服务器
- 数据最多延迟 15 分钟

### 限制
- 不是严格意义上的"打开页面瞬间抓取"，而是"打开页面获取最近 15 分钟内已抓取的数据"

---

## 方案二：Render 免费后端 + 打开页面触发抓取

### 原理
- 部署 `backend.py` 到 Render.com 免费 Web Service
- 页面打开时调用 `https://your-service.onrender.com/api/refresh`
- 后端执行 Python 抓取脚本，更新数据并推送到 GitHub
- 前端轮询状态，完成后自动重新加载最新数据

### 部署步骤

1. **Fork / 推送本仓库到 GitHub**

2. **注册 Render**（免费）：https://render.com

3. **在 Render 创建 Web Service**
   - 选择本仓库
   - 选择 Python 环境
   - Render 会自动识别 `render.yaml`

4. **设置环境变量**
   - `GH_TOKEN`：GitHub Personal Access Token（需要 `repo` 权限，用于后端推送数据）
   - `GIT_USER_NAME`：默认 `github-actions[bot]`
   - `GIT_USER_EMAIL`：默认 `github-actions[bot]@users.noreply.github.com`

5. **等待部署完成**，复制服务地址，例如：
   ```
   https://hkex-sfc-dashboard-backend.onrender.com
   ```

6. **修改前端配置**
   编辑 `docs/regulatory/index.html`，在 script 开头添加：
   ```javascript
   const API_BASE = 'https://hkex-sfc-dashboard-backend.onrender.com';
   ```
   并启用后端刷新逻辑（见代码注释）。

7. **提交并推送**，等待 GitHub Pages 重新部署

### 优点
- 真正的"打开页面触发抓取"
- 同时保留每小时自动更新

### 限制（Render 免费套餐）
- **Cold start**：15 分钟无访问后实例会休眠，首次请求可能需要 30-60 秒唤醒
- 每月有 750 小时运行时间限制（足够单个实例整月运行）
- 需要 GitHub Token，务必只在 Render 后台设置，不要写进代码

---

## 当前状态

- ✅ 数据已更新至 2026-07-10
- ✅ GitHub Actions 已改为每 15 分钟更新
- ✅ 前端已支持打开页面自动刷新 JSON
- ⏳ Render 后端需要用户自行部署并配置

---

## 数据文件

| 文件 | 说明 |
|---|---|
| `docs/data/sfc_news.json` | SFC 新闻稿 |
| `docs/data/sfc_circulars.json` | SFC 通函 |
| `docs/data/hkex_guidance_updates.json` | HKEX 规则手册指引/FAQ |
| `docs/data/hkex_regulatory_announcements.json` | HKEX 监管通讯 RSS |
| `docs/data/hkex_news_releases.json` | HKEX 新闻稿（监管相关） |
| `docs/data/hkex_guidance_archive.json` | HKEX 指引信档案 |
| `docs/data/update_meta.json` | 最后更新时间元数据 |
