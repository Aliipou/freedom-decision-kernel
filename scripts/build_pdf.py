"""Render PAPER.md to PAPER.html (for printing to PDF via a headless browser)."""
from __future__ import annotations

import pathlib

import markdown

ROOT = pathlib.Path(__file__).resolve().parent.parent
md_text = (ROOT / "PAPER.md").read_text(encoding="utf-8")
body = markdown.markdown(md_text, extensions=["tables", "fenced_code", "sane_lists"])

CSS = """
body { font-family: Georgia, 'Times New Roman', serif; max-width: 820px;
       margin: 40px auto; line-height: 1.5; color: #111; }
h1 { font-size: 25px; line-height: 1.2; }
h2 { font-size: 18px; border-bottom: 1px solid #ddd; padding-bottom: 3px; margin-top: 30px; }
h3 { font-size: 15px; margin-top: 20px; }
code, pre { font-family: Consolas, 'Courier New', monospace; }
pre { background: #f6f6f6; padding: 10px 12px; border-radius: 6px; overflow-x: auto;
      font-size: 12px; line-height: 1.35; }
code { background: #f0f0f0; padding: 1px 4px; border-radius: 3px; font-size: 90%; }
pre code { background: none; padding: 0; }
table { border-collapse: collapse; width: 100%; font-size: 12.5px; margin: 10px 0; }
th, td { border: 1px solid #ccc; padding: 5px 8px; text-align: left; vertical-align: top; }
th { background: #f0f0f0; }
blockquote { border-left: 3px solid #bbb; margin: 12px 0; padding: 2px 14px; color: #444; }
hr { border: none; border-top: 1px solid #ddd; margin: 24px 0; }
@page { margin: 1.6cm; }
"""

html = (
    "<!doctype html><html><head><meta charset='utf-8'>"
    f"<style>{CSS}</style></head><body>{body}</body></html>"
)
(ROOT / "PAPER.html").write_text(html, encoding="utf-8")
print("wrote PAPER.html")
