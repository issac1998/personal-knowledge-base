#!/usr/bin/env python3
"""Build the public, static copy of the local knowledge base into docs/."""

from __future__ import annotations

import argparse
import html
import os
from pathlib import Path
import re
import shutil
import subprocess
from urllib.parse import urlsplit


DEFAULT_SOURCE = Path("/Users/a/Documents/Codex/2026-10-23/new-chat/knowledge-base")
ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs"

SPACE_PAGES = {
    "page_6ae2eedffcec8191a5cc873eb4c04fb2": "index.html",
    "page_4f8b3ee504208191ba115605f3fc0812": "medical-records/summary-2026-11-09.html",
    "page_6ae3d1b39ac88191a4f939e5f547123c": "notes/右腕就医与理赔.html",
    "page_6ae2ef2c505c8191ab238cd150f11f93": "notes/项目与工作.html",
    "page_6ae2ef3da72881918f6c29f13cbd1886": "notes/投资健康法律.html",
    "page_6ae2ef4fb9f081919b70f01754488c8f": "notes/学习与兴趣.html",
    "page_6ae2ef204f44819190fe7f3b7c3e9809": "notes/生活与出行.html",
    "page_6ae3d1e4864081918bf772f635d58751": "notes/购物核实方法.html",
    "page_6ae2ef07e8508191bf12e9256c569ef3": "notes/个人偏好.html",
    "page_6ae2ef5cb4bc819193b6a546990eae60": "notes/待确认.html",
}

CSS = """\
:root{color-scheme:light;--ink:#19262b;--muted:#59666b;--line:#dce5e3;--accent:#146b67;--soft:#f1f8f6}
*{box-sizing:border-box}html{font:16px/1.7 -apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;color:var(--ink);background:#f9fbfa}
body{margin:0}header{background:white;border-bottom:1px solid var(--line)}.bar{max-width:1100px;margin:auto;padding:13px 24px;display:flex;gap:24px;align-items:center;flex-wrap:wrap}
.brand{font-size:19px;font-weight:700;color:var(--ink);text-decoration:none}nav{display:flex;gap:18px;flex-wrap:wrap}a{color:var(--accent)}nav a{text-decoration:none;font-size:14px}
main{max-width:900px;margin:32px auto 64px;padding:30px 40px;background:#fff;border:1px solid var(--line);border-radius:14px;box-shadow:0 8px 35px #163c3210}
h1,h2,h3{line-height:1.3;scroll-margin-top:25px}h1{font-size:30px;margin-top:0}h2{font-size:22px;margin-top:38px;border-bottom:1px solid var(--line);padding-bottom:8px}h3{font-size:18px;margin-top:28px}
p,li{overflow-wrap:anywhere}li{margin:4px 0}ul,ol{padding-left:1.5em}blockquote{border-left:4px solid var(--accent);padding:3px 18px;margin:20px 0;background:var(--soft)}
table{display:block;overflow-x:auto;border-collapse:collapse;width:100%}td,th{border:1px solid var(--line);padding:7px 10px;text-align:left;vertical-align:top}th{background:var(--soft)}
pre{background:#eef3f2;padding:15px;overflow-x:auto;border-radius:8px}code{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:.9em}p code,li code{background:#eef3f2;padding:2px 4px;border-radius:4px}
.crumb{color:var(--muted);font-size:13px;margin-bottom:18px}.quick{display:flex;flex-wrap:wrap;gap:10px;margin:22px 0}.quick a{border:1px solid var(--line);background:var(--soft);border-radius:8px;padding:8px 13px;text-decoration:none}
footer{max-width:900px;margin:0 auto 32px;padding:0 20px;color:var(--muted);font-size:13px}@media(max-width:650px){main{margin:0;border:0;border-radius:0;padding:25px 20px}.bar{padding:10px 20px}h1{font-size:26px}}
"""


def rel_url(from_page: Path, to_page: str) -> str:
    return Path(os.path.relpath(to_page, from_page.parent)).as_posix()


def fix_links(markdown: str, page: Path) -> str:
    def replace(match: re.Match[str]) -> str:
        url = match.group(2)
        parsed = urlsplit(url)
        if parsed.netloc == "chatgpt.com" and parsed.path.startswith("/space/"):
            page_id = parsed.path.rsplit("/", 1)[-1]
            target = SPACE_PAGES.get(page_id)
            if target:
                return f"]({rel_url(page, target)})"
        if not parsed.scheme and not parsed.netloc and parsed.path.lower().endswith(".md"):
            return f"]({parsed.path[:-3]}.html{('?' + parsed.query) if parsed.query else ''}{('#' + parsed.fragment) if parsed.fragment else ''})"
        return match.group(0)

    return re.sub(r"\](\()([^\s)]+)\)", replace, markdown)


def markdown_html(markdown: str) -> str:
    ruby = "require 'kramdown'; STDOUT.write Kramdown::Document.new(STDIN.read).to_html"
    result = subprocess.run(["ruby", "-e", ruby], input=markdown, text=True, capture_output=True, check=True)
    return result.stdout


def wrap(title: str, page: Path, body: str) -> str:
    home = rel_url(page, "index.html")
    files = rel_url(page, "files.html")
    med = rel_url(page, "medical-records/README.html")
    hub = rel_url(page, "medical-records/health-hub.html")
    crumb = "首页" if page == Path("index.html") else html.escape(page.as_posix())
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} · 个人知识库</title><link rel="stylesheet" href="{rel_url(page, 'assets/style.css')}"></head>
<body><header><div class="bar"><a class="brand" href="{home}">个人知识库</a><nav><a href="{home}">首页</a><a href="{med}">医疗资料</a><a href="{hub}">健康查阅台</a><a href="{files}">全部文件</a></nav></div></header>
<main><div class="crumb">{crumb}</div>{body}</main><footer>公开知识库 · 原始资料与网页版本同时保留</footer></body></html>
"""


def build(source: Path) -> None:
    source = source.expanduser().resolve()
    if not (source / "README.md").is_file():
        raise SystemExit(f"没有找到知识库首页：{source / 'README.md'}")
    if source == OUT or source in OUT.parents or OUT in source.parents:
        raise SystemExit("来源目录与发布目录不能嵌套")
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    pages: list[Path] = []
    raw_count = 0
    for item in sorted(source.rglob("*")):
        if not item.is_file() or any(part.startswith(".") for part in item.relative_to(source).parts):
            continue
        relative = item.relative_to(source)
        destination = OUT / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, destination)
        if relative == Path("medical-records/health-hub.html"):
            old = "https://chatgpt.com/space/page_4f8b3ee504208191ba115605f3fc0812"
            rendered = destination.read_text(encoding="utf-8").replace(old, "summary-2026-11-09.html")
            destination.write_text(rendered, encoding="utf-8")
        raw_count += 1
        if item.suffix.lower() == ".md":
            page = relative.with_suffix(".html")
            markdown = fix_links(item.read_text(encoding="utf-8"), page)
            title_match = re.search(r"^#\s+(.+)$", markdown, re.M)
            title = title_match.group(1).strip() if title_match else item.stem
            (OUT / page).write_text(wrap(title, page, markdown_html(markdown)), encoding="utf-8")
            pages.append(page)
    home_source = (source / "README.md").read_text(encoding="utf-8")
    home_body = markdown_html(fix_links(home_source, Path("index.html")))
    home_body += '<div class="quick"><a href="medical-records/health-hub.html">打开健康记录查阅台</a><a href="files.html">浏览全部文件</a></div>'
    (OUT / "index.html").write_text(wrap("首页", Path("index.html"), home_body), encoding="utf-8")
    entries = [f'<li><a href="{html.escape(p.as_posix(), quote=True)}">{html.escape(p.as_posix())}</a></li>' for p in pages if p != Path("README.html")]
    raw_entries = []
    for p in sorted(OUT.rglob("*")):
        if p.is_file() and p.suffix.lower() in {".csv", ".json", ".tsv", ".py"}:
            rel = p.relative_to(OUT).as_posix()
            raw_entries.append(f'<li><a href="{html.escape(rel, quote=True)}">{html.escape(rel)}</a></li>')
    inventory = '<h1>全部文件</h1><p>下列页面可直接阅读。数据和脚本文件按原样提供。</p><h2>阅读页面</h2><ul>' + "".join(entries) + '</ul><h2>原始数据与脚本</h2><ul>' + "".join(raw_entries) + '</ul>'
    (OUT / "files.html").write_text(wrap("全部文件", Path("files.html"), inventory), encoding="utf-8")
    (OUT / "assets").mkdir()
    (OUT / "assets/style.css").write_text(CSS, encoding="utf-8")
    (OUT / ".nojekyll").touch()
    print(f"已同步 {raw_count} 个原始文件，生成 {len(pages) + 2} 个阅读页面：{OUT}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="本地知识库目录")
    build(parser.parse_args().source)
