"""
Render Cron Job — 每小时拉取 HKEX/SFC 数据并推送至 GitHub。
部署为 Render Cron Job，每小时执行一次。
"""

import subprocess
import sys
import os
import logging
from datetime import datetime, timezone, timedelta

HKT = timezone(timedelta(hours=8))
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

GH_TOKEN = os.environ.get('GH_TOKEN', '')
GIT_USER = os.environ.get('GIT_USER_NAME', 'github-actions[bot]')
GIT_EMAIL = os.environ.get('GIT_USER_EMAIL', 'github-actions[bot]@users.noreply.github.com')
REPO_URL = f'https://{GH_TOKEN}@github.com/qychasedream/hkex-sfc-dashboard.git' if GH_TOKEN else ''


def setup_git():
    subprocess.run(['git', 'config', 'user.name', GIT_USER], cwd=ROOT_DIR)
    subprocess.run(['git', 'config', 'user.email', GIT_EMAIL], cwd=ROOT_DIR)
    # 确保远程地址带 token
    if REPO_URL:
        subprocess.run(['git', 'remote', 'set-url', 'origin', REPO_URL], cwd=ROOT_DIR)


def main():
    logger.info(f"=== Render Cron Job: 数据更新 {datetime.now(HKT).strftime('%Y-%m-%d %H:%M HKT')} ===")

    setup_git()

    # 1. 拉取最新代码
    subprocess.run(['git', 'pull', '--rebase', 'origin', 'main'], cwd=ROOT_DIR, timeout=60)

    # 2. 运行主更新脚本
    r = subprocess.run([sys.executable, 'src/update_data.py'], cwd=ROOT_DIR,
                       capture_output=True, text=True, timeout=300)
    logger.info(r.stdout)
    if r.stderr:
        logger.warning(r.stderr)

    # 3. 运行 Claude AI 数据补充
    if os.path.exists(os.path.join(ROOT_DIR, 'gen_data.py')):
        subprocess.run([sys.executable, 'gen_data.py'], cwd=ROOT_DIR, timeout=60)

    # 4. 提交并推送
    subprocess.run(['git', 'add', 'docs/data/'], cwd=ROOT_DIR, timeout=30)
    status = subprocess.run(['git', 'diff', '--staged', '--quiet'], cwd=ROOT_DIR, timeout=30)
    if status.returncode != 0:
        msg = f"📊 Cron数据更新 — {datetime.now(HKT).strftime('%Y-%m-%d %H:%M HKT')}"
        subprocess.run(['git', 'commit', '-m', msg], cwd=ROOT_DIR, timeout=30)
        subprocess.run(['git', 'push', 'origin', 'main'], cwd=ROOT_DIR, timeout=60)
        logger.info("✅ 已推送")
    else:
        logger.info("⏭️ 数据无变化")


if __name__ == '__main__':
    main()
