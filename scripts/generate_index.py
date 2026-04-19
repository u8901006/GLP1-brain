#!/usr/bin/env python3
"""Generate index.html listing all GLP-1 daily reports."""

import glob
import os
from datetime import datetime

html_files = sorted(glob.glob("docs/glp1-*.html"), reverse=True)
links = ""
for f in html_files[:30]:
    name = os.path.basename(f)
    date = name.replace("glp1-", "").replace(".html", "")
    try:
        d = datetime.strptime(date, "%Y-%m-%d")
        date_display = f"{d.year}年{d.month}月{d.day}日"
    except Exception:
        date_display = date
    weekday = (
        ["一", "二", "三", "四", "五", "六", "日"][
            datetime.strptime(date, "%Y-%m-%d").weekday()
        ]
        if len(date) == 10
        else ""
    )
    links += f'<li><a href="{name}">\U0001f4c5 {date_display}（週{weekday}）</a></li>\n'

total = len(html_files)

index = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>GLP-1 Brain \u00b7 GLP-1 文獻日報</title>
<style>
  :root {{ --bg: #f6f1e8; --surface: #fffaf2; --line: #d8c5ab; --text: #2b2118; --muted: #766453; --accent: #8c4f2b; --accent-soft: #ead2bf; }}
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: radial-gradient(circle at top, #fff6ea 0, var(--bg) 55%, #ead8c6 100%); color: var(--text); font-family: "Noto Sans TC", "PingFang TC", "Helvetica Neue", Arial, sans-serif; min-height: 100vh; }}
  .container {{ position: relative; z-index: 1; max-width: 640px; margin: 0 auto; padding: 80px 24px; }}
  .logo {{ font-size: 48px; text-align: center; margin-bottom: 16px; }}
  h1 {{ text-align: center; font-size: 24px; color: var(--text); margin-bottom: 8px; }}
  .subtitle {{ text-align: center; color: var(--accent); font-size: 14px; margin-bottom: 48px; }}
  .count {{ text-align: center; color: var(--muted); font-size: 13px; margin-bottom: 32px; }}
  ul {{ list-style: none; }}
  li {{ margin-bottom: 8px; }}
  a {{ color: var(--text); text-decoration: none; display: block; padding: 14px 20px; background: var(--surface); border: 1px solid var(--line); border-radius: 12px; transition: all 0.2s; font-size: 15px; }}
  a:hover {{ background: var(--accent-soft); border-color: var(--accent); transform: translateX(4px); }}
  .actions {{ display: flex; gap: 12px; margin-top: 40px; margin-bottom: 40px; flex-wrap: wrap; }}
  .action-card {{ flex: 1; min-width: 200px; display: flex; align-items: center; gap: 14px; padding: 18px 20px; background: var(--surface); border: 1px solid var(--line); border-radius: 16px; text-decoration: none; color: var(--text); transition: all 0.2s; }}
  .action-card:hover {{ background: var(--accent-soft); border-color: var(--accent); transform: translateY(-2px); }}
  .action-icon {{ font-size: 28px; flex-shrink: 0; }}
  .action-title {{ font-size: 14px; font-weight: 700; }}
  .action-desc {{ font-size: 11px; color: var(--muted); margin-top: 2px; }}
  footer {{ margin-top: 56px; text-align: center; font-size: 12px; color: var(--muted); }}
  footer a {{ display: inline; padding: 0; background: none; border: none; color: var(--muted); }}
  footer a:hover {{ color: var(--accent); }}
</style>
</head>
<body>
<div class="container">
  <div class="logo">\U0001f9ea</div>
  <h1>GLP-1 Brain</h1>
  <p class="subtitle">GLP-1 文獻日報 \u00b7 每日自動更新</p>
  <p class="count">共 {total} 期日報</p>
  <ul>{links}</ul>
  <div class="actions">
    <a href="https://blog.leepsyclinic.com/" class="action-card" target="_blank">
      <span class="action-icon">\U0001f4ec</span>
      <div class="action-text">
        <div class="action-title">訂閱電子報</div>
        <div class="action-desc">接收最新 GLP-1 研究動態</div>
      </div>
    </a>
    <a href="https://buymeacoffee.com/CYlee" class="action-card" target="_blank">
      <span class="action-icon">\u2615</span>
      <div class="action-text">
        <div class="action-title">Buy me a coffee</div>
        <div class="action-desc">支持這個計畫持續運作</div>
      </div>
    </a>
  </div>
  <footer>
    <p>Powered by PubMed + Zhipu AI &middot; <a href="https://github.com/u8901006/GLP1-brain">GitHub</a></p>
  </footer>
</div>
</body>
</html>"""

with open("docs/index.html", "w", encoding="utf-8") as f:
    f.write(index)
print("Index page generated")
