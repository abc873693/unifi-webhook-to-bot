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

bot = Bot(token=TELEGRAM_TOKEN)

@app.post("/webhook/{webhook_id}")
async def receive_webhook(webhook_id: str, request: Request):
    data = await request.json()

    if webhook_id != WEB_HOOK_ID:
        return {"status": "error", "message": "Invalid webhook ID"}
    
    asyncio.create_task(notify(data))

    return {"status": "success", "webhook_id": webhook_id}


async def notify(data):

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

    thumbnail_base64 = (
        data.get("alarm", {})
            .get("thumbnail")
    )

    if thumbnail_base64:
        dt = datetime.fromtimestamp(timestamp / 1000)
        thumbnail_filename = f"./output/{dt}.png"
        
        if thumbnail_base64.startswith('data:image'):
            thumbnail_base64 = thumbnail_base64.split(',')[1]
        
        with open(thumbnail_filename, "wb") as f:
            f.write(base64.b64decode(thumbnail_base64))
        
        await bot.send_photo(
            chat_id=CHAT_ID,
            photo=thumbnail_filename,
            caption= f"*{event_name}* for _{event_type}_",
            parse_mode="Markdown"
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
