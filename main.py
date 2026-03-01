from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

print("PAGE_ACCESS_TOKEN:", "SET" if PAGE_ACCESS_TOKEN else "NOT SET")
print("VERIFY_TOKEN:", VERIFY_TOKEN)

user_state = {}


@app.get("/webhook")
async def verify(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return PlainTextResponse(content=challenge)

    return PlainTextResponse(content="verify failed", status_code=403)


@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    print("INCOMING EVENT:", body)

    if "entry" in body:
        for entry in body["entry"]:
            for event in entry.get("messaging", []):

                sender_id = event["sender"]["id"]

                # ถ้าเป็นข้อความ
                if "message" in event:

                    # กันกรณีไม่มี text (เช่น sticker, image)
                    text = event["message"].get("text", "").strip()

                    if not text:
                        send_message(sender_id, "กรุณาพิมพ์ข้อความเป็นตัวหนังสือครับ 😊")
                        return {"status": "ok"}

                    print("USER TEXT:", text)

                    # ผู้ใช้ใหม่
                    if sender_id not in user_state:
                        user_state[sender_id] = "waiting_detail"

                        send_message(
                            sender_id,
                            "สวัสดีครับ 😊\n\n"
                            "รับพัฒนาเว็บไซต์ทุกประเภท\n\n"
                            "กรุณาพิมพ์รายละเอียดเว็บไซต์ที่ต้องการ เช่น:\n"
                            "• ประเภทเว็บไซต์\n"
                            "• ฟังก์ชันที่ต้องการ\n"
                            "• งบประมาณ\n"
                            "• ระยะเวลา\n\n"
                            "พิมพ์รายละเอียดได้เลยครับ 👇",
                        )
                        return {"status": "ok"}

                    # ผู้ใช้ส่งรายละเอียด
                    if user_state[sender_id] == "waiting_detail":
                        send_message(
                            sender_id,
                            "ขอบคุณสำหรับรายละเอียดครับ 🙏\n"
                            "Developer จะติดต่อกลับโดยเร็วที่สุดครับ",
                        )

                        user_state[sender_id] = "done"
                        return {"status": "ok"}

    return {"status": "ok"}


def send_message(recipient_id, text):
    url = "https://graph.facebook.com/v18.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    data = {"recipient": {"id": recipient_id}, "message": {"text": text}}

    response = requests.post(url, params=params, headers=headers, json=data)

    print("=== SEND MESSAGE DEBUG ===")
    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text)