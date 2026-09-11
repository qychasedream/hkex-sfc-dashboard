#!/usr/bin/env python3
"""
香港监管资讯看板 - 一键刷新（带进度显示）
由 刷新数据.bat 调用；也可直接运行: python -u refresh_all.py
"""
import os
import socket
import subprocess
import sys
import time
import webbrowser
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable

STAGES = [
    ("SFC / HKEX 官方数据抓取", [PY, "-u", "-X", "utf8", os.path.join("src", "update_data.py")], "约1-2分钟"),
    ("律所监管通讯扫描",        [PY, "-u", "-X", "utf8", os.path.join("src", "collectors", "law_firm_scan.py")], "约1-2分钟"),
    ("元数据汇总",              [PY, "-u", "-X", "utf8", "gen_data.py"], "约10秒"),
]

BAR_W = 30

def bar(pct):
    done = int(BAR_W * pct / 100)
    return "█" * done + "░" * (BAR_W - done)

def run_stage(idx, name, cmd, est):
    total = len(STAGES)
    print()
    print("=" * 58)
    print(f"  [{idx}/{total}] {name}  （预计 {est}）")
    print("=" * 58)
    t0 = time.time()
    # -u 无缓冲，子脚本输出实时显示
    proc = subprocess.Popen(cmd, cwd=ROOT, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True,
                            encoding="utf-8", errors="replace")
    for line in proc.stdout:
        line = line.rstrip()
        if line:
            print("    " + line, flush=True)
    proc.wait()
    el = time.time() - t0
    if proc.returncode == 0:
        print(f"  ✓ 完成，耗时 {int(el)} 秒")
        return True
    else:
        print(f"  ✗ 失败（退出码 {proc.returncode}），耗时 {int(el)} 秒")
        return False

def port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0

def main():
    t_start = time.time()
    print("=" * 58)
    print("   香港监管资讯看板 · 一键刷新")
    print("   全程约需 2-4 分钟，进度实时显示，请勿关闭窗口")
    print("=" * 58)

    ok = True
    for i, (name, cmd, est) in enumerate(STAGES, 1):
        if not run_stage(i, name, cmd, est):
            ok = False
            print("  → 本阶段失败，继续执行后续阶段...")

    # 启动本地服务器（如未运行）
    print()
    print("=" * 58)
    print("  [收尾] 启动本地服务器并打开看板")
    print("=" * 58)
    if port_in_use(8000):
        print("    本地服务器已在运行 (http://localhost:8000)")
    else:
        subprocess.Popen(
            [PY, "-m", "http.server", "8000", "--directory", "docs"],
            cwd=ROOT,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        time.sleep(2)
        print("    已后台启动本地服务器 (http://localhost:8000)")

    url = f"http://localhost:8000/regulatory/?_t={int(time.time())}"
    webbrowser.open(url)
    print(f"    已在浏览器打开: {url}")

    total = int(time.time() - t_start)
    print()
    print("=" * 58)
    if ok:
        print(f"  ✅ 全部完成！总耗时 {total // 60} 分 {total % 60} 秒")
    else:
        print(f"  ⚠️  完成但有阶段失败（详见上方日志），总耗时 {total // 60} 分 {total % 60} 秒")
    print("  如页面仍显示旧数据，请点看板右上角「刷新全部动态」")
    print("=" * 58)
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
