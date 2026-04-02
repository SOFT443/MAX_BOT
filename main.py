import asyncio
import logging
import threading
import httpx
from fastapi import FastAPI, Request
from maxapi import Bot, Dispatcher
from maxapi.types import BotStarted, MessageCreated

# ========== НАСТРОЙКИ ==========
TOKEN = "f9LHodD0cOJYcBrUhdAkWfRzKqK57mFf5SExUIZIHXqG0PoiAgzYBDoEEOb2gBsW7OkfIOrxCdUu-J-BhcxK"
BITRIX_WEBHOOK = "https://taksidrayver.bitrix24.ru/rest/1228/itdr0r0hi0mcui33"
CATEGORY_ID = 14
RENDER_URL = "https://max-booking-bot-1.onrender.com"
# ===============================

# ========== ВСЕ АВТОМОБИЛИ ==========
VALID_CARS = {
    "Т731ХО797": "Belgee X50",
    "Е330ХТ797": "Belgee X50",
    "Е327ХС797": "Belgee X50",
    "Т290ХВ797": "Belgee X50",
    "Т218ХВ797": "Belgee X50",
    "Т780ХК797": "Belgee X50",
    "Т279ХВ797": "Belgee X50",
    "Е335ХТ797": "Belgee X50",
    "Т203ХР797": "Belgee X50",
    "Т638ХА797": "Belgee X50",
    "О615РН797": "Chery Arrizo 8",
    "Е036ОК797": "Chery Arrizo 8",
    "О919РН797": "Chery Arrizo 8",
    "О921РН797": "Chery Arrizo 8",
    "О884РН797": "Chery Arrizo 8",
    "Х069РР797": "Chery Arrizo 8",
    "О905РН797": "Chery Arrizo 8",
    "О469РН797": "Chery Arrizo 8",
    "Е488НН797": "Chery Tiggo 4",
    "К012НР797": "Chery Tiggo 4",
    "К676НТ797": "Chery Tiggo 4",
    "Е981НУ797": "Chery Tiggo 4",
    "Х990НС797": "Chery Tiggo 4",
    "Е479НН797": "Chery Tiggo 4",
    "К042НР797": "Chery Tiggo 4",
    "Х187НН797": "Chery Tiggo 4",
    "Е984НУ797": "Chery Tiggo 4",
    "М969МВ797": "Chery Tiggo 7 Pro",
    "Е546ОМ797": "Chery Tiggo 7 Pro",
    "Е797ОК797": "Chery Tiggo 7 Pro",
    "М979МВ797": "Chery Tiggo 7 Pro",
    "Е472ОМ797": "Chery Tiggo 7 Pro",
    "ЕВ07899": "Chery Tiggo 7 Pro",
    "Т727ОМ797": "Chery Tiggo 7 Pro",
    "Т166ОЕ797": "Chery Tiggo 7 Pro",
    "К486МХ797": "Chery Tiggo 7 Pro",
    "К541МХ797": "Chery Tiggo 7 Pro",
    "М995МВ797": "Chery Tiggo 7 Pro",
    "ЕВ07499": "Chery Tiggo 7 Pro",
    "Т717ОМ797": "Chery Tiggo 7 Pro",
    "Е553ОМ797": "Chery Tiggo 7 Pro",
    "Е056ОН797": "Chery Tiggo 7 Pro",
    "Е202ОС797": "Chery Tiggo 7 Pro",
    "ЕВ07399": "Chery Tiggo 7 Pro",
    "Т220ОЕ797": "Chery Tiggo 7 Pro",
    "Т704ОМ797": "Chery Tiggo 7 Pro",
    "Е542ОМ797": "Chery Tiggo 7 Pro",
    "ЕВ07299": "Chery Tiggo 7 Pro",
    "Т216ОЕ797": "Chery Tiggo 7 Pro",
    "Т237ОЕ797": "Chery Tiggo 7 Pro",
    "ЕВ07599": "Chery Tiggo 7 Pro",
    "Е677ОР797": "Chery Tiggo 7 Pro",
    "Е548ОМ797": "Chery Tiggo 7 Pro",
    "Е493ОМ797": "Chery Tiggo 7 Pro",
    "Е490ОМ797": "Chery Tiggo 7 Pro",
    "ЕВ07799": "Chery Tiggo 7 Pro",
    "М035МА797": "Chery Tiggo 7 Pro",
    "Е800ОК797": "Chery Tiggo 7 Pro",
    "Е522ОМ797": "Chery Tiggo 7 Pro",
    "ЕВ07999": "Chery Tiggo 7 Pro",
    "К543МХ797": "Chery Tiggo 7 Pro",
    "Е531ОМ797": "Chery Tiggo 7 Pro",
    "К508МХ797": "Chery Tiggo 7 Pro",
    "ЕВ07199": "Chery Tiggo 7 Pro",
    "ЕВ08099": "Chery Tiggo 7 Pro",
    "К544МХ797": "Chery Tiggo 7 Pro",
    "Е547ОМ797": "Chery Tiggo 7 Pro",
    "Е802ОК797": "Chery Tiggo 7 Pro",
    "Е686ОР797": "Chery Tiggo 7 Pro",
    "Е494ОМ797": "Chery Tiggo 7 Pro",
    "Е133ОН797": "Chery Tiggo 7 Pro",
    "К518МХ797": "Chery Tiggo 7 Pro",
    "ЕВ07699": "Chery Tiggo 7 Pro",
    "Е664ОР797": "Chery Tiggo 7 Pro",
    "Х960РЕ797": "EVOLUTE i-PRO",
    "Х409РО797": "EVOLUTE i-PRO",
    "Х918РН797": "EVOLUTE i-PRO",
    "Х456РО797": "EVOLUTE i-PRO",
    "Х393РО797": "EVOLUTE i-PRO",
    "О085УМ797": "FAW Bestune B70",
    "А455ХВ797": "FAW Bestune B70",
    "О636УО797": "FAW Bestune B70",
    "С128УА797": "FAW Bestune B70",
    "А597ТО797": "FAW Bestune B70",
    "С072УЕ797": "FAW Bestune B70",
    "С348УМ797": "FAW Bestune B70",
    "А460СА797": "FAW Bestune B70",
    "А371ХС797": "FAW Bestune B70",
    "А371ТТ797": "FAW Bestune B70",
    "А370ТМ797": "FAW Bestune B70",
    "Х500УЕ797": "FAW Bestune B70",
    "Х528УЕ797": "FAW Bestune B70",
    "А505СС797": "FAW Bestune B70",
    "А549ТК797": "FAW Bestune B70",
    "А509ХМ797": "FAW Bestune B70",
    "С925УО797": "FAW Bestune B70",
    "С478УР797": "FAW Bestune B70",
    "А374ТС797": "FAW Bestune B70",
    "С079УЕ797": "FAW Bestune B70",
    "А595ХМ797": "FAW Bestune B70",
    "Х499УЕ797": "FAW Bestune B70",
    "А459ХЕ797": "FAW Bestune B70",
    "А460ТА797": "FAW Bestune B70",
    "А549ТН797": "FAW Bestune B70",
    "А596СХ797": "FAW Bestune B70",
    "Х465УЕ797": "FAW Bestune B70",
    "О125УМ797": "FAW Bestune B70",
    "А596ТМ797": "FAW Bestune B70",
    "А508ХЕ797": "FAW Bestune B70",
    "С940УО797": "FAW Bestune B70",
    "О644УО797": "FAW Bestune B70",
    "К761УУ797": "FAW Bestune B70",
    "А507ХМ797": "FAW Bestune B70",
    "А457ТУ797": "FAW Bestune B70",
    "Х546УЕ797": "FAW Bestune B70",
    "А551ТУ797": "FAW Bestune B70",
    "С889УО797": "FAW Bestune B70",
    "А593СА797": "FAW Bestune B70",
    "К791УУ797": "FAW Bestune B70",
    "А551ТА797": "FAW Bestune B70",
    "А368ТТ797": "FAW Bestune B70",
    "А550СР797": "FAW Bestune B70",
    "К801УУ797": "FAW Bestune B70",
    "О090УМ797": "FAW Bestune B70",
    "Р321УУ797": "FAW Bestune B70",
    "Х185РМ797": "Geely Atlas Pro",
    "М130ОУ797": "Geely Atlas Pro",
    "С096РВ797": "Geely Atlas Pro",
    "С031РВ797": "Geely Atlas Pro",
    "Х196РМ797": "Geely Atlas Pro",
    "Х700РК797": "Geely Atlas Pro",
    "Х716РО797": "Geely Atlas Pro",
    "С033РВ797": "Geely Atlas Pro",
    "ЕА88799": "Geely Atlas Pro",
    "С236ОМ797": "Geely Atlas Pro",
    "М145ОУ797": "Geely Atlas Pro",
    "Н640ОА797": "Geely Atlas Pro",
    "Н679ОА797": "Geely Atlas Pro",
    "С587РК797": "Geely Atlas Pro",
    "ЕА88499": "Geely Atlas Pro",
    "Н670ОА797": "Geely Atlas Pro",
    "С528РК797": "Geely Atlas Pro",
    "К622ОЕ797": "Geely Atlas Pro",
    "К569ОВ797": "Geely Atlas Pro",
    "С225ОМ797": "Geely Atlas Pro",
    "Х652РЕ797": "Geely Atlas Pro",
    "Х227РМ797": "Geely Atlas Pro",
    "С186ОМ797": "Geely Atlas Pro",
    "М172ОУ797": "Geely Atlas Pro",
    "Х684РЕ797": "Geely Atlas Pro",
    "К584ОВ797": "Geely Atlas Pro",
    "Х155РА797": "Geely Atlas Pro",
    "Х230РМ797": "Geely Atlas Pro",
    "С065РВ797": "Geely Atlas Pro",
    "К566ОВ797": "Geely Atlas Pro",
    "С608РК797": "Geely Atlas Pro",
    "Х218РМ797": "Geely Atlas Pro",
    "Н698ОА797": "Geely Atlas Pro",
    "Н659ОА797": "Geely Atlas Pro",
    "Н347ОВ797": "Geely Atlas Pro",
    "Х700РО797": "Geely Atlas Pro",
    "С604РК797": "Geely Atlas Pro",
    "Х173РР797": "Geely Atlas Pro",
    "М114ОУ797": "Geely Atlas Pro",
    "Х684РК797": "Geely Atlas Pro",
    "С420РА797": "Geely Atlas Pro",
    "М164ОУ797": "Geely Atlas Pro",
    "ЕА88699": "Geely Atlas Pro",
    "К149ОК797": "Geely Atlas Pro",
    "Х131РА797": "Geely Atlas Pro",
    "Х135РА797": "Geely Atlas Pro",
    "Х112РА797": "Geely Atlas Pro",
    "С855ХМ797": "Geely Atlas Pro",
    "С242ОМ797": "Geely Atlas Pro",
    "Х141РА797": "Geely Atlas Pro",
    "Н633ОА797": "Geely Atlas Pro",
    "М138ОУ797": "Geely Atlas Pro",
    "Х150РА797": "Geely Atlas Pro",
    "Х160РА797": "Geely Atlas Pro",
    "С590РК797": "Geely Atlas Pro",
    "К119ОК797": "Geely Atlas Pro",
    "ЕА88599": "Geely Atlas Pro",
    "М155ОУ797": "Geely Atlas Pro",
    "Х694РК797": "Geely Atlas Pro",
    "Х152РА797": "Geely Atlas Pro",
    "Х116ОМ797": "Haval F7",
    "М850ОТ797": "Haval F7",
    "Х603ОО797": "Haval F7",
    "Х154ОМ797": "Haval F7",
    "Х144ОМ797": "Haval F7",
    "М927ОТ797": "Haval F7",
    "Х504ОА797": "Haval F7",
    "М914ОТ797": "Haval F7",
    "Х662ОО797": "Haval F7",
    "Х546ОА797": "Haval F7",
    "Х097ОМ797": "Haval F7",
    "М925ОТ797": "Haval F7",
    "М852ОТ797": "Haval F7",
    "М371ОР797": "Haval F7",
    "Х560ОА797": "Haval F7",
    "М870ОТ797": "Haval F7",
    "М379ОР797": "Haval F7",
    "Х076ОМ797": "Haval F7",
    "Х124ОМ797": "Haval F7",
    "Х580ОК797": "Haval F7",
    "У367УР797": "Haval Jolion",
    "Т597ОР797": "Haval Jolion",
    "Х562УС797": "Haval Jolion",
    "Х537УС797": "Haval Jolion",
    "У914УО797": "Haval Jolion",
    "У480РК797": "Haval Jolion",
    "У363УР797": "Haval Jolion",
    "Т098ОС797": "Haval Jolion",
    "У519РО797": "Haval Jolion",
    "У341УМ797": "Haval Jolion",
    "У391УР797": "Haval Jolion",
    "У911УО797": "Haval Jolion",
    "Х902УМ797": "Haval Jolion",
    "У081РУ797": "Haval Jolion",
    "Х904УМ797": "Haval Jolion",
    "Т132ОС797": "Haval Jolion",
    "Х634РА797": "Haval Jolion",
    "Х159РВ797": "Haval Jolion",
    "Т575ОР797": "Haval Jolion",
    "Х945УР797": "Haval Jolion",
    "Х461УН797": "Haval Jolion",
    "У861УО797": "Haval Jolion",
    "У332УР797": "Haval Jolion",
    "У521РО797": "Haval Jolion",
    "У524РК797": "Haval Jolion",
    "Х964УР797": "Haval Jolion",
    "Х905УМ797": "Haval Jolion",
    "У856УО797": "Haval Jolion",
    "У891УО797": "Haval Jolion",
    "Т134ОС797": "Haval Jolion",
    "У985РЕ797": "Haval Jolion",
    "У897УО797": "Haval Jolion",
    "Х050УТ797": "Haval Jolion",
    "У394УР797": "Haval Jolion",
    "У017РМ797": "Haval Jolion",
    "У607ХК797": "Haval Jolion",
    "Т032ОН797": "Haval Jolion",
    "Т129ОС797": "Haval Jolion",
    "Т127ОС797": "Haval Jolion",
    "Т557ОР797": "Haval Jolion",
    "У135РУ797": "Haval Jolion",
    "Т108ОС797": "Haval Jolion",
    "У383УР797": "Haval Jolion",
    "Х426УН797": "Haval Jolion",
    "У906УО797": "Haval Jolion",
    "Х421УН797": "Haval Jolion",
    "У386УР797": "Haval Jolion",
    "Х655РК797": "Haval Jolion",
    "Х937УР797": "Haval Jolion",
    "Т550ОР797": "Haval Jolion",
    "Т109ОС797": "Haval Jolion",
    "Т038ОН797": "Haval Jolion",
    "У514РК797": "Haval Jolion",
    "У316УМ797": "Haval Jolion",
    "У421УР797": "Haval Jolion",
    "У994РН797": "Haval Jolion",
    "У950РЕ797": "Haval Jolion",
    "Т573ОР797": "Haval Jolion",
    "У840УО797": "Haval Jolion",
    "У052РМ797": "Haval Jolion",
    "У332УМ797": "Haval Jolion",
    "Т120ОС797": "Haval Jolion",
    "У422УР797": "Haval Jolion",
    "Х542УС797": "Haval Jolion",
    "Х125РВ797": "Haval Jolion",
    "У851УО797": "Haval Jolion",
    "У397УР797": "Haval Jolion",
    "У904УО797": "Haval Jolion",
    "Т117ОС797": "Haval Jolion",
    "У342УР797": "Haval Jolion",
    "У850УО797": "Haval Jolion",
    "У887УТ797": "Haval Jolion",
    "У877УТ797": "Haval Jolion",
    "Т092ОС797": "Haval Jolion",
    "У920УО797": "Haval Jolion",
    "Т583ОР797": "Haval Jolion",
    "Т060ОН797": "Haval Jolion",
    "У516РО797": "Haval Jolion",
    "У523РО797": "Haval Jolion",
    "У832УО797": "Haval Jolion",
    "У016РМ797": "Haval Jolion",
    "У146РУ797": "Haval Jolion",
    "У381УР797": "Haval Jolion",
    "У336УМ797": "Haval Jolion",
    "У857УО797": "Haval Jolion",
    "У876УО797": "Haval Jolion",
    "У528РО797": "Haval Jolion",
    "Х142РВ797": "Haval Jolion",
    "У399УХ797": "Haval Jolion",
    "У503РО797": "Haval Jolion",
    "У848УО797": "Haval Jolion",
    "У314УМ797": "Haval Jolion",
    "Х101РВ797": "Haval Jolion",
    "У829УО797": "Haval Jolion",
    "У161РУ797": "Haval Jolion",
    "Т017ОН797": "Haval Jolion",
    "А558ХА797": "Hongqi H5",
    "А554ТС797": "Hongqi H5",
    "А558СА797": "Hongqi H5",
    "А558ТЕ797": "Hongqi H5",
    "А557ХР797": "Hongqi H5",
    "А052ТС797": "Hongqi H5",
    "О448ЕТ797": "Kia K5",
    "К201ЕО797": "Kia K5",
    "Р845ЕТ797": "Kia K5",
    "Р873ЕТ797": "Kia K5",
    "У162ЕР797": "Kia K5",
    "М625ЕО797": "Kia K5",
    "У189ЕР797": "Kia K5",
    "У528ЕР797": "Kia K5",
    "У180ЕР797": "Kia K5",
    "Р834ЕТ797": "Kia K5",
    "К155ЕО797": "Kia K5",
    "Р859ЕТ797": "Kia K5",
    "У201ЕР797": "Kia K5",
    "У530ЕР797": "Kia K5",
    "М570ЕО797": "Kia K5",
    "У151ЕР797": "Kia K5",
    "О458ЕТ797": "Kia K5",
    "Р862ЕТ797": "Kia K5",
    "К199ЕО797": "Kia K5",
    "М654ЕО797": "Kia K5",
    "К216ЕО797": "Kia K5",
    "У548ЕР797": "Kia K5",
    "У200ЕР797": "Kia K5",
    "Р842ЕТ797": "Kia K5",
    "К170ЕО797": "Kia K5",
    "К183ЕО797": "Kia K5",
    "К198ЕО797": "Kia K5",
    "У205ЕР797": "Kia K5",
    "У518ЕР797": "Kia K5",
    "К206ЕО797": "Kia K5",
    "К154ЕО797": "Kia K5",
    "У539ЕР797": "Kia K5",
    "У517ЕР797": "Kia K5",
    "У537ЕР797": "Kia K5",
    "М639ЕО797": "Kia K5",
    "М049ЕО797": "Kia K5",
    "К200ЕО797": "Kia K5",
    "У152ЕР797": "Kia K5",
    "Р881ЕТ797": "Kia K5",
    "О015ЕК797": "Kia K5",
    "К159ЕО797": "Kia K5",
    "К394АВ797": "Kia Optima",
    "К392АН797": "Kia Optima",
    "К390АТ797": "Kia Optima",
    "К397АН797": "Kia Optima",
    "К395АН797": "Kia Optima",
    "В450КН797": "LADA Vesta",
    "К174КТ797": "LADA Vesta",
    "К342КА797": "LADA Vesta",
    "Х894ВЕ797": "Skoda Octavia",
    "К383ВА797": "Skoda Octavia",
    "К381АА797": "Skoda Octavia",
    "К384АВ797": "Skoda Octavia",
    "К400АХ797": "Skoda Octavia",
    "К397АР797": "Skoda Octavia",
    "К378АН797": "Skoda Octavia",
    "К371АК797": "Skoda Octavia",
    "К385АВ797": "Skoda Octavia",
    "К384АР797": "Skoda Octavia",
    "К387АВ797": "Skoda Octavia",
    "Р585МО797": "Toyota Camry",
}

bot = Bot(TOKEN)
dp = Dispatcher()
app = FastAPI()

logging.basicConfig(level=logging.INFO)
user_data = {}
processed = set()
user_deal_map = {}  # deal_id -> user_id

# ========== ПИНГИ ==========
async def keep_alive():
    while True:
        await asyncio.sleep(240)
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.get(f"{RENDER_URL}/ping")
                await client.get(f"{RENDER_URL}/health")
        except:
            pass

# ========== ОТПРАВКА В MAX ==========
async def send_message_to_max(user_id: int, text: str):
    url = f"https://platform-api.max.ru/messages?user_id={user_id}"
    headers = {"Authorization": TOKEN, "Content-Type": "application/json"}
    payload = {"text": text}
    async with httpx.AsyncClient() as client:
        await client.post(url, headers=headers, json=payload)

# ========== ПОЛУЧЕНИЕ ПОСЛЕДНЕГО КОММЕНТАРИЯ ИЗ СДЕЛКИ ==========
async def get_last_comment_from_deal(deal_id: int) -> str:
    """Получает последний комментарий из сделки через API Битрикс24"""
    base = BITRIX_WEBHOOK
    method = "crm.timeline.comment.list"
    params = {
        "filter": {"ENTITY_ID": deal_id, "ENTITY_TYPE": "deal"},
        "order": {"CREATED": "DESC"},
        "limit": 1
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{base}/{method}.json", json=params, timeout=30)
            result = response.json()
            if result.get("result"):
                comments = result["result"]
                if comments:
                    return comments[0].get("COMMENT", "")
    except Exception as e:
        print(f"Ошибка получения комментария: {e}")
    return ""

# ========== ОТПРАВКА В БИТРИКС24 ==========
async def send_to_bitrix24(phone, name, car_number, car_model, uid):
    base = BITRIX_WEBHOOK
    contact_data = {"fields": {"NAME": name, "PHONE": [{"VALUE": phone}]}}
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{base}/crm.contact.add.json", json=contact_data, timeout=30)
        cid = r.json().get("result")
        if not cid:
            return
        deal_data = {
            "fields": {
                "TITLE": f"Заявка от {name}",
                "STAGE_ID": "NEW",
                "CATEGORY_ID": CATEGORY_ID,
                "ASSIGNED_BY_ID": 1,
                "CONTACT_ID": cid,
                "COMMENTS": f"Номер ТС: {car_number}\nМарка: {car_model}"
            }
        }
        deal_response = await client.post(f"{base}/crm.deal.add.json", json=deal_data, timeout=30)
        deal_result = deal_response.json()
        deal_id = deal_result.get("result")
        if deal_id:
            user_deal_map[deal_id] = uid
            print(f"✅ Сделка {deal_id} привязана к пользователю {uid}")

# ========== ВЕБХУК ОТ БИТРИКС24 ==========
@app.post("/bitrix_webhook")
async def bitrix_webhook(request: Request):
    try:
        data = await request.json()
        event = data.get("event")
        
        if event == "ONCRMDEALUPDATE":
            deal_id = data.get("data", {}).get("FIELDS", {}).get("ID")
            
            if deal_id and deal_id in user_deal_map:
                user_id = user_deal_map[deal_id]
                comment = await get_last_comment_from_deal(deal_id)
                if comment:
                    await send_message_to_max(user_id, f"📝 Ответ от менеджера:\n{comment}")
                    print(f"✅ Ответ отправлен клиенту {user_id}")
        
        return {"status": "ok"}
    except Exception as e:
        print(f"❌ Ошибка вебхука: {e}")
        return {"status": "error"}

# ========== ОБРАБОТЧИКИ MAX ==========
@dp.bot_started()
async def on_start(event):
    await event.bot.send_message(chat_id=event.chat_id, text="Напишите /start")

@dp.message_created()
async def handle(event):
    uid = event.from_user.user_id
    msg_id = event.message.body.mid
    if msg_id in processed:
        return
    processed.add(msg_id)

    text = event.message.body.text.strip().upper()

    if text == "/START":
        await event.message.answer(
            "🚗 Здравствуйте! Это бот Драйвер.\n\n"
            "Я помогу вам забронировать автомобиль.\n\n"
            "Для начала введите номер телефона:\n"
            "+7 999 123-45-67\n\n"
            "🔙 НАЗАД"
        )
        user_data[uid] = {"step": "phone"}
        return

    if uid not in user_data:
        return

    step = user_data[uid].get("step")

    if text == "НАЗАД":
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
        phone_clean = text.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if phone_clean.startswith(("+7", "8")):
            user_data[uid]["phone"] = text
            user_data[uid]["step"] = "name"
            await event.message.answer("📝 Введите ваше ФИО")
        else:
            await event.message.answer("❌ Неверный формат. Пример: +7 999 123-45-67")
        return

    if step == "name":
        if len(text.split()) >= 2:
            user_data[uid]["name"] = text
            user_data[uid]["step"] = "car_number"
            await event.message.answer("🚗 Введите номер ТС (например: Т731ХО797)")
        else:
            await event.message.answer("❌ Введите полное ФИО (минимум фамилия и имя)")
        return

    if step == "car_number":
        car_number = text.strip().upper()
        if car_number in VALID_CARS:
            car_model = VALID_CARS[car_number]
            user_data[uid]["car_number"] = car_number
            user_data[uid]["car_model"] = car_model
            await event.message.answer(
                f"📋 Проверьте данные:\n📞 {user_data[uid]['phone']}\n👤 {user_data[uid]['name']}\n🚗 {car_number} ({car_model})\n\n✅ СОГЛАСЕН\n🔙 НАЗАД"
            )
            user_data[uid]["step"] = "final"
        else:
            await event.message.answer("❌ Неверный номер ТС. Попробуйте снова:\n🚗 Введите номер ТС (например: Т731ХО797)")
        return

    if step == "final" and text == "СОГЛАСЕН":
        await event.message.answer(f"✅ Заявка отправлена!")
        await send_to_bitrix24(
            user_data[uid]['phone'],
            user_data[uid]['name'],
            user_data[uid]['car_number'],
            user_data[uid]['car_model'],
            uid
        )
        del user_data[uid]

@app.get("/")
async def root():
    return {"status": "ok"}

@app.get("/ping")
async def ping():
    return {"status": "alive"}

@app.get("/health")
async def health():
    return {"status": "ok"}

async def main():
    await bot.delete_webhook()
    asyncio.create_task(keep_alive())
    await dp.start_polling(bot)

threading.Thread(target=lambda: asyncio.run(main()), daemon=True).start()
print("🚀 Бот запущен")
