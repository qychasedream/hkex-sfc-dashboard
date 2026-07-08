"""
Render Web Service — 打开页面时自动刷新数据并展示看板。
Render 免费层：每月 750 小时，15 分钟无访问自动休眠，访问即唤醒。
"""
import subprocess, sys, os, json, time, logging
from datetime import datetime, timezone, timedelta
from http.server import HTTPServer, SimpleHTTPRequestHandler

HKT = timezone(timedelta(hours=8))
ROOT = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.join(ROOT, 'docs')
DATA = os.path.join(DOCS, 'data')
os.makedirs(DATA, exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

CACHE_FILE = os.path.join(DATA, '_render_cache.json')
CACHE_TTL = 3600  # 1 小时，避免频繁请求 HKEX


def is_cache_fresh():
    if not os.path.exists(CACHE_FILE):
        return False
    try:
        with open(CACHE_FILE) as f:
            cache = json.load(f)
        age = time.time() - cache.get('ts', 0)
        return age < CACHE_TTL
    except Exception:
        return False


def refresh_data():
    """运行数据更新脚本"""
    if is_cache_fresh():
        logger.info("缓存未过期，跳过刷新")
        return

    logger.info(f"=== 刷新数据 {datetime.now(HKT).strftime('%Y-%m-%d %H:%M HKT')} ===")

    # 1. 运行 SFC/HKEX 抓取
    result = subprocess.run(
        [sys.executable, os.path.join(ROOT, 'src', 'update_data.py')],
        cwd=ROOT, capture_output=True, text=True, timeout=300
    )
    logger.info(result.stdout[-300:] if len(result.stdout) > 300 else result.stdout)

    # 2. 补充 Claude AI 搜索数据（如果 gen_data.py 存在）
    gen = os.path.join(ROOT, 'gen_data.py')
    if os.path.exists(gen):
        subprocess.run([sys.executable, gen], cwd=ROOT, timeout=60)

    # 3. 记录缓存时间
    with open(CACHE_FILE, 'w') as f:
        json.dump({'ts': time.time(), 'updated': datetime.now(HKT).isoformat()}, f)
    logger.info("数据刷新完成")


class DashboardHandler(SimpleHTTPRequestHandler):
    """自定义 handler：访问首页时触发刷新，其他请求正常服务"""

    def do_GET(self):
        # 如果是访问看板页面，先触发刷新
        if self.path in ('/', '/regulatory/', '/regulatory/index.html', '/index.html'):
            logger.info(f"页面请求触发刷新: {self.path}")
            try:
                refresh_data()
            except Exception as e:
                logger.error(f"刷新失败: {e}")

        # 路径映射：/ → /regulatory/
        if self.path == '/':
            self.path = '/regulatory/index.html'
        elif self.path == '/regulatory/' or self.path == '/regulatory':
            self.path = '/regulatory/index.html'

        # 静态文件从 docs/ 目录提供服务
        return super().do_GET()

    def translate_path(self, path):
        return os.path.join(DOCS, path.lstrip('/'))

    def log_message(self, format, *args):
        logger.info(f"{self.client_address[0]} - {format % args}")


def main():
    port = int(os.environ.get('PORT', 10000))

    # 启动时刷新一次
    try:
        refresh_data()
    except Exception as e:
        logger.error(f"初始刷新失败: {e}")

    server = HTTPServer(('0.0.0.0', port), DashboardHandler)
    logger.info(f"🚀 香港监管资讯看板已启动: http://0.0.0.0:{port}")
    server.serve_forever()


if __name__ == '__main__':
    main()
