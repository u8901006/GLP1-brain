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
        date_display = d.strftime("%Y年%-m月%-d日")
    except Exception:
        date_display = date
    weekday = (
        ["一", "二", "三", "四", "五", "六", "日"][
            datetime.strptime(date, "%Y-%m-%d").weekday()
        ]
        if len(date) == 10
        else ""
    )
    links += f'<li><a href="{name}">\U0001f4c5 {date_display}\uff08\u9031{weekday}\uff09</a></li>\n'

total = len(html_files)

index = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>GLP-1 Brain \u00b7 GLP-1 \u6587\u737b\u65e5\u5831</title>
<style>
  :root {{ --bg: #070b14; --surface: #0d1525; --line: #1a2744; --text: #E8EDF5; --muted: #8899B4; --accent: #00D4AA; --accent-soft: rgba(0,212,170,0.12); }}
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--text); font-family: -apple-system, "PingFang TC", "Helvetica Neue", Arial, sans-serif; min-height: 100vh; }}
  .container {{ position: relative; z-index: 1; max-width: 640px; margin: 0 auto; padding: 80px 24px; }}
  .logo {{ font-size: 48px; text-align: center; margin-bottom: 16px; }}
  h1 {{ text-align: center; font-size: 24px; color: #fff; margin-bottom: 8px; }}
  .subtitle {{ text-align: center; color: #00D4AA; font-size: 14px; margin-bottom: 48px; }}
  .count {{ text-align: center; color: var(--muted); font-size: 13px; margin-bottom: 32px; }}
  ul {{ list-style: none; }}
  li {{ margin-bottom: 8px; }}
  a {{ color: var(--text); text-decoration: none; display: block; padding: 14px 20px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); border-radius: 12px; transition: all 0.2s; font-size: 15px; }}
  a:hover {{ background: rgba(0,212,170,0.05); border-color: rgba(0,212,170,0.2); transform: translateX(4px); }}
  footer {{ margin-top: 56px; text-align: center; font-size: 12px; color: #37474F; }}
  footer a {{ display: inline; padding: 0; background: none; border: none; color: #546E7A; }}
  footer a:hover {{ color: #00D4AA; }}
</style>
</head>
<body>
<div class="container">
  <div class="logo">\U0001f9ea</div>
  <h1>GLP-1 Brain</h1>
  <p class="subtitle">GLP-1 \u6587\u737b\u65e5\u5831 \u00b7 \u6bcf\u65e5\u81ea\u52d5\u66f4\u65b0</p>
  <p class="count">\u5171 {total} \u671f\u65e5\u5831</p>
  <ul>{links}</ul>
  <footer>
    <p>Powered by PubMed + Zhipu AI &middot; <a href="https://github.com/u8901006/GLP1-brain">GitHub</a></p>
  </footer>
</div>
</body>
</html>"""

with open("docs/index.html", "w", encoding="utf-8") as f:
    f.write(index)
print("Index page generated")
