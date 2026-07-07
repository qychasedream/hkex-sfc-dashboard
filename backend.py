"""
独立后端服务 — 每小时自动拉取 HKEX/SFC 数据并推送至 GitHub。
部署到 Render.com（免费）后 24x7 运行，不依赖前端打开。
"""

import subprocess
import sys
import os
import time
import logging
from datetime import datetime, timezone, timedelta

HKT = timezone(timedelta(hours=8))

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# 项目根目录（假设此文件在仓库根目录）
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, 'docs', 'data')

# GitHub 配置（从环境变量读取，Render 上设置）
GIT_USER_NAME = os.environ.get('GIT_USER_NAME', 'github-actions[bot]')
GIT_USER_EMAIL = os.environ.get('GIT_USER_EMAIL', 'github-actions[bot]@users.noreply.github.com')
GH_TOKEN = os.environ.get('GH_TOKEN', '')  # GitHub Personal Access Token
REPO_URL = f'https://{GH_TOKEN}@github.com/qychasedream/hkex-sfc-dashboard.git' if GH_TOKEN else ''


def configure_git():
    """配置 git 用户信息"""
    subprocess.run(['git', 'config', 'user.name', GIT_USER_NAME], cwd=ROOT_DIR, capture_output=True)
    subprocess.run(['git', 'config', 'user.email', GIT_USER_EMAIL], cwd=ROOT_DIR, capture_output=True)


def run_update():
    """运行数据更新脚本"""
    logger.info("=" * 60)
    logger.info(f"开始数据更新 — {datetime.now(HKT).strftime('%Y-%m-%d %H:%M HKT')}")

    try:
        # 拉取最新代码（避免冲突）
        if REPO_URL:
            subprocess.run(['git', 'pull', '--rebase', REPO_URL, 'main'],
                           cwd=ROOT_DIR, capture_output=True, timeout=60)

        # 运行更新脚本
        result = subprocess.run(
            [sys.executable, os.path.join(ROOT_DIR, 'src', 'update_data.py')],
            cwd=ROOT_DIR, capture_output=True, text=True, timeout=300
        )
        logger.info(result.stdout)
        if result.stderr:
            logger.warning(result.stderr)

        # 运行 Claude AI 数据补充
        try:
            result2 = subprocess.run(
                [sys.executable, 'gen_data.py'],
                cwd=ROOT_DIR, capture_output=True, text=True, timeout=60
            )
            logger.info(result2.stdout)
        except Exception:
            logger.info("gen_data.py 未执行或不存在")

        # 提交并推送
        subprocess.run(['git', 'add', 'docs/data/'], cwd=ROOT_DIR, capture_output=True, timeout=30)
        status = subprocess.run(
            ['git', 'diff', '--staged', '--quiet'],
            cwd=ROOT_DIR, capture_output=True, timeout=30
        )
        if status.returncode != 0:
            commit_msg = f"📊 自动更新监管数据 — {datetime.now(HKT).strftime('%Y-%m-%d %H:%M HKT')}"
            subprocess.run(['git', 'commit', '-m', commit_msg], cwd=ROOT_DIR, capture_output=True, timeout=30)
            if REPO_URL:
                subprocess.run(['git', 'push', REPO_URL, 'main'], cwd=ROOT_DIR, capture_output=True, timeout=60)
                logger.info("✅ 数据已推送至 GitHub")
        else:
            logger.info("⏭️ 数据无变化，跳过提交")

    except Exception as e:
        logger.error(f"❌ 更新失败: {e}")

    logger.info(f"下次更新: ~60 分钟后")


def main():
    """主循环：每 60 分钟运行一次"""
    logger.info("🚀 香港监管资讯看板 — 后端服务启动")
    logger.info(f"   数据目录: {DATA_DIR}")
    logger.info(f"   更新间隔: 60 分钟")

    # 立即运行一次
    run_update()

    # 然后每小时运行
    while True:
        time.sleep(3600)  # 60 分钟
        run_update()


if __name__ == '__main__':
    main()
