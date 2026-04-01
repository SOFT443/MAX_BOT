import asyncio
import logging
import httpx
from fastapi import FastAPI
from maxapi import Bot, Dispatcher
from maxapi.types import BotStarted, MessageCreated

# ========== НАСТРОЙКИ ==========
TOKEN = "f9LHodD0cOJPSQFyzeHjlwhPa8rjFBDzIdnz8GwLy-sWU105dTWg3LE_hT5NkX9Apo6mGxA89YHT9G3xOnWx"
BITRIX_WEBHOOK = "https://taksidrayver.bitrix24.ru/rest/1228/bj7vi1r4oew89t64/"
CATEGORY_ID = 14  # ← твой ID воронки
# ===============================

bot = Bot(TOKEN)
dp = Dispatcher()
app = FastAPI()

logging.basicConfig(level=logging.INFO)
user_data = {}

# ========== ФОНОВЫЙ ПИНГ ==========
async def keep_alive():
    while True:
        await asyncio.sleep(600)
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:8000/health")
                print(f"🔁 Пинг: {response.status_code}")
        except Exception as e:
            print(f"❌ Ошибка пинга: {e}")

# ========== ОТПРАВКА В БИТРИКС24 ==========
async def send_to_bitrix24(phone: str, name: str, car_number: str):
    base_url = BITRIX_WEBHOOK

    contact_data = {
        "fields": {
            "NAME": name,
            "PHONE": [{"VALUE": phone, "VALUE_TYPE": "WORK"}]
        }
    }

    async with httpx.AsyncClient() as client:
        contact_response = await client.post(
            f"{base_url}crm.contact.add.json",
            json=contact_data,
            timeout=10
        )
        contact_result = contact_response.json()
        contact_id = contact_result.get("result")

        if not contact_id:
            print(f"❌ Не удалось создать контакт: {contact_response.text}")
            return

        print(f"✅ Контакт создан, ID: {contact_id}")

        deal_data = {
            "fields": {
                "TITLE": f"Заявка на бронирование от {name}",
                "STAGE_ID": "NEW",
                "CATEGORY_ID": CATEGORY_ID,
                "ASSIGNED_BY_ID": 1,
                "CONTACT_ID": contact_id,
                "COMMENTS": f"Номер ТС: {car_number}"
            }
        }

        deal_response = await client.post(
            f"{base_url}crm.deal.add.json",
            json=deal_data,
            timeout=10
        )

        print(f"✅ Статус сделки: {deal_response.status_code}")
        print(f"📦 Ответ: {deal_response.text}")

# ========== ОБРАБОТЧИК СООБЩЕНИЙ ==========
@dp.bot_started()
async def on_start(event: BotStarted):
    await event.bot.send_message(
        chat_id=event.chat_id,
        text="Привет! Я бот для бронирования авто.\nНапиши /start"
    )

@dp.message_created()
async def handle_message(event: MessageCreated):
    uid = event.from_user.user_id
    text = event.message.body.text.strip()
    text_lower = text.lower()
    
    if text_lower == "/start":
        await event.message.answer(
            "🚗 Добро пожаловать в бот бронирования авто!\n\n"
            "Для оформления заявки введите номер телефона:\n"
            "Формат: +7 999 123-45-67\n\n"
            "🔙 НАЗАД"
        )
        user_data[uid] = {"step": "phone"}
        return
    
    if uid not in user_data:
        return
    
    step = user_data[uid].get("step")
    
    if text_lower == "назад":
        if step == "name":
            user_data[uid]["step"] = "phone"
            await event.message.answer(
                "📞 Введите номер телефона:\nФормат: +7 999 123-45-67\n\n🔙 НАЗАД"
            )
        elif step == "car_number":
            user_data[uid]["step"] = "name"
            await event.message.answer(
                "📝 Введите ваше ФИО:\n\n🔙 НАЗАД"
            )
        elif step == "final":
            user_data[uid]["step"] = "car_number"
            await event.message.answer(
                "🚗 Введите номер ТС:\n\n🔙 НАЗАД"
            )
        return
    
    if step == "phone":
        phone_clean = text.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if phone_clean.startswith(("+7", "8")):
            user_data[uid]["phone"] = text
            user_data[uid]["step"] = "name"
            await event.message.answer(
                "📝 Введите ваше ФИО:\n\n🔙 НАЗАД"
            )
        else:
            await event.message.answer(
                "❌ Неверный формат. Пример: +7 999 123-45-67\n\n🔙 НАЗАД"
            )
        return
    
    if step == "name":
        if len(text.split()) >= 2:
            user_data[uid]["name"] = text
            user_data[uid]["step"] = "car_number"
            await event.message.answer(
                "🚗 Введите номер ТС:\n\n🔙 НАЗАД"
            )
        else:
            await event.message.answer(
                "❌ Введите полное ФИО (минимум фамилия и имя)\n\n🔙 НАЗАД"
            )
        return
    
    if step == "car_number":
        if text.strip():
            user_data[uid]["car_number"] = text
            await event.message.answer(
                f"📋 ПРОВЕРЬТЕ ДАННЫЕ:\n\n"
                f"📞 Телефон: {user_data[uid]['phone']}\n"
                f"👤 ФИО: {user_data[uid]['name']}\n"
                f"🚗 Номер ТС: {text}\n\n"
                f"✅ Всё верно? Напишите: СОГЛАСЕН\n"
                f"🔙 Или НАЗАД, чтобы исправить"
            )
            user_data[uid]["step"] = "final"
        else:
            await event.message.answer("❌ Введите номер ТС\n\n🔙 НАЗАД")
        return
    
    if step == "final":
        if text_lower == "согласен":
            await event.message.answer(
                f"✅ ЗАЯВКА ОТПРАВЛЕНА!\n\n"
                f"📞 Телефон: {user_data[uid]['phone']}\n"
                f"👤 ФИО: {user_data[uid]['name']}\n"
                f"🚗 Номер ТС: {user_data[uid]['car_number']}\n\n"
                f"Менеджер свяжется с вами."
            )
            await send_to_bitrix24(
                phone=user_data[uid]['phone'],
                name=user_data[uid]['name'],
                car_number=user_data[uid]['car_number']
            )
            del user_data[uid]
        elif text_lower == "назад":
            user_data[uid]["step"] = "car_number"
            await event.message.answer("🚗 Введите номер ТС:\n\n🔙 НАЗАД")
        else:
            await event.message.answer("❌ Напишите СОГЛАСЕН для отправки или НАЗАД для исправления")

@app.get("/")
async def root():
    return {"status": "ok"}

@app.get("/health")
async def health():
    return {"status": "ok"}

# ========== ЗАПУСК БОТА ==========
async def main():
    await bot.delete_webhook()
    print("Вебхук удалён, запускаем polling...")
    asyncio.create_task(keep_alive())
    await dp.start_polling(bot)

def run_bot():
    asyncio.run(main())

import threading
threading.Thread(target=run_bot, daemon=True).start()
print("Бот запущен!")
