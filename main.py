import asyncio
import logging
import threading
import httpx
from fastapi import FastAPI
from maxapi import Bot, Dispatcher
from maxapi.types import BotStarted, MessageCreated

# ========== НАСТРОЙКИ ==========
TOKEN = "f9LHodD0cOJPSQFyzeHjlwhPa8rjFBDzIdnz8GwLy-sWU105dTWg3LE_hT5NkX9Apo6mGxA89YHT9G3xOnWx"
BITRIX_WEBHOOK = "https://taksidrayver.bitrix24.ru/rest/1228/itdr0r0hi0mcui33"
CATEGORY_ID = 14
# ===============================

bot = Bot(TOKEN)
dp = Dispatcher()
app = FastAPI()

logging.basicConfig(level=logging.INFO)
user_data = {}
processed = set()

# ========== ПИНГ ==========
async def keep_alive():
    while True:
        await asyncio.sleep(600)
        try:
            async with httpx.AsyncClient() as client:
                await client.get("http://localhost:8000/health")
        except:
            pass

# ========== БИТРИКС ==========
async def send_to_bitrix24(phone, name, car_number):
    base = BITRIX_WEBHOOK
    contact_data = {"fields": {"NAME": name, "PHONE": [{"VALUE": phone}]}}
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{base}/crm.contact.add.json", json=contact_data, timeout=30)
        cid = r.json().get("result")
        if not cid:
            print("Ошибка контакта")
            return
        deal_data = {
            "fields": {
                "TITLE": f"Заявка от {name}",
                "STAGE_ID": "NEW",
                "CATEGORY_ID": CATEGORY_ID,
                "ASSIGNED_BY_ID": 1,
                "CONTACT_ID": cid,
                "COMMENTS": f"ТС: {car_number}"
            }
        }
        await client.post(f"{base}/crm.deal.add.json", json=deal_data, timeout=30)
        print("Сделка создана")

# ========== БОТ ==========
@dp.bot_started()
async def on_start(event):
    await event.bot.send_message(chat_id=event.chat_id, text="Напиши /start")

@dp.message_created()
async def handle(event):
    uid = event.from_user.user_id
    msg_id = event.message.body.mid
    if msg_id in processed:
        return
    processed.add(msg_id)

    text = event.message.body.text.strip().lower()

    if text == "/start":
        await event.message.answer(
            "🚗 Введите номер телефона:\n+7 999 123-45-67\n🔙 НАЗАД"
        )
        user_data[uid] = {"step": "phone"}
        return

    if uid not in user_data:
        return

    step = user_data[uid].get("step")

    if text == "назад":
        if step == "name":
            user_data[uid]["step"] = "phone"
            await event.message.answer("📞 Введите телефон")
        elif step == "car_number":
            user_data[uid]["step"] = "name"
            await event.message.answer("📝 Введите ФИО")
        elif step == "final":
            user_data[uid]["step"] = "car_number"
            await event.message.answer("🚗 Введите номер ТС")
        return

    if step == "phone":
        if text.replace(" ", "").replace("-", "").replace("(", "").replace(")", "").startswith(("+7", "8")):
            user_data[uid]["phone"] = text
            user_data[uid]["step"] = "name"
            await event.message.answer("📝 Введите ФИО")
        else:
            await event.message.answer("❌ Неверный формат")
        return

    if step == "name":
        if len(text.split()) >= 2:
            user_data[uid]["name"] = text
            user_data[uid]["step"] = "car_number"
            await event.message.answer("🚗 Введите номер ТС")
        else:
            await event.message.answer("❌ Введите полное ФИО")
        return

    if step == "car_number":
        if text.strip():
            user_data[uid]["car_number"] = text
            await event.message.answer(
                f"📋 Данные:\n📞 {user_data[uid]['phone']}\n👤 {user_data[uid]['name']}\n🚗 {text}\n\n✅ СОГЛАСЕН\n🔙 НАЗАД"
            )
            user_data[uid]["step"] = "final"
        else:
            await event.message.answer("❌ Введите номер ТС")
        return

    if step == "final" and text == "согласен":
        await event.message.answer(f"✅ Заявка отправлена!")
        await send_to_bitrix24(
            user_data[uid]['phone'],
            user_data[uid]['name'],
            user_data[uid]['car_number']
        )
        del user_data[uid]

@app.get("/")
async def root():
    return {"status": "ok"}

@app.get("/health")
async def health():
    return {"status": "ok"}

# ========== ЗАПУСК ==========
async def main():
    await bot.delete_webhook()
    asyncio.create_task(keep_alive())
    await dp.start_polling(bot)

threading.Thread(target=lambda: asyncio.run(main()), daemon=True).start()
print("Бот запущен")
