# 香港监管咨询看板

自动追踪香港证监会（SFC）及香港联交所（HKEX）监管动态，包括纪律处分、咨询总结、监管规则及执法新闻。

## 快速开始

```bash
# 生成演示看板（示例数据）
python main.py --open

# 使用 Claude API 获取真实数据（需 Anthropic API Key）
set ANTHROPIC_API_KEY=sk-ant-...
python main.py --live --open
```

## 项目结构

```
├── main.py               # 入口脚本
├── config/config.yaml    # 配置文件
├── docs/index.html       # 生成的看板网页
├── src/
│   ├── collectors/       # 数据采集（RSS / 爬虫 / Claude API）
│   ├── output/           # HTML 看板生成器
│   └── processors/       # 数据去重 / 分类 / 摘要
└── data/                 # 缓存数据
```

## 部署到 GitHub Pages

1. 在 GitHub 创建新仓库 `hkex-sfc-dashboard`
2. 推送代码：
   ```bash
   git remote add origin https://github.com/你的用户名/hkex-sfc-dashboard.git
   git add .
   git commit -m "Initial commit"
   git push -u origin main
   ```
3. 在仓库 Settings > Pages 中，Source 选择 `Deploy from a branch`，分支选 `main`，文件夹选 `/docs`
4. 访问 `https://你的用户名.github.io/hkex-sfc-dashboard/`

## 数据来源

- 香港证监会 SFC: [e-Distribution](https://apps.sfc.hk/edistributionWeb/)
- 香港联交所 HKEX: [监管公告](https://www.hkex.com.hk/News/Regulatory-Announcements)

## 免责声明

本看板仅供参考，不构成法律或投资建议。所有内容以监管机构官方发布为准。
