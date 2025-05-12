from __future__ import annotations
import asyncio, os, textwrap
from typing import List

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP            # MCP SDK ≥1.2
from google import genai                          # ← 新 SDK
from google.genai import types                    # 型定義はこちら

# ── 初期化 ───────────────────────────────
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_ID = "gemini-2.0-flash"

mcp = FastMCP("gemini-grounding-search")

# ── Google 検索グラウディング ─────────────
@mcp.tool()
async def web_search(query: str, max_sources: int = 5) -> str:
    search_tool = types.Tool(google_search=types.GoogleSearch())  # 🔑
    resp = await asyncio.to_thread(
        client.models.generate_content,
        model=MODEL_ID,
        contents=query,
        config=types.GenerateContentConfig(tools=[search_tool]),
    )

    answer = resp.text
    # grounding_chunks からリンクを抽出
    chunks = resp.candidates[0].grounding_metadata.grounding_chunks
    links = []
    for c in chunks[:max_sources]:
        web = getattr(c, "web", None)     # c.web に WebGrounding オブジェクト
        if web:
            links.append(f"- {web.title or '(no-title)'} : {web.uri}")


    return textwrap.dedent(f"""{answer}

    ▼ 参考リンク
    {os.linesep.join(links) if links else "(なし)"}
    """)

# ── エントリポイント ───────────────────
if __name__ == "__main__":
    mcp.run("stdio")
