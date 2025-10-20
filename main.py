from datetime import datetime
import os
import requests
from fastapi import FastAPI, Request
from telegram import Bot
import uvicorn
import asyncio
import base64

app = FastAPI()

WEB_HOOK_ID = os.environ.get("WEB_HOOK_ID")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
UNIFI_TOKEN = os.environ.get("UNIFI_TOKEN")

bot = Bot(token=TELEGRAM_TOKEN)

@app.post("/webhook/{webhook_id}")
async def receive_webhook(webhook_id: str, request: Request):
    data = await request.json()

    if webhook_id != WEB_HOOK_ID:
        return {"status": "error", "message": "Invalid webhook ID"}
    
    asyncio.create_task(notify(data))

    return {"status": "success", "webhook_id": webhook_id}


async def notify(data):
    event_id = (
        data.get("alarm", {})
            .get("triggers", [{}])[0]
            .get("eventId")
    )

    event_type = (
        data.get("alarm", {})
            .get("triggers", [{}])[0]
            .get("key")
    )

    timestamp = (
        data.get("alarm", {})
            .get("triggers", [{}])[0]
            .get("timestamp")
    )

    event_name = (
        data.get("alarm", {})
            .get("name")
    )

    image_url = f'https://192.168.0.1/proxy/protect/api/events/{event_id}/thumbnail'

    print(f"事件: {event_name}, 類型: {event_type}, 時間: {timestamp}, 影像URL: {image_url}")

    response = requests.get(
        image_url, 
        cookies={
            "TOKEN": UNIFI_TOKEN
        }, 
        verify=False
    )
    if response.status_code == 200:
        dt = datetime.fromtimestamp(timestamp / 1000)
        filename = f"./output/{dt}.png"
        with open(filename, "wb") as f:
            f.write(response.content)

        with open(filename, "rb") as photo_file:
            await bot.send_photo(
                chat_id=CHAT_ID,
                photo=photo_file,
                caption= f"*{event_name}* for _{event_type}_",
                parse_mode="Markdown"
            )
    else:
        print("下載圖片失敗", response.status_code)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
