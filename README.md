# Tamagotchi MCP Server

## Installation

### Create a virtual environment

```bash
python3 -m venv tamagotchi-mcp-env
```

### Activate the virtual environment

```bash
source tamagotchi-mcp-env/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

## Usage

```bash
uvicorn tamagotchi:app --host 0.0.0.0 --port 8000
```
