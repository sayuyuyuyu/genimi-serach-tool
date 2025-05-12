# Gemini Grounding Search MCP Server

Google Gemini の **検索グラウディング** 機能をツール化し、  
[MCP](https://modelcontextprotocol.org/) クライアント（Cursor AI／Claude Desktop など）から呼び出せる軽量サーバーです。

---

## ディレクトリ構成

```
genimi_search_mcp/        プロジェクトルート
├─ .env.example           環境変数サンプル
├─ server.py              MCP サーバー本体
├─ requirements.txt       必要ライブラリ（uv で自動生成される）
└─ .vscode/launch.json    VS Code デバッグ設定
```

---

## 前提条件

| ソフト            | バージョン例          |
|-------------------|-----------------------|
| Python            | 3.9 – 3.12           |
| `uv`              | 0.1.35 以上           |
| `google-genai`    | 0.5.* 以上            |
| `mcp` (Python SDK)| 1.2.* 以上            |

> **Windows** では PowerShell を推奨（`Ctrl + Shift + 右クリック` → "PowerShell ここで開く"）。

---

## セットアップ

```powershell
# 1. プロジェクト生成（済みなら不要）
#    curl -LsSf https://astral.sh/uv/install.sh | sh
#    uv init genimi_search_mcp

cd C:\Work\genimi_search_mcp
uv venv                       # .venv/ を作成
.venv\Scripts\Activate.ps1    # venv 有効化（Linux/Mac は source .venv/bin/activate）

# 2. 依存ライブラリ
uv pip install -U google-genai mcp[cli] python-dotenv

# 3. .env を作成
copy .env.example .env
notepad .env                  # API キーを設定してください
```

---

## 環境変数

```
GEMINI_API_KEY=your_api_key_here
```

- **検索グラウディング特権** を持つキーを使う  
  （[Google AI Studio › API keys] で発行）。

---

## 起動方法

```powershell
uv run python server.py
```

ターミナルに

```
[INFO] FastMCP listening on stdio…
```

と出れば待受完了。  
クライアント側で MCP サーバーとして `gemini-grounding-search` を登録し、  
以下の JSON を送ると検索結果＋引用リンクが返る。

```jsonc
{
  "tool": "web_search",
  "arguments": {
    "query": "F1 2025 日本GP 優勝は？",
    "max_sources": 3
  }
}
```

---

### HTTP モード（オプション）

サーバー側を変更：

```python
if __name__ == "__main__":
    mcp.run("http", port=8801)
```

```bash
curl -X POST http://127.0.0.1:8801   -H "Content-Type: application/json"   -d '{"tool":"web_search","arguments":{"query":"最新の TypeScript 安定版","max_sources":2}}'
```

---

## VS Code でのデバッグ

1. `File › Open Folder…` でプロジェクトを開く。  
2. 右下の **Python Interpreter** を `.venv` の Python に切替。  
3. **Run and Debug** パネルで構成 **Run MCP server** を選び **F5**。  
   - 別ターミナル不要でホットリロードしながら開発できる。

---

## ツール呼び出し例（REST Client 拡張）

```
### Search
POST http://localhost
Content-Type: application/json

{
  "tool": "web_search",
  "arguments": {
    "query": "LLM の RAG とは",
    "max_sources": 4
  }
}
```

"Send Request" をクリックすると結果がサイドパネルに表示される。

---

## MCPサーバーの導入方法

### VS Code での導入

1. MCPサーバーを起動:
   ```powershell
   .venv\Scripts\Activate.ps1
   python server.py
   ```

2. VS Codeで設定を開く: `Ctrl+,` (Windows/Linux) または `Cmd+,` (Mac)

3. 検索ボックスに「MCP」を入力

4. 「Tool Providers」セクションで「Add Item」をクリック

5. 以下の設定を追加:
   ```json
   {
     "name": "gemini-grounding-search",
     "command": "${workspaceFolder}/.venv/Scripts/python",
     "args": ["${workspaceFolder}/server.py"]
   }
   ```

6. VS Codeを再起動

7. AIアシスタントで利用:
   ```
   @web_search クエリ文字列
   ```

### Cursor での導入

1. MCPサーバーを起動:
   ```powershell
   .venv\Scripts\Activate.ps1
   python server.py
   ```

2. Cursorの設定を開く: `Ctrl+,` (Windows/Linux) または `Cmd+,` (Mac)

3. 左メニューから「AI」を選択

4. 「MCP Tool Provider」セクションで「Add Tool Provider」をクリック

5. 以下を入力:
   - Name: `gemini-grounding-search`
   - Command: アブソリュートパスで python.exe を指定
     例: `C:\Users\username\project\.venv\Scripts\python.exe`
   - Args: アブソリュートパスで server.py を指定
     例: `C:\Users\username\project\server.py`

6. Cursorを再起動

7. AIアシスタントで利用:
   ```
   @web_search クエリ文字列
   ```

---

## トラブルシューティング

| 症状 | 原因と対処 |
|------|-----------|
| `ModuleNotFoundError: google.genai` | `pip install -U google-genai`／venv 未選択 |
| `KeyError: 'GEMINI_API_KEY'` | `.env` でキー名を **GEMINI_API_KEY** にしているか |
| 引用リンクが付かない | `MODEL_ID` が 2.x 系か確認／`types.Tool(google_search=…)` を渡しているか |
| MCP からツールが見えない | `@mcp.tool()` デコレータ忘れ／サーバー再起動忘れ |
| VS Code/Cursorで接続できない | パスが正しいか確認／server.py が "stdio" モードになっているか |

---

## ライセンス

本リポジトリのコードは MIT License とします。  
ただし Google Gemini API の利用規約・制限は別途従ってください。
