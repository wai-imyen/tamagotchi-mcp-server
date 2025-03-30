import aiohttp
from mcp.server.fastmcp import FastMCP
from datetime import datetime

FASTAPI_BASE_URL = "http://0.0.0.0:8000"
mcp = FastMCP("tamagotchi-mcp-server")

@mcp.tool()
async def get_game_instructions() -> dict:
    """取得遊戲說明"""
    instructions = (
        "【歡迎來到小雞養成遊戲！】\n"
        "你將養育一隻可愛的小雞，從一顆蛋開始，陪伴它成長為成雞！\n\n"
        "🎮 遊戲玩法：\n"
        "1. **開始遊戲**：你的小雞預設名叫「小雞」，初始狀態為蛋\n"
        "2. **自訂名字**：你可以幫小雞取個獨特的名字！\n"
        "3. **孵化蛋**：蛋階段時，你可以搖晃蛋，約 5 分鐘後孵化。\n"
        "4. **照顧小雞**：\n"
        "   - 'feed'：餵食降低飢餓，提升快樂。\n"
        "   - 'play'：玩耍提升快樂，但消耗能量。\n"
        "   - 'rest'：休息恢復能量，可能降低快樂。\n"
        "   - 'clean'：清理窩減少髒亂，提升健康。\n"
        "   - 'heal'：治療恢復健康。\n"
        "5. **時間影響**：太久沒照顧（12 小時以上），小雞會不開心，甚至可能飛走（24 小時且健康低）！\n\n"
        "🏆 目標：\n"
        "讓小雞健康快樂地成長到成雞階段，避免它因為疏忽而飛走。根據你的照顧，它可能會有不同的結局哦！\n"
        "快開始吧，聽到蛋裡傳來啾啾聲了嗎？"
    )
    return {"message": instructions}

@mcp.tool()
async def get_pet_status() -> dict:
    """取得寵物狀態"""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{FASTAPI_BASE_URL}/pet/status") as response:
            if response.status == 200:
                pet_data = await response.json()
                stage_display = {
                    "egg": "🥚 蛋階段",
                    "baby": "🐤 幼雛階段",
                    "teen": "🐥 青少年階段",
                    "adult": "🐔 成雞階段"
                }
                last_interaction = datetime.fromisoformat(pet_data["last_interaction"])
                hours_since_interaction = (datetime.now() - last_interaction).total_seconds() / 3600

                status_msg = (
                    f"【寵物 {pet_data['name']}】\n"
                    f"📅 年齡: {pet_data['age']:.2f} 小時\n"
                    f"⏰ 距離上次互動: {hours_since_interaction:.2f} 小時\n"
                    f"📊 階段: {stage_display[pet_data['stage']]}\n"
                    f"🍽️ 飢餓: {pet_data['hunger']}%\n"
                    f"😊 快樂: {pet_data['happiness']}%\n"
                    f"⚡ 能量: {pet_data['energy']}%\n"
                    f"❤️ 健康: {pet_data['health']}%\n"
                    f"🗑️ 髒亂: {pet_data['mess']}%\n"
                    f"📜 最近事件: {pet_data['last_event']}\n"
                )
                if pet_data["runaway"]:
                    status_msg += "❌ 小雞已經飛走，遊戲結束！請重新開始。\n"
                elif pet_data["stage"] == "egg":
                    status_msg += "💡 提示: 使用 'shake' 動作來加速孵化！\n"
                elif hours_since_interaction > 12:
                    status_msg += "⚠️ 你太久沒照顧小雞了，它很孤單，快行動吧！\n"
                elif pet_data["health"] < 30:
                    status_msg += "🚨 小雞健康很差，快治療它！\n"
                elif pet_data["mess"] > 80:
                    status_msg += "🧹 窩太髒了，快清理吧！\n"
                status_msg += "💡 你可以用 'set_pet_name' 更改小雞的名字！\n"
                return {"message": status_msg, "data": pet_data}
            else:
                raise ValueError(f"無法獲取寵物狀態: {response.status}")

@mcp.tool()
async def set_pet_name(name: str) -> dict:
    """
    設定寵物名字
    
    Args:
        name: 名字 (1-20 字)
    """
    payload = {"action": "set_name", "name": name}
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{FASTAPI_BASE_URL}/pet/update", json=payload) as response:
            if response.status == 200:
                pet_data = await response.json()
                return {
                    "message": f"成功將小雞命名為 {pet_data['name']}！啾啾！",
                    "data": pet_data
                }
            else:
                error_detail = await response.text()
                raise ValueError(f"命名失敗: {error_detail}")

@mcp.tool()
async def update_pet_status(action: str, value: int = 20) -> dict:
    """
    更新寵物狀態
    
    Args:
        action: 行動 (e.g., 'feed', 'play', 'rest', 'clean', 'heal', 'shake')
        value: 行動值 (default: 20)
    """
    payload = {"action": action, "value": value}
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{FASTAPI_BASE_URL}/pet/update", json=payload) as response:
            if response.status == 200:
                pet_data = await response.json()
                message = (
                    f"【行動結果】\n"
                    f"📜 {pet_data['last_event']}\n"
                    f"🍽️ 飢餓: {pet_data['hunger']}%\n"
                    f"😊 快樂: {pet_data['happiness']}%\n"
                    f"⚡ 能量: {pet_data['energy']}%\n"
                    f"❤️ 健康: {pet_data['health']}%\n"
                    f"🗑️ 髒亂: {pet_data['mess']}%\n"
                )
                if pet_data["runaway"]:
                    message += "❌ 小雞已經飛走，遊戲結束！\n"
                return {"message": message, "data": pet_data}
            else:
                error_detail = await response.text()
                raise ValueError(f"更新失敗: {error_detail}")

@mcp.tool()
async def reset() -> dict:
    """
    重置遊戲
    """
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{FASTAPI_BASE_URL}/reset") as response:
            if response.status == 200:
                return {"message": "遊戲已重置"}
            else:
                raise ValueError("無法重置遊戲")

@mcp.resource("discovery://info")
async def mcp_discovery() -> dict:
    """
    提供 MCP discovery 資訊
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{FASTAPI_BASE_URL}/mcp/discovery") as response:
            if response.status == 200:
                return await response.json()
            else:
                raise ValueError("無法獲取 discovery 資訊")

if __name__ == "__main__":
    mcp.run()