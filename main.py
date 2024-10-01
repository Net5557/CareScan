from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, JSONResponse
import io
import base64
import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO
from fastapi.staticfiles import StaticFiles

# Import libraries for LINE Messaging API
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = FastAPI()

# Mount static files (เช่น รูปภาพ, CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# โหลดโมเดล YOLO
model = YOLO("last.pt")

# Channel secret และ Channel access token จาก LINE Developers Console
line_bot_api = LineBotApi('XOWkIFjiF/6ZyckXULH15soqscDaGCADxVcPZhM4t9ElbSDMeC63N7fepOBQWwFegyxywMXOeGKukRCphPssBrqpaUHAkQh3sawZ9gnO7+Gu6lWvE8YxPmjDzhqqde3zL1KQ9VyNZp9TykhwYsVjAwdB04t89/1O/w1cDnyilFU=')  # ใส่ Channel Access Token ของคุณ
handler = WebhookHandler('ee09c1cb8d298e229fc64ded3a5a3295T')  # ใส่ Channel Secret ของคุณ

@app.get("/", response_class=HTMLResponse)
async def index():
    with open('templates/index.html', 'r', encoding='utf-8') as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

@app.get("/data.html", response_class=HTMLResponse)
async def data():
    with open('templates/data.html', 'r', encoding='utf-8') as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

@app.get("/contact.html", response_class=HTMLResponse)
async def data():
    with open('templates/contact.html', 'r', encoding='utf-8') as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

@app.get("/navbar.html", response_class=HTMLResponse)
async def data():
    with open('templates/navbar.html', 'r', encoding='utf-8') as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

@app.get("/footer.html", response_class=HTMLResponse)
async def data():
    with open('templates/footer.html', 'r', encoding='utf-8') as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

@app.post("/predict")
async def predict(image: UploadFile = File(...)):
    image_data = await image.read()
    np_image = np.frombuffer(image_data, np.uint8)
    np_image = cv2.imdecode(np_image, cv2.IMREAD_COLOR)

    results = model.predict(source=np_image)
    result = results[0]

    predictions = []
    for box in result.boxes:
        class_id = result.names[box.cls[0].item()]
        cords = box.xyxy[0].tolist()
        cords = [round(x) for x in cords]
        conf = round(box.conf[0].item(), 2)

        predictions.append({
            "class_id": class_id,
            "coordinates": cords,
            "confidence": conf
        })

    result_image = Image.fromarray(result.plot()[:, :, ::-1])
    buffer = io.BytesIO()
    result_image.save(buffer, format="JPEG")
    buffer.seek(0)

    result_image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return JSONResponse(content={"predictions": predictions, "result_image": result_image_base64})


# Endpoint สำหรับรับ Webhook จาก LINE
@app.post("/webhook")
async def callback(request: Request):
    # รับค่า X-Line-Signature จาก Header
    signature = request.headers['X-Line-Signature']

    # รับค่าจาก body
    body = await request.body()
    body = body.decode('utf-8')

    try:
        # Handle ข้อความจาก LINE
        handler.handle(body, signature)
    except InvalidSignatureError:
        return JSONResponse(content={"message": "Invalid signature"}, status_code=400)

    return JSONResponse(content={"message": "OK"}, status_code=200)

# ฟังก์ชันสำหรับจัดการข้อความที่ได้รับจากผู้ใช้
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # ตอบกลับข้อความที่ผู้ใช้ส่งมา
    reply_message = f"คุณส่งข้อความว่า: {event.message.text}"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_message)
    )
