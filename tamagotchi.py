from fastapi import FastAPI, HTTPException
import json
import os
import random
from datetime import datetime

app = FastAPI()
PET_FILE = "./tamagotchi.json"

def init_pet():
    if not os.path.exists(PET_FILE):
        default_pet = {
            "name": "咕咕",
            "stage": "egg",
            "hunger": 0,
            "happiness": 0,
            "energy": 100,
            "health": 100,
            "mess": 0,
            "age": 0,  # 以小時計數
            "last_updated": datetime.now().isoformat(),
            "last_interaction": datetime.now().isoformat(),
            "last_event": "蛋正在孵化中...",
            "runaway": False
        }
        with open(PET_FILE, "w") as f:
            json.dump(default_pet, f)

def load_pet():
    with open(PET_FILE, "r") as f:
        return json.load(f)

def save_pet(pet):
    with open(PET_FILE, "w") as f:
        json.dump(pet, f)

def update_age_and_status(pet):
    now = datetime.now()
    last_updated = datetime.fromisoformat(pet["last_updated"])
    last_interaction = datetime.fromisoformat(pet["last_interaction"])
    hours_passed = (now - last_updated).total_seconds() / 3600
    hours_since_interaction = (now - last_interaction).total_seconds() / 3600

    pet["age"] += hours_passed
    pet["last_updated"] = now.isoformat()

    if pet["stage"] != "egg" and not pet["runaway"]:
        pet["hunger"] = min(100, pet["hunger"] + hours_passed * 10)
        pet["energy"] = max(0, pet["energy"] - hours_passed * 5)
        pet["mess"] = min(100, pet["mess"] + hours_passed * 8)
        if pet["hunger"] > 80 or pet["mess"] > 80:
            pet["health"] = max(0, pet["health"] - hours_passed * 15)

        if hours_since_interaction > 12:
            pet["happiness"] = max(0, pet["happiness"] - 20)
            pet["health"] = max(0, pet["health"] - 30)
            pet["last_event"] = f"{pet['name']}因為太久沒人照顧，感到很孤單..."

        if hours_since_interaction > 24 and pet["health"] < 20:
            pet["runaway"] = True
            pet["last_event"] = f"{pet['name']}因為長時間被忽視，飛走了...遊戲結束！"

    # 成長階段
    if pet["stage"] == "egg" and pet["age"] >= 0.083:  # 5 分鐘孵化
        pet["stage"] = "baby"
        pet["hunger"] = 50
        pet["happiness"] = 50
        pet["energy"] = 80
        pet["last_event"] = f"{pet['name']}從蛋裡孵出來了！啾啾！"
    elif pet["stage"] == "baby" and pet["age"] >= 24:
        pet["stage"] = "teen"
        pet["last_event"] = f"{pet['name']}長成青少年了！"
    elif pet["stage"] == "teen" and pet["age"] >= 48:
        pet["stage"] = "adult"
        pet["last_event"] = f"{pet['name']}成為成雞啦！"

    return pet

def trigger_random_event(pet):
    if pet["stage"] == "egg" or pet["runaway"]:
        return pet
    event_chance = random.random()
    if event_chance > 0.7:
        events = [
            {"name": "生病", "health": -20, "happiness": -10, "message": f"{pet['name']}感冒了，好可憐！快治療它！"},
            {"name": "搗蛋", "mess": 20, "happiness": 10, "message": f"{pet['name']}在窩裡亂踩，把羽毛弄得到處都是！"},
            {"name": "撒嬌", "happiness": 15, "message": f"{pet['name']}對你啾啾叫，想跟你玩！"}
        ]
        event = random.choice(events)
        pet["hunger"] = max(0, min(100, pet["hunger"] + event.get("hunger", 0)))
        pet["happiness"] = max(0, min(100, pet["happiness"] + event.get("happiness", 0)))
        pet["energy"] = max(0, min(100, pet["energy"] + event.get("energy", 0)))
        pet["health"] = max(0, min(100, pet["health"] + event.get("health", 0)))
        pet["mess"] = max(0, min(100, pet["mess"] + event.get("mess", 0)))
        pet["last_event"] = event["message"]
    return pet

@app.get("/pet/status")
def get_pet_status():
    init_pet()
    pet = load_pet()
    pet = update_age_and_status(pet)
    pet = trigger_random_event(pet)
    save_pet(pet)
    return pet

@app.post("/pet/update")
def update_pet_status(action: dict):
    init_pet()
    pet = load_pet()
    pet = update_age_and_status(pet)
    action_type = action.get("action")
    value = action.get("value", 20)

    if pet["runaway"]:
        raise HTTPException(status_code=400, detail=f"{pet['name']}已經飛走，遊戲結束！")
    if pet["stage"] == "egg" and action_type != "shake" and action_type != "set_name":
        raise HTTPException(status_code=400, detail="蛋還沒孵化，請先搖晃它！")
    if action_type == "set_name":
        new_name = action.get("name")
        if not new_name or len(new_name) > 20:
            raise HTTPException(status_code=400, detail="名字必須在 1-20 字之間！")
        pet["name"] = new_name
        pet["last_event"] = f"你給小雞取名為 {new_name}！啾啾！"
    elif action_type == "shake" and pet["stage"] == "egg":
        pet["age"] += 0.05
        pet["last_event"] = "你搖晃了蛋，它好像動了一下！"
    elif action_type == "feed":
        pet["hunger"] = max(0, pet["hunger"] - value)
        pet["happiness"] = min(100, pet["happiness"] + 10)
        pet["last_event"] = f"{pet['name']}吃得很開心，啾啾！"
    elif action_type == "play":
        pet["happiness"] = min(100, pet["happiness"] + value)
        pet["energy"] = max(0, pet["energy"] - 15)
        pet["last_event"] = f"{pet['name']}玩得很開心，跳來跳去！"
    elif action_type == "rest":
        pet["energy"] = min(100, pet["energy"] + value)
        pet["happiness"] = max(0, pet["happiness"] - 5)
        pet["last_event"] = f"{pet['name']}休息了一下，閉著眼！"
    elif action_type == "clean":
        pet["mess"] = max(0, pet["mess"] - value)
        pet["health"] = min(100, pet["health"] + 10)
        pet["last_event"] = f"你清理了 {pet['name']} 的窩，它看起來很舒服！"
    elif action_type == "heal":
        pet["health"] = min(100, pet["health"] + value)
        pet["happiness"] = min(100, pet["happiness"] + 5)
        pet["last_event"] = f"{pet['name']}的健康恢復了，{pet['name']}很有精神！"

    pet["last_interaction"] = datetime.now().isoformat()
    pet = trigger_random_event(pet)
    save_pet(pet)
    return pet

@app.get("/mcp/discovery")
def mcp_discovery():
    return {
        "name": "Virtual Pet Manager",
        "endpoints": {
            "status": {"method": "GET", "path": "/pet/status"},
            "update": {"method": "POST", "path": "/pet/update"}
        }
    }