# Tamagotchi MCP Server

實作一個簡易的 Tamagotchi MCP Server，模擬養電子雞的遊戲。

## Prerequisites

- Python 3.11
- uvicorn

## Setup

### 1. 建立虛擬環境

```bash
python3 -m venv tamagotchi-mcp-env
```

### 2. 使用虛擬環境

```bash
source tamagotchi-mcp-env/bin/activate
```

### 3. 安裝依賴套件

```bash
pip install -r requirements.txt
```

### 4. 啟動 FastAPI 伺服器

```bash
uvicorn tamagotchi:app --host 0.0.0.0 --port 8000
```

### 5. 配置 Claude Desktop
```json
{
  "mcpServers": {
    "tamagotchi-mcp-server": {
      "command": "/path/to/your/tamagotchi-mcp-server/tamagotchi-mcp-env/bin/python3",
      "args": ["/path/to/your/tamagotchi-mcp-server/server.py"]
    }
  }
}
```

## Usage

基本動作

- 「幫小雞取名字」
- 「查看小雞狀況」
- 「搖晃蛋」
- 「餵小雞吃飯」
- 「跟小雞玩」
- 「讓小雞休息」
- 「幫小雞洗澡」
- 「帶小雞看醫生」
- 「清理小雞的窩」
