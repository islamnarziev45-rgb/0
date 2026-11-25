"""Tez VPN Telegram chat bot scaffold; never put secrets in this file."""
from __future__ import annotations

import json
import html
import os
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

BOT_TOKEN = os.environ.get("TEZ_BOT_TOKEN") or os.environ.get("BOT_TOKEN", "")
BOT_USERNAME = os.environ.get("TEZ_BOT_USERNAME", "")
API_BASE = os.environ.get("TEZ_BACKEND_URL", "").rstrip("/")
API_SECRET = os.environ.get("TEZ_BACKEND_SECRET", "")
SUPPORT_USERNAME = os.environ.get("TEZ_SUPPORT_USERNAME", "tbworstversion").lstrip("@")
TERMS_URL = os.environ.get("TEZ_TERMS_URL", "")
BANNER_URL = os.environ.get("TEZ_BANNER_URL", "")
DB_PATH = Path(os.environ.get("TEZ_DB_PATH", str(Path(__file__).resolve().parent / "tez.sqlite3")))
TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}"
BANNER_PATH = Path(os.environ.get("TEZ_BANNER_PATH", str(Path(__file__).resolve().parent / "assets" / "tez-welcome.png")))

LANGUAGES = ("ru", "tj", "uz", "ky")
T = {
    "ru": {
        "welcome": "Добро пожаловать в Tez VPN! ⚡\n\nБыстрое и надёжное подключение — без лишних шагов.",
        "features": "⚡ Быстрое подключение\n🔒 Защита соединения\n📱 До 2 устройств\n🌍 Серверные локации Tez VPN",
        "trial": "🎁 Пробный период", "buy": "💳 Купить / продлить", "subscription": "🔗 Моя подписка",
        "help": "❔ Помощь", "promo": "🎟 Промокод", "invite": "👥 Пригласить друга", "gift": "🎁 Подарить подписку",
        "terms": "📄 Пользовательское соглашение", "language": "🌐 Язык", "back": "↩ Назад",
        "trial_ready": "Пробный доступ активирован на 2 дня. Подробности и расход трафика — в разделе «Моя подписка».",
        "trial_unavailable": "Не удалось включить пробный доступ. Попробуй позже или напиши в поддержку.",
        "inactive": "Активной подписки пока нет.", "plans_title": "Выбери срок подписки:",
        "plan_1": "1 месяц — 150 ₽", "plan_3": "3 месяца — 399 ₽", "plan_6": "6 месяцев — 679 ₽",
        "payment_methods": "Выбери способ оплаты:", "main_payment": "Основной способ", "stars": "⭐ Telegram Stars",
        "payment_pending": "Платёжная система пока не подключена. Не отправляй деньги вручную.",
        "payment_created": "Ссылка на оплату готова. После оплаты вернись в бот и нажми «Проверить оплату».",
        "check_payment": "🔄 Проверить оплату", "payment_not_found": "Оплата пока не подтверждена. Если уже оплатил — подожди немного и проверь ещё раз.",
        "sub_status": "Статус: {status}\nДействует до: {expires}\nОсталось: {remaining}\nТрафик: {used} / {limit} ГБ\nУстройства: {devices}/2",
        "sub_no_key": "Ссылка подключения появится после выдачи доступа сервером.",
        "connect": "🔗 Подключиться", "devices": "📱 Мои устройства", "new_key": "♻ Перевыпустить ключ",
        "help_text": "Выбери тему — расскажу, что делать.", "help_connect": "Установи Happ или INCY. После активации открой свою ссылку подключения и добавь её в приложение.",
        "support_button": "💬 Написать в поддержку", "promo_prompt": "Отправь промокод одним сообщением.",
        "promo_ok": "Промокод применён.", "promo_bad": "Промокод не найден или уже использован.",
        "invite_title": "Твоя ссылка для друга:\n{link}\n\nЗа каждого нового приглашённого, который оплатит первую подписку, тебе добавится 3 дня. Здесь отображаются только подтверждённые приглашения.",
        "invite_stats": "Подтверждённых приглашённых: {count}\nНачислено бонусных дней: {days}",
        "gift_choose": "Выбери срок подписки в подарок:", "gift_pending": "Подарочный платёж пока недоступен.",
        "language_choose": "Выбери язык:", "lang_ru": "🇷🇺 Русский", "lang_tj": "🇹🇯 Тоҷикӣ", "lang_uz": "🇺🇿 O‘zbekcha", "lang_ky": "🇰🇬 Кыргызча",
        "terms_missing": "Пользовательское соглашение скоро появится.", "unknown": "Не понял сообщение. Выбери действие в меню ниже.",
        "server_unavailable": "Сервис пока не подключён. Пробный доступ и ключ заработают после настройки сервера Tez VPN."
    },
    "tj": {
        "welcome": "Ба Tez VPN хуш омадед! ⚡\n\nПайвасти зуд ва боэътимод — бе қадамҳои зиёдатӣ.",
        "features": "⚡ Пайвасти зуд\n🔒 Ҳифзи пайваст\n📱 То 2 дастгоҳ\n🌍 Ҷойгиршавиҳои Tez VPN",
        "trial": "🎁 Давраи озмоишӣ", "buy": "💳 Харидан / дароз кардан", "subscription": "🔗 Обунаи ман",
        "help": "❔ Кӯмак", "promo": "🎟 Рамзи тахфиф", "invite": "👥 Дӯстро даъват кун", "gift": "🎁 Обунаро ҳадя кун",
        "terms": "📄 Созишномаи корбар", "language": "🌐 Забон", "back": "↩ Бозгашт",
        "trial_ready": "Дастрасии озмоишӣ барои 2 рӯз фаъол шуд. Ҳолат ва трафикро дар бахши «Обунаи ман» бин.",
        "trial_unavailable": "Дастрасии озмоишӣ фаъол нашуд. Баъдтар кӯшиш кун ё ба дастгирӣ навис.",
        "inactive": "Обунаи фаъол нест.", "plans_title": "Муҳлати обунаро интихоб кун:",
        "plan_1": "1 моҳ — 150 ₽", "plan_3": "3 моҳ — 399 ₽", "plan_6": "6 моҳ — 679 ₽",
        "payment_methods": "Усули пардохтро интихоб кун:", "main_payment": "Усули асосӣ", "stars": "⭐ Telegram Stars",
        "payment_pending": "Пардохт ҳоло пайваст нест. Дастӣ пул нафирист.",
        "payment_created": "Пайванди пардохт омода аст. Пас аз пардохт ба бот баргард ва «Санҷидани пардохт»-ро пахш кун.",
        "check_payment": "🔄 Санҷидани пардохт", "payment_not_found": "Пардохт ҳоло тасдиқ нашудааст. Каме интизор шав ва дубора санҷ.",
        "sub_status": "Ҳолат: {status}\nТо: {expires}\nБоқӣ: {remaining}\nТрафик: {used} / {limit} ГБ\nДастгоҳҳо: {devices}/2",
        "sub_no_key": "Пайванди пайвастшавӣ баъди додани дастрасӣ пайдо мешавад.", "connect": "🔗 Пайваст шудан", "devices": "📱 Дастгоҳҳои ман", "new_key": "♻ Калидро нав кардан",
        "help_text": "Мавзӯъро интихоб кун — роҳнамоӣ мекунам.", "help_connect": "Happ ё INCY-ро насб кун. Баъди фаъолшавӣ пайванди шахсиро ба барнома илова кун.",
        "support_button": "💬 Ба дастгирӣ навис", "promo_prompt": "Рамзи тахфифро як паём фирист.", "promo_ok": "Рамз фаъол шуд.", "promo_bad": "Рамз ёфт нашуд ё истифода шудааст.",
        "invite_title": "Пайванди ту барои дӯст:\n{link}\n\nБарои ҳар дӯсти нав, ки обунаро бори аввал пардохт мекунад, 3 рӯз мегирӣ. Танҳо даъватҳои тасдиқшуда нишон дода мешаванд.",
        "invite_stats": "Дӯстони тасдиқшуда: {count}\nРӯзҳои бонусӣ: {days}", "gift_choose": "Муҳлати ҳадяро интихоб кун:", "gift_pending": "Пардохти ҳадя ҳоло дастрас нест.",
        "language_choose": "Забонро интихоб кун:", "lang_ru": "🇷🇺 Русский", "lang_tj": "🇹🇯 Тоҷикӣ", "lang_uz": "🇺🇿 O‘zbekcha", "lang_ky": "🇰🇬 Кыргызча",
        "terms_missing": "Созишнома ба зудӣ дастрас мешавад.", "unknown": "Амалиётро аз меню интихоб кун.", "server_unavailable": "Хизмат ҳоло пайваст нест. Дастрасӣ ва калид баъди танзими сервер фаъол мешаванд."
    },
    "uz": {
        "welcome": "Tez VPN’ga xush kelibsiz! ⚡\n\nTez va ishonchli ulanish — ortiqcha qadamlarsiz.",
        "features": "⚡ Tez ulanish\n🔒 Ulanish himoyasi\n📱 2 tagacha qurilma\n🌍 Tez VPN server joylashuvlari",
        "trial": "🎁 Sinov muddati", "buy": "💳 Xarid qilish / uzaytirish", "subscription": "🔗 Obunam",
        "help": "❔ Yordam", "promo": "🎟 Promokod", "invite": "👥 Do‘stni taklif qilish", "gift": "🎁 Obunani sovg‘a qilish",
        "terms": "📄 Foydalanuvchi kelishuvi", "language": "🌐 Til", "back": "↩ Orqaga",
        "trial_ready": "Sinov muddati 2 kunga faollashtirildi. Holat va trafikni «Obunam» bo‘limidan ko‘ring.",
        "trial_unavailable": "Sinov muddati faollashmadi. Keyinroq urinib ko‘ring yoki yordamga yozing.", "inactive": "Faol obuna yo‘q.",
        "plans_title": "Obuna muddatini tanlang:", "plan_1": "1 oy — 150 ₽", "plan_3": "3 oy — 399 ₽", "plan_6": "6 oy — 679 ₽",
        "payment_methods": "To‘lov usulini tanlang:", "main_payment": "Asosiy usul", "stars": "⭐ Telegram Stars", "payment_pending": "To‘lov hali ulanmagan. Qo‘lda pul yubormang.",
        "payment_created": "To‘lov havolasi tayyor. To‘lovdan so‘ng botga qaytib «To‘lovni tekshirish»ni bosing.", "check_payment": "🔄 To‘lovni tekshirish", "payment_not_found": "To‘lov hali tasdiqlanmadi. Biroz kutib, qayta tekshiring.",
        "sub_status": "Holat: {status}\nAmal qiladi: {expires}\nQoldi: {remaining}\nTrafik: {used} / {limit} GB\nQurilmalar: {devices}/2", "sub_no_key": "Ulanish havolasi server kirish bergach ko‘rinadi.",
        "connect": "🔗 Ulanish", "devices": "📱 Qurilmalarim", "new_key": "♻ Kalitni yangilash", "help_text": "Mavzuni tanlang — yo‘l-yo‘riq ko‘rsataman.",
        "help_connect": "Happ yoki INCY’ni o‘rnating. Kirish faollashgach, shaxsiy havolani ilovaga qo‘shing.", "support_button": "💬 Yordamga yozish", "promo_prompt": "Promokodni bitta xabar qilib yuboring.", "promo_ok": "Promokod qo‘llandi.", "promo_bad": "Promokod topilmadi yoki ishlatilgan.",
        "invite_title": "Do‘stingiz uchun havola:\n{link}\n\nBirinchi obunasini to‘lagan har bir yangi taklif qilingan do‘st uchun 3 kun bonus olasiz. Faqat tasdiqlangan takliflar ko‘rsatiladi.", "invite_stats": "Tasdiqlangan takliflar: {count}\nBonus kunlari: {days}",
        "gift_choose": "Sovg‘a obunasi muddatini tanlang:", "gift_pending": "Sovg‘a to‘lovi hozircha mavjud emas.", "language_choose": "Tilni tanlang:",
        "lang_ru": "🇷🇺 Русский", "lang_tj": "🇹🇯 Тоҷикӣ", "lang_uz": "🇺🇿 O‘zbekcha", "lang_ky": "🇰🇬 Кыргызча", "terms_missing": "Foydalanuvchi kelishuvi tez orada qo‘shiladi.", "unknown": "Menyudan amalni tanlang.", "server_unavailable": "Xizmat hali ulanmagan. Sinov va kalit server sozlangach ishga tushadi."
    },
    "ky": {
        "welcome": "Tez VPN’ге кош келиңиз! ⚡\n\nТез жана ишенимдүү байланыш — ашыкча кадамдарсыз.",
        "features": "⚡ Тез байланыш\n🔒 Байланышты коргоо\n📱 2 түзмөккө чейин\n🌍 Tez VPN серверлери",
        "trial": "🎁 Сыноо мөөнөтү", "buy": "💳 Сатып алуу / узартуу", "subscription": "🔗 Менин жазылуум",
        "help": "❔ Жардам", "promo": "🎟 Промокод", "invite": "👥 Дос чакыруу", "gift": "🎁 Жазылууну белек кылуу",
        "terms": "📄 Колдонуучу келишими", "language": "🌐 Тил", "back": "↩ Артка",
        "trial_ready": "Сыноо мүмкүнчүлүгү 2 күнгө иштетилди. Абалын жана трафикти «Менин жазылуум» бөлүмүнөн көр.", "trial_unavailable": "Сыноо иштеген жок. Кийин кайра аракет кыл же колдоого жаз.",
        "inactive": "Активдүү жазылуу жок.", "plans_title": "Жазылуу мөөнөтүн танда:", "plan_1": "1 ай — 150 ₽", "plan_3": "3 ай — 399 ₽", "plan_6": "6 ай — 679 ₽",
        "payment_methods": "Төлөм ыкмасын танда:", "main_payment": "Негизги ыкма", "stars": "⭐ Telegram Stars", "payment_pending": "Төлөм азырынча кошулган жок. Кол менен акча жөнөтпө.",
        "payment_created": "Төлөм шилтемеси даяр. Төлөгөндөн кийин ботко кайтып, «Төлөмдү текшерүү» бас.", "check_payment": "🔄 Төлөмдү текшерүү", "payment_not_found": "Төлөм азырынча ырасталган жок. Бир аз күтүп кайра текшер.",
        "sub_status": "Абалы: {status}\nМөөнөтү: {expires}\nКалды: {remaining}\nТрафик: {used} / {limit} ГБ\nТүзмөктөр: {devices}/2", "sub_no_key": "Сервер кирүү бергенден кийин байланыш шилтемеси көрүнөт.",
        "connect": "🔗 Туташуу", "devices": "📱 Менин түзмөктөрүм", "new_key": "♻ Ачкычты жаңылоо", "help_text": "Теманы танда — жардам берем.",
        "help_connect": "Happ же INCY орнот. Кирүү иштегенден кийин жеке шилтемени колдонмого кош.", "support_button": "💬 Колдоого жазуу", "promo_prompt": "Промокодду бир билдирүү кылып жөнөт.", "promo_ok": "Промокод кабыл алынды.", "promo_bad": "Промокод табылган жок же колдонулган.",
        "invite_title": "Досуңа жөнөтө турган шилтеме:\n{link}\n\nБиринчи жазылуусун төлөгөн ар бир жаңы дос үчүн 3 күн бонус аласың. Ырасталган чакыруулар гана көрсөтүлөт.", "invite_stats": "Ырасталган чакыруулар: {count}\nБонус күндөрү: {days}",
        "gift_choose": "Белек жазылуунун мөөнөтүн танда:", "gift_pending": "Белек төлөмү азырынча жеткиликсиз.", "language_choose": "Тилди танда:",
        "lang_ru": "🇷🇺 Русский", "lang_tj": "🇹🇯 Тоҷикӣ", "lang_uz": "🇺🇿 O‘zbekcha", "lang_ky": "🇰🇬 Кыргызча", "terms_missing": "Колдонуучу келишими кийин кошулат.", "unknown": "Төмөнкү менюдан аракетти танда.", "server_unavailable": "Кызмат азырынча туташкан жок. Сыноо менен ачкыч сервер орнотулгандан кийин иштейт."
    }
}

T["ru"].update({"help_renew":"🔗 Обновить / перевыпустить ключ","help_device":"📱 Второе устройство","help_referral":"👥 Реферальная программа","help_broken":"🛠 VPN не работает","help_other":"💬 Другой вопрос","help_device_text":"К подписке можно подключить до 2 устройств. Открой «Моя подписка», чтобы увидеть текущий статус.","gift_issued":"Подарок оплачен. Код для друга: {code}","payment_check_pending":"Платёж пока не подтверждён.","ref_unavailable":"Статистику приглашений пока не удалось загрузить."})
T["tj"].update({"help_renew":"🔗 Нав кардани калид","help_device":"📱 Дастгоҳи дуюм","help_referral":"👥 Барномаи даъват","help_broken":"🛠 VPN кор намекунад","help_other":"💬 Саволи дигар","help_device_text":"Ба обуна то 2 дастгоҳ пайваст мешавад. Барои дидани ҳолат «Обунаи ман»-ро кушо.","gift_issued":"Ҳадя пардохт шуд. Рамз барои дӯст: {code}","payment_check_pending":"Пардохт ҳоло тасдиқ нашудааст.","ref_unavailable":"Маълумоти даъватҳо ҳоло дастрас нест."})
T["uz"].update({"help_renew":"🔗 Kalitni yangilash","help_device":"📱 Ikkinchi qurilma","help_referral":"👥 Taklif dasturi","help_broken":"🛠 VPN ishlamayapti","help_other":"💬 Boshqa savol","help_device_text":"Obunaga 2 tagacha qurilma ulash mumkin. Holatni ko‘rish uchun «Obunam»ni oching.","gift_issued":"Sovg‘a to‘landi. Do‘stingiz uchun kod: {code}","payment_check_pending":"To‘lov hali tasdiqlanmadi.","ref_unavailable":"Taklif statistikasi hozircha yuklanmadi."})
T["ky"].update({"help_renew":"🔗 Ачкычты жаңылоо","help_device":"📱 Экинчи түзмөк","help_referral":"👥 Чакыруу программасы","help_broken":"🛠 VPN иштебейт","help_other":"💬 Башка суроо","help_device_text":"Жазылууга 2 түзмөккө чейин туташтырууга болот. Абалды көрүү үчүн «Менин жазылуумду» ач.","gift_issued":"Белек төлөндү. Досуңа берилчү код: {code}","payment_check_pending":"Төлөм азырынча ырасталган жок.","ref_unavailable":"Чакыруу статистикасы азырынча жүктөлгөн жок."})
for _lang, _text in {
    "ru":"Оплата подтверждена! Показываю активную подписку.",
    "tj":"Пардохт тасдиқ шуд! Обунаи фаъолро нишон медиҳам.",
    "uz":"To‘lov tasdiqlandi! Faol obunani ko‘rsataman.",
    "ky":"Төлөм ырасталды! Активдүү жазылууну көрсөтөм."
}.items(): T[_lang]["payment_confirmed"] = _text

def tr(lang: str, key: str, **values: object) -> str:
    text = T.get(lang, T["ru"]).get(key, T["ru"].get(key, key))
    return text.format(**values)

def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, lang TEXT NOT NULL, state TEXT NOT NULL DEFAULT '', joined_at TEXT NOT NULL)")
    conn.execute("CREATE TABLE IF NOT EXISTS referrals (invitee_id INTEGER PRIMARY KEY, inviter_id INTEGER NOT NULL, qualified INTEGER NOT NULL DEFAULT 0)")
    conn.commit()
    return conn

def tg(method: str, payload: dict[str, object] | None = None) -> dict[str, object]:
    if not BOT_TOKEN:
        raise RuntimeError("TEZ_BOT_TOKEN is not configured")
    data = json.dumps(payload or {}).encode()
    req = urllib.request.Request(f"{TG_API}/{method}", data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=40) as response:
        result = json.loads(response.read().decode())
    if not result.get("ok"):
        raise RuntimeError(f"Telegram {method} failed: {result.get('description', 'unknown error')}")
    return result["result"]

def backend(path: str, payload: dict[str, object] | None = None) -> dict[str, object] | None:
    if not API_BASE or not API_SECRET:
        return None
    url = API_BASE + path
    data = json.dumps(payload).encode() if payload is not None else None
    headers = {"Authorization": f"Bearer {API_SECRET}", "Content-Type": "application/json"}
    req = urllib.request.Request(url, data=data, headers=headers, method="POST" if data is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode())
    except (urllib.error.URLError, TimeoutError, ValueError):
        return None

def user_lang(user: dict[str, object], conn: sqlite3.Connection) -> str:
    row = conn.execute("SELECT lang FROM users WHERE user_id=?", (user["id"],)).fetchone()
    if row:
        return str(row["lang"])
    code = str(user.get("language_code", "ru")).lower()
    return "tj" if code.startswith("tg") else "uz" if code.startswith("uz") else "ky" if code.startswith("ky") else "ru"

def main_keyboard(lang: str) -> dict[str, object]:
    # Inline buttons stay attached to the branded welcome card. Telegram supports
    # success/primary styles for clear green purchase and blue subscription actions.
    rows = [
        [{"text":tr(lang,"trial"),"callback_data":"trial"}],
        [{"text":tr(lang,"buy"),"callback_data":"plans","style":"success"},
         {"text":tr(lang,"subscription"),"callback_data":"subscription","style":"primary"}],
        [{"text":tr(lang,"help"),"callback_data":"help"},{"text":tr(lang,"promo"),"callback_data":"promo"}],
        [{"text":tr(lang,"invite"),"callback_data":"invite"},{"text":tr(lang,"gift"),"callback_data":"gift"}],
        [{"text":tr(lang,"terms"),"callback_data":"terms"}],
        [{"text":tr(lang,"language"),"callback_data":"language"}],
    ]
    return inline(rows)

def inline(rows: list[list[dict[str, object]]]) -> dict[str, object]:
    return {"inline_keyboard": rows}

def send(chat_id: int, text: str, lang: str, markup: dict[str, object] | None = None, photo: bool = True) -> None:
    if photo and BANNER_PATH.is_file():
        boundary = f"----TezVPN{int(time.time()*1000)}"
        fields = {
            "chat_id": str(chat_id), "caption": text, "parse_mode": "HTML",
            "reply_markup": json.dumps(markup or main_keyboard(lang), ensure_ascii=False)
        }
        body = bytearray()
        for name, value in fields.items():
            body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode())
        body.extend(f"--{boundary}\r\nContent-Disposition: form-data; name=\"photo\"; filename=\"tez-welcome.png\"\r\nContent-Type: image/png\r\n\r\n".encode())
        body.extend(BANNER_PATH.read_bytes())
        body.extend(f"\r\n--{boundary}--\r\n".encode())
        request = urllib.request.Request(f"{TG_API}/sendPhoto", data=bytes(body), headers={"Content-Type":f"multipart/form-data; boundary={boundary}"})
        with urllib.request.urlopen(request, timeout=40) as response:
            result = json.loads(response.read().decode())
        if not result.get("ok"):
            raise RuntimeError("Telegram sendPhoto failed")
    elif photo and BANNER_URL:
        tg("sendPhoto", {"chat_id":chat_id,"photo":BANNER_URL,"caption":text,"reply_markup":markup or main_keyboard(lang),"parse_mode":"HTML"})
    else:
        tg("sendMessage", {"chat_id":chat_id,"text":text,"parse_mode":"HTML","reply_markup":markup or main_keyboard(lang),"disable_web_page_preview":True})

def start_message(chat_id: int, lang: str) -> None:
    send(chat_id, f"<b>Tez VPN</b>\n{tr(lang,'welcome')}\n\n{tr(lang,'features')}", lang)

def terms_keyboard(lang: str) -> dict[str, object]:
    return inline([[{"text":tr(lang,"lang_ru"),"callback_data":"lang:ru"},{"text":tr(lang,"lang_tj"),"callback_data":"lang:tj"}],
                   [{"text":tr(lang,"lang_uz"),"callback_data":"lang:uz"},{"text":tr(lang,"lang_ky"),"callback_data":"lang:ky"}]])

def show_plans(chat_id: int, lang: str, gift: bool = False) -> None:
    title = tr(lang,"gift_choose" if gift else "plans_title")
    rows = [[{"text":tr(lang,"plan_1"),"callback_data":f"{'gift' if gift else 'plan'}:month"}],
            [{"text":tr(lang,"plan_3"),"callback_data":f"{'gift' if gift else 'plan'}:quarter"}],
            [{"text":tr(lang,"plan_6"),"callback_data":f"{'gift' if gift else 'plan'}:halfYear"}],
            [{"text":tr(lang,"back"),"callback_data":"home"}]]
    send(chat_id, title, lang, inline(rows), photo=False)

def show_payment_methods(chat_id: int, lang: str, plan: str, gift: bool = False) -> None:
    rows = [[{"text":tr(lang,"main_payment"),"callback_data":f"pay:{plan}:main:{int(gift)}"}],
            [{"text":tr(lang,"stars"),"callback_data":f"pay:{plan}:stars:{int(gift)}"}],
            [{"text":tr(lang,"back"),"callback_data":"plans"}]]
    send(chat_id, tr(lang,"payment_methods"), lang, inline(rows), photo=False)

def show_subscription(chat_id: int, user_id: int, lang: str) -> None:
    data = backend(f"/api/me?telegram_id={user_id}")
    if data is None:
        send(chat_id,tr(lang,"server_unavailable"),lang,photo=False); return
    subscription = data.get("subscription")
    if not subscription:
        send(chat_id, tr(lang,"inactive"), lang, inline([[{"text":tr(lang,"trial"),"callback_data":"trial"}], [{"text":tr(lang,"buy"),"callback_data":"plans"}], [{"text":tr(lang,"back"),"callback_data":"home"}]]), photo=False)
        return
    # Backend values are user-facing HTML text; escape them before formatting.
    message = tr(lang,"sub_status", status=html.escape(str(subscription.get("status","active"))), expires=html.escape(str(subscription.get("expires_at","—"))), remaining=html.escape(str(subscription.get("remaining","—"))), used=html.escape(str(subscription.get("used_gb",0))), limit=html.escape(str(subscription.get("limit_gb",150))), devices=html.escape(str(subscription.get("devices",0))))
    link = subscription.get("subscription_url")
    if link:
        message += f"\n\n🔗 <code>{html.escape(str(link))}</code>"
    else:
        message += "\n\n" + tr(lang,"sub_no_key")
    rows = []
    if subscription.get("happ_url"):
        rows.append([{"text":"Открыть в Happ","url":subscription["happ_url"]}])
    if subscription.get("incy_url"):
        rows.append([{"text":"Открыть в INCY","url":subscription["incy_url"]}])
    rows += [[{"text":tr(lang,"devices"),"callback_data":"devices"}], [{"text":tr(lang,"new_key"),"callback_data":"newkey"}], [{"text":tr(lang,"buy"),"callback_data":"plans"}], [{"text":tr(lang,"back"),"callback_data":"home"}]]
    send(chat_id, message, lang, inline(rows), photo=False)

def show_referral(chat_id: int, user_id: int, lang: str) -> None:
    if not BOT_USERNAME:
        send(chat_id, tr(lang,"server_unavailable"), lang, photo=False)
        return
    link = f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"
    stats = backend(f"/api/referrals?telegram_id={user_id}")
    if stats is None:
        send(chat_id,tr(lang,"ref_unavailable"),lang,photo=False); return
    title = tr(lang,"invite_title", link=f"<code>{link}</code>") + "\n\n" + tr(lang,"invite_stats", count=stats.get("verified_count",0), days=stats.get("bonus_days",0))
    send(chat_id, title, lang, inline([[{"text":"↗ Поделиться ссылкой","url":f"https://t.me/share/url?url={urllib.parse.quote(link)}"}], [{"text":tr(lang,"back"),"callback_data":"home"}]]), photo=False)

def process_callback(query: dict[str, object], conn: sqlite3.Connection) -> None:
    data = str(query.get("data", "")); message = query.get("message", {})
    chat_id = int(message["chat"]["id"]); user = query["from"]; uid = int(user["id"])
    lang = user_lang(user, conn)
    tg("answerCallbackQuery", {"callback_query_id":query["id"]})
    if data.startswith("lang:"):
        lang = data.split(":")[1]
        if lang not in LANGUAGES:
            return
        conn.execute("UPDATE users SET lang=? WHERE user_id=?", (lang,uid)); conn.commit()
        start_message(chat_id, lang); return
    if data == "home": start_message(chat_id, lang); return
    if data == "subscription": show_subscription(chat_id,uid,lang); return
    if data == "help":
        send(chat_id,tr(lang,"help_text"),lang,inline([[{"text":tr(lang,"help_renew"),"callback_data":"help:renew"}],[{"text":tr(lang,"help_device"),"callback_data":"help:device"}],[{"text":tr(lang,"help_referral"),"callback_data":"help:referral"}],[{"text":tr(lang,"help_broken"),"callback_data":"help:broken"}],[{"text":tr(lang,"help_other"),"url":f"https://t.me/{SUPPORT_USERNAME}"}],[{"text":tr(lang,"language"),"callback_data":"language"}],[{"text":tr(lang,"back"),"callback_data":"home"}]]),photo=False)
        return
    if data == "invite": show_referral(chat_id,uid,lang); return
    if data == "gift": show_plans(chat_id,lang,gift=True); return
    if data == "terms":
        if TERMS_URL: send(chat_id,TERMS_URL,lang,inline([[{"text":tr(lang,"terms"),"url":TERMS_URL}]]),photo=False)
        else: send(chat_id,tr(lang,"terms_missing"),lang,photo=False)
        return
    if data == "language": send(chat_id,tr(lang,"language_choose"),lang,terms_keyboard(lang),photo=False); return
    if data == "plans": show_plans(chat_id,lang); return
    if data == "trial":
        result = backend("/api/trial", {"telegram_id":uid,"days":2,"limit_gb":3})
        if result and result.get("subscription"):
            send(chat_id,tr(lang,"trial_ready"),lang,photo=False); show_subscription(chat_id,uid,lang)
        else: send(chat_id,tr(lang,"server_unavailable" if not result else "trial_unavailable"),lang,photo=False)
        return
    if data.startswith("plan:") or data.startswith("gift:"):
        gift = data.startswith("gift:"); plan = data.split(":",1)[1]
        show_payment_methods(chat_id,lang,plan,gift); return
    if data.startswith("pay:"):
        _,plan,method,gift=data.split(":")
        result=backend("/api/payments",{"telegram_id":uid,"plan":plan,"method":method,"gift":gift=="1"})
        if result and result.get("checkout_url"):
            send(chat_id,tr(lang,"payment_created"),lang,inline([[{"text":"Оплатить","url":result["checkout_url"]}],[{"text":tr(lang,"check_payment"),"callback_data":"check_payment"}],[{"text":tr(lang,"back"),"callback_data":"home"}]]),photo=False)
        else: send(chat_id,tr(lang,"payment_pending"),lang,photo=False)
        return
    if data == "check_payment":
        result=backend("/api/payments/check",{"telegram_id":uid})
        if result and result.get("gift_code"):
            send(chat_id,tr(lang,"gift_issued",code=html.escape(str(result["gift_code"]))),lang,photo=False)
        elif result and result.get("subscription"):
            send(chat_id,tr(lang,"payment_confirmed"),lang,photo=False); show_subscription(chat_id,uid,lang)
        else:
            send(chat_id,tr(lang,"payment_check_pending"),lang,inline([[{"text":tr(lang,"check_payment"),"callback_data":"check_payment"}],[{"text":tr(lang,"back"),"callback_data":"home"}]]),photo=False)
        return
    if data.startswith("help:"):
        topic=data.split(":",1)[1]
        if topic == "renew": show_subscription(chat_id,uid,lang)
        elif topic == "device":
            response=backend(f"/api/me?telegram_id={uid}")
            if response is None: send(chat_id,tr(lang,"server_unavailable"),lang,photo=False); return
            count=((response).get("subscription") or {}).get("devices",0)
            send(chat_id,f"{tr(lang,'help_device_text')}\n\n{tr(lang,'devices')}: {count}/2",lang,photo=False)
        elif topic == "referral": show_referral(chat_id,uid,lang)
        else: send(chat_id,tr(lang,"help_connect"),lang,inline([[{"text":tr(lang,"support_button"),"url":f"https://t.me/{SUPPORT_USERNAME}"}],[{"text":tr(lang,"back"),"callback_data":"home"}]]),photo=False)
        return
    if data == "devices":
        response=backend(f"/api/me?telegram_id={uid}")
        if response is None: send(chat_id,tr(lang,"server_unavailable"),lang,photo=False); return
        sub=response.get("subscription") or {}
        send(chat_id,f"{tr(lang,'devices')}: {sub.get('devices',0)}/2\n\n{tr(lang,'help_device_text')}",lang,photo=False); return
    if data == "newkey":
        result=backend("/api/subscription/renew-key",{"telegram_id":uid})
        if result and result.get("subscription"):
            show_subscription(chat_id,uid,lang)
        else:
            send(chat_id,tr(lang,"server_unavailable" if not result else "trial_unavailable"),lang,photo=False)
        return
    if data == "promo":
        conn.execute("UPDATE users SET state='promo' WHERE user_id=?",(uid,)); conn.commit()
        send(chat_id,tr(lang,"promo_prompt"),lang,photo=False); return

def process_message(message: dict[str, object], conn: sqlite3.Connection) -> None:
    chat_id=int(message["chat"]["id"]); user=message["from"]; uid=int(user["id"]); text=str(message.get("text","")).strip()
    lang=user_lang(user,conn)
    existing=conn.execute("SELECT user_id,state,lang FROM users WHERE user_id=?",(uid,)).fetchone()
    if not existing:
        conn.execute("INSERT INTO users(user_id,lang,joined_at) VALUES(?,?,?)",(uid,lang,datetime.utcnow().isoformat())); conn.commit()
    else: lang=str(existing["lang"])
    if text.startswith("/start"):
        parts=text.split(maxsplit=1)
        if len(parts)>1 and parts[1].startswith("ref_"):
            try:
                inviter=int(parts[1][4:])
                if inviter != uid and not existing:
                    conn.execute("INSERT OR IGNORE INTO referrals(invitee_id,inviter_id) VALUES(?,?)",(uid,inviter)); conn.commit()
                    backend("/api/referrals/register",{"inviter_id":inviter,"invitee_id":uid})
            except ValueError: pass
        start_message(chat_id,lang); return
    if text == "/language" or text == tr(lang,"language"):
        send(chat_id,tr(lang,"language_choose"),lang,terms_keyboard(lang),photo=False); return
    if text == "/menu" or text == tr(lang,"back"):
        start_message(chat_id,lang); return
    if text == tr(lang,"trial"):
        result=backend("/api/trial",{"telegram_id":uid,"days":2,"limit_gb":3})
        if result and result.get("subscription"):
            send(chat_id,tr(lang,"trial_ready"),lang,photo=False); show_subscription(chat_id,uid,lang)
        else: send(chat_id,tr(lang,"server_unavailable" if not result else "trial_unavailable"),lang,photo=False)
        return
    if text == tr(lang,"buy"):
        show_plans(chat_id,lang); return
    if text == tr(lang,"subscription"):
        show_subscription(chat_id,uid,lang); return
    if text == tr(lang,"help"):
        send(chat_id,tr(lang,"help_text"),lang,inline([[{"text":tr(lang,"help_renew"),"callback_data":"help:renew"}],[{"text":tr(lang,"help_device"),"callback_data":"help:device"}],[{"text":tr(lang,"help_referral"),"callback_data":"help:referral"}],[{"text":tr(lang,"help_broken"),"callback_data":"help:broken"}],[{"text":tr(lang,"help_other"),"url":f"https://t.me/{SUPPORT_USERNAME}"}],[{"text":tr(lang,"language"),"callback_data":"language"}],[{"text":tr(lang,"back"),"callback_data":"home"}]]),photo=False); return
    if text == tr(lang,"promo"):
        conn.execute("UPDATE users SET state='promo' WHERE user_id=?",(uid,)); conn.commit(); send(chat_id,tr(lang,"promo_prompt"),lang,photo=False); return
    if text == tr(lang,"invite"):
        show_referral(chat_id,uid,lang); return
    if text == tr(lang,"gift"):
        show_plans(chat_id,lang,gift=True); return
    if text == tr(lang,"terms"):
        if TERMS_URL: send(chat_id,TERMS_URL,lang,inline([[{"text":tr(lang,"terms"),"url":TERMS_URL}]]),photo=False)
        else: send(chat_id,tr(lang,"terms_missing"),lang,photo=False)
        return
    state=str(existing["state"]) if existing else ""
    if state == "promo":
        result=backend("/api/promos/redeem",{"telegram_id":uid,"code":text})
        conn.execute("UPDATE users SET state='' WHERE user_id=?",(uid,)); conn.commit()
        send(chat_id,tr(lang,"promo_ok") if result and result.get("ok") else tr(lang,"promo_bad"),lang,photo=False); return
    send(chat_id,tr(lang,"unknown"),lang)

def main() -> None:
    if not BOT_TOKEN:
        raise SystemExit("Set TEZ_BOT_TOKEN in the server environment; do not paste it into source files.")
    conn=db(); offset=0
    print("Tez VPN chat bot polling started.")
    while True:
        try:
            updates=tg("getUpdates",{"offset":offset,"timeout":30,"allowed_updates":["message","callback_query"]})
            for update in updates:
                offset=int(update["update_id"])+1
                if "callback_query" in update: process_callback(update["callback_query"],conn)
                elif "message" in update: process_message(update["message"],conn)
        except KeyboardInterrupt: break
        except Exception as exc:
            if isinstance(exc, urllib.error.HTTPError):
                detail = f"Telegram API HTTP {exc.code}: {exc.reason}"
            elif isinstance(exc, urllib.error.URLError):
                detail = f"Telegram network error: {exc.reason}"
            else:
                detail = f"Bot loop error ({type(exc).__name__}): {exc}"
            print(f"{detail}; retrying.", flush=True)
            time.sleep(3)
    conn.close()

if __name__ == "__main__":
    main()

