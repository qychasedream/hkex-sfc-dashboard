"""
免费后端服务 — 部署到 Render.com 免费套餐。

功能：
- 提供 /api/refresh 接口，供前端打开页面时调用以触发一次实时抓取
- 提供 /api/status 接口，供前端轮询刷新状态
- 保留原有每小时自动运行的能力（ Render Web Service 内循环）

部署后，把 RENDER_SERVICE_URL 填到 docs/regulatory/index.html 的 API_BASE 配置里即可。
"""

import os
import sys
import subprocess
import threading
import time
import logging
from datetime import datetime, timezone, timedelta

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
# 只允许 GitHub Pages 域名调用，防止被滥用
CORS(app, origins=[
    'https://qychasedream.github.io',
    'http://localhost:*',
    'http://127.0.0.1:*'
])

HKT = timezone(timedelta(hours=8))
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, 'docs', 'data')

GIT_USER_NAME = os.environ.get('GIT_USER_NAME', 'github-actions[bot]')
GIT_USER_EMAIL = os.environ.get('GIT_USER_EMAIL', 'github-actions[bot]@users.noreply.github.com')
GH_TOKEN = os.environ.get('GH_TOKEN', '')
REPO_URL = f'https://{GH_TOKEN}@github.com/qychasedream/hkex-sfc-dashboard.git' if GH_TOKEN else ''

# 全局状态
last_refresh = None
refresh_in_progress = False
refresh_lock = threading.Lock()


def configure_git():
    """配置 git 用户信息"""
    subprocess.run(['git', 'config', 'user.name', GIT_USER_NAME], cwd=ROOT_DIR, capture_output=True)
    subprocess.run(['git', 'config', 'user.email', GIT_USER_EMAIL], cwd=ROOT_DIR, capture_output=True)
    if REPO_URL:
        subprocess.run(['git', 'remote', 'set-url', 'origin', REPO_URL], cwd=ROOT_DIR, capture_output=True)


def run_update():
    """执行数据更新并推送到 GitHub"""
    global last_refresh, refresh_in_progress
    with refresh_lock:
        if refresh_in_progress:
            return {'status': 'already_running'}
        refresh_in_progress = True

    logger.info("开始执行数据更新...")
    try:
        configure_git()

        # 拉取最新代码，避免冲突
        if REPO_URL:
            pull = subprocess.run(
                ['git', 'pull', '--rebase', 'origin', 'main'],
                cwd=ROOT_DIR, capture_output=True, text=True, timeout=60
            )
            if pull.returncode != 0:
                logger.warning(f"git pull 警告: {pull.stderr}")

        # 运行主更新脚本
        result = subprocess.run(
            [sys.executable, os.path.join(ROOT_DIR, 'src', 'update_data.py')],
            cwd=ROOT_DIR, capture_output=True, text=True, timeout=300
        )
        logger.info(result.stdout)
        if result.stderr:
            logger.warning(result.stderr)

        # 可选：运行 Claude AI 数据补充
        if os.path.exists(os.path.join(ROOT_DIR, 'gen_data.py')):
            try:
                ai_result = subprocess.run(
                    [sys.executable, 'gen_data.py'],
                    cwd=ROOT_DIR, capture_output=True, text=True, timeout=120
                )
                logger.info(ai_result.stdout)
            except Exception as e:
                logger.warning(f"gen_data.py 未执行: {e}")

        # 提交并推送
        pushed = False
        subprocess.run(['git', 'add', 'docs/data/'], cwd=ROOT_DIR, capture_output=True, timeout=30)
        status = subprocess.run(
            ['git', 'diff', '--staged', '--quiet'],
            cwd=ROOT_DIR, capture_output=True, timeout=30
        )
        if status.returncode != 0:
            commit_msg = f"📊 自动更新监管数据 — {datetime.now(HKT).strftime('%Y-%m-%d %H:%M HKT')}"
            commit = subprocess.run(
                ['git', 'commit', '-m', commit_msg],
                cwd=ROOT_DIR, capture_output=True, text=True, timeout=30
            )
            if commit.returncode == 0 and REPO_URL:
                push = subprocess.run(
                    ['git', 'push', 'origin', 'main'],
                    cwd=ROOT_DIR, capture_output=True, text=True, timeout=60
                )
                if push.returncode == 0:
                    pushed = True
                    logger.info("✅ 数据已推送至 GitHub")
                else:
                    logger.error(f"git push 失败: {push.stderr}")
        else:
            logger.info("⏭️ 数据无变化，跳过提交")

        last_refresh = datetime.now(HKT).isoformat()
        return {
            'status': 'success',
            'lastUpdate': last_refresh,
            'pushed': pushed,
            'stdout': result.stdout[-2000:] if result.stdout else '',
            'stderr': result.stderr[-1000:] if result.stderr else ''
        }
    except Exception as e:
        logger.error(f"更新失败: {e}")
        return {'status': 'error', 'message': str(e)}
    finally:
        with refresh_lock:
            refresh_in_progress = False


@app.route('/api/refresh', methods=['POST', 'GET'])
def api_refresh():
    """触发一次数据刷新（带 5 分钟冷却，防止滥用）"""
    global last_refresh
    if last_refresh:
        last = datetime.fromisoformat(last_refresh)
        seconds_since = (datetime.now(HKT) - last).total_seconds()
        if seconds_since < 300:
            return jsonify({
                'status': 'cooldown',
                'lastUpdate': last_refresh,
                'secondsRemaining': int(300 - seconds_since),
                'message': '5 分钟内已刷新过，请稍后再试'
            })

    # 在后台线程执行，避免前端等待超时
    thread = threading.Thread(target=run_update)
    thread.start()

    return jsonify({
        'status': 'started',
        'lastUpdate': last_refresh,
        'message': '后台刷新已启动，约需 30-60 秒'
    })


@app.route('/api/status', methods=['GET'])
def api_status():
    """查询刷新状态"""
    return jsonify({
        'status': 'ok',
        'lastUpdate': last_refresh,
        'refreshInProgress': refresh_in_progress
    })


@app.route('/')
def index():
    """返回看板页面（备用入口）"""
    return send_from_directory(os.path.join(ROOT_DIR, 'docs'), 'index.html')


def background_loop():
    """后台每小时自动运行一次（兼容 Render 免费实例）"""
    logger.info("🚀 香港监管资讯看板 — 后端服务启动")
    logger.info(f"   数据目录: {DATA_DIR}")
    logger.info("   更新间隔: 60 分钟")

    # 服务启动时先执行一次
    run_update()

    while True:
        time.sleep(3600)
        run_update()


if __name__ == '__main__':
    # 启动后台定时线程
    bg_thread = threading.Thread(target=background_loop, daemon=True)
    bg_thread.start()

    port = int(os.environ.get('PORT', 5000))
    # 生产环境用 gunicorn，开发环境直接运行
    app.run(host='0.0.0.0', port=port, threaded=True)
