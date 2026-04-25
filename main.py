from keep_alive import keep_alive
keep_alive
import asyncio
import logging
import json
import csv
import io
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, WebAppInfo,
    InlineKeyboardMarkup, InlineKeyboardButton,
    BufferedInputFile
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

# ─── Налаштування ─────────────────────────────────────────────────────────────

TOKEN    = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
WEBAPP_URL = os.getenv("WEBAPP_URL")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

bot     = Bot(token=TOKEN)
storage = MemoryStorage()
dp      = Dispatcher(storage=storage)


# ─── Переклади ────────────────────────────────────────────────────────────────
TRANSLATIONS = {
    "uk": {
        "btn_calc":      "💰 Відкрити калькулятор",
        "btn_help":      "📖 Допомога",
        "btn_stats":     "📊 Статистика",
        "btn_feedback":  "✉️ Зворотній зв'язок",
        "btn_site":      "🌐 Відкрити сайт",
        "btn_dev":       "📩 Написати розробнику",
        "start_text":    "👋 Привіт, <b>{name}</b>!\n\nЯ допоможу тобі з фінансовими розрахунками.\nНатисни кнопку нижче, щоб відкрити калькулятор 👇",
        "help_text":     "📖 <b>Довідка</b>\n\n🔹 <b>Калькулятор</b> — відкриває веб-додаток для розрахунків\n🔹 <b>Статистика</b> — показує скільки разів ти користувався ботом\n🔹 <b>Зворотній зв'язок</b> — надіслати повідомлення розробнику\n\n<i>Версія: 1.0 | Розроблено з ❤️</i>",
        "stats_text":    "📊 <b>Твоя статистика</b>\n\n🔢 Запитів: <b>{count}</b>\n👥 Всього користувачів: <b>{total}</b>",
        "feedback_ask":  "✉️ Напиши своє повідомлення, і я його передам розробнику.\nАбо /cancel щоб скасувати.",
        "feedback_done": "✅ Дякую! Твоє повідомлення надіслано розробнику.",
        "cancelled":     "❌ Скасовано.",
        "contact_alert": "Напиши нам через кнопку «Зворотній зв'язок»!",
        "webapp_result": "📊 <b>Результат з калькулятора:</b>\n<pre>{data}</pre>",
        "webapp_raw":    "📊 <b>Отримано з калькулятора:</b>\n<code>{data}</code>",
        "fallback":      "🤔 Не розумію цю команду.\nСкористайся кнопками меню або введи /help",
        "lang_changed":  "✅ Мову змінено на українську 🇺🇦",
    },
    "en": {
        "btn_calc":      "💰 Open calculator",
        "btn_help":      "📖 Help",
        "btn_stats":     "📊 Statistics",
        "btn_feedback":  "✉️ Feedback",
        "btn_site":      "🌐 Open website",
        "btn_dev":       "📩 Contact developer",
        "start_text":    "👋 Hello, <b>{name}</b>!\n\nI will help you with financial calculations.\nPress the button below to open the calculator 👇",
        "help_text":     "📖 <b>Help</b>\n\n🔹 <b>Calculator</b> — opens the web app for calculations\n🔹 <b>Statistics</b> — shows how many times you used the bot\n🔹 <b>Feedback</b> — send a message to the developer\n\n<i>Version: 1.0 | Made with ❤️</i>",
        "stats_text":    "📊 <b>Your statistics</b>\n\n🔢 Requests: <b>{count}</b>\n👥 Total users: <b>{total}</b>",
        "feedback_ask":  "✉️ Write your message and I will forward it to the developer.\nOr /cancel to cancel.",
        "feedback_done": "✅ Thank you! Your message has been sent to the developer.",
        "cancelled":     "❌ Cancelled.",
        "contact_alert": "Write to us via the «Feedback» button!",
        "webapp_result": "📊 <b>Calculator result:</b>\n<pre>{data}</pre>",
        "webapp_raw":    "📊 <b>Received from calculator:</b>\n<code>{data}</code>",
        "fallback":      "🤔 I don't understand this command.\nUse the menu buttons or type /help",
        "lang_changed":  "✅ Language changed to English 🇬🇧",
    },
    "hu": {
        "btn_calc":      "💰 Számológép megnyitása",
        "btn_help":      "📖 Súgó",
        "btn_stats":     "📊 Statisztika",
        "btn_feedback":  "✉️ Visszajelzés",
        "btn_site":      "🌐 Weboldal megnyitása",
        "btn_dev":       "📩 Kapcsolat a fejlesztővel",
        "start_text":    "👋 Szia, <b>{name}</b>!\n\nSegítek a pénzügyi számításokban.\nNyomd meg az alábbi gombot a számológép megnyitásához 👇",
        "help_text":     "📖 <b>Súgó</b>\n\n🔹 <b>Számológép</b> — megnyitja a webalkalmazást\n🔹 <b>Statisztika</b> — megmutatja hányszor használtad a botot\n🔹 <b>Visszajelzés</b> — üzenet küldése a fejlesztőnek\n\n<i>Verzió: 1.0 | Szeretettel készítve ❤️</i>",
        "stats_text":    "📊 <b>Statisztikád</b>\n\n🔢 Kérések: <b>{count}</b>\n👥 Összes felhasználó: <b>{total}</b>",
        "feedback_ask":  "✉️ Írd meg az üzeneted, és továbbítom a fejlesztőnek.\nVagy /cancel a megszakításhoz.",
        "feedback_done": "✅ Köszönöm! Az üzeneted elküldve a fejlesztőnek.",
        "cancelled":     "❌ Megszakítva.",
        "contact_alert": "Írj nekünk a «Visszajelzés» gombbal!",
        "webapp_result": "📊 <b>Számológép eredménye:</b>\n<pre>{data}</pre>",
        "webapp_raw":    "📊 <b>Számológépből érkezett:</b>\n<code>{data}</code>",
        "fallback":      "🤔 Nem értem ezt a parancsot.\nHasználd a menügombokat vagy írd be: /help",
        "lang_changed":  "✅ A nyelv magyarra változott 🇭🇺",
    },
}

# ─── Сховище даних (in-memory) ────────────────────────────────────────────────
user_lang:     dict[int, str]   = {}  # uid -> "uk"/"en"/"hu"
usage_stats:   dict[int, int]   = {}  # uid -> кількість запитів
user_profiles: dict[int, dict]  = {}  # uid -> {name, username, lang, joined}
calc_history:  dict[int, list]  = {}  # uid -> [{timestamp, data}, ...]


def t(user_id: int, key: str, **kwargs) -> str:
    lang = user_lang.get(user_id, "uk")
    text = TRANSLATIONS[lang].get(key, key)
    return text.format(**kwargs) if kwargs else text

def get_lang(user_id: int) -> str:
    return user_lang.get(user_id, "uk")

def track_usage(user_id: int):
    usage_stats[user_id] = usage_stats.get(user_id, 0) + 1

def save_profile(user: types.User):
    if user.id not in user_profiles:
        user_profiles[user.id] = {
            "name":     user.full_name,
            "username": user.username or "—",
            "lang":     user_lang.get(user.id, "uk"),
            "joined":   datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    else:
        user_profiles[user.id]["lang"] = user_lang.get(user.id, "uk")

def save_calc_data(user_id: int, raw: str):
    if user_id not in calc_history:
        calc_history[user_id] = []
    calc_history[user_id].append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data": raw,
    })

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


# ─── FSM стани ────────────────────────────────────────────────────────────────
class BotState(StatesGroup):
    choosing_language    = State()
    waiting_for_feedback = State()


# ─── Клавіатури ───────────────────────────────────────────────────────────────
def lang_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🇺🇦 Українська", callback_data="lang_uk"),
        InlineKeyboardButton(text="🇬🇧 English",    callback_data="lang_en"),
        InlineKeyboardButton(text="🇭🇺 Magyar",     callback_data="lang_hu"),
    )
    return builder.as_markup()

def main_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text=t(user_id, "btn_calc"), web_app=WebAppInfo(url=WEBAPP_URL))
    )
    builder.row(
        KeyboardButton(text=t(user_id, "btn_help")),
        KeyboardButton(text=t(user_id, "btn_stats")),
    )
    builder.row(
        KeyboardButton(text=t(user_id, "btn_feedback"))
    )
    return builder.as_markup(resize_keyboard=True)

def help_inline_keyboard(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=t(user_id, "btn_site"), url=WEBAPP_URL))
    builder.row(InlineKeyboardButton(text=t(user_id, "btn_dev"), callback_data="contact_dev"))
    return builder.as_markup()

def admin_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="👥 Список користувачів", callback_data="adm_users"),
        InlineKeyboardButton(text="📈 Статистика",          callback_data="adm_stats"),
    )
    builder.row(
        InlineKeyboardButton(text="💾 Резервна копія JSON", callback_data="adm_backup_json"),
        InlineKeyboardButton(text="📋 Резервна копія CSV",  callback_data="adm_backup_csv"),
    )
    builder.row(
        InlineKeyboardButton(text="🗂 Дані калькулятора",   callback_data="adm_calc_all"),
    )
    return builder.as_markup()


# ─── /start ───────────────────────────────────────────────────────────────────
@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(BotState.choosing_language)
    await message.answer(
        "🌐 Оберіть мову / Choose language / Válasszon nyelvet:",
        reply_markup=lang_keyboard()
    )

@dp.callback_query(F.data.in_({"lang_uk", "lang_en", "lang_hu"}))
async def cb_set_language(callback: types.CallbackQuery, state: FSMContext):
    lang_map = {"lang_uk": "uk", "lang_en": "en", "lang_hu": "hu"}
    lang = lang_map[callback.data]
    uid  = callback.from_user.id
    user_lang[uid] = lang

    await state.clear()
    track_usage(uid)
    save_profile(callback.from_user)

    user_name = callback.from_user.first_name or "User"
    await callback.message.edit_text(t(uid, "lang_changed"))
    await callback.message.answer(
        t(uid, "start_text", name=user_name),
        parse_mode="HTML",
        reply_markup=main_keyboard(uid)
    )
    logger.info(f"Користувач {uid} обрав мову: {lang}")
    await callback.answer()


# ─── /language ────────────────────────────────────────────────────────────────
@dp.message(Command("language"))
async def cmd_language(message: types.Message, state: FSMContext):
    await state.set_state(BotState.choosing_language)
    await message.answer(
        "🌐 Оберіть мову / Choose language / Válasszon nyelvet:",
        reply_markup=lang_keyboard()
    )


# ─── /help ────────────────────────────────────────────────────────────────────
@dp.message(Command("help"))
async def cmd_help_command(message: types.Message):
    uid = message.from_user.id
    track_usage(uid)
    await message.answer(t(uid, "help_text"), parse_mode="HTML",
                         reply_markup=help_inline_keyboard(uid))


# ─── /admin ───────────────────────────────────────────────────────────────────
@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    uid = message.from_user.id
    if not is_admin(uid):
        await message.answer("⛔ Доступ заборонено.")
        return

    total_users = len(user_profiles)
    total_reqs  = sum(usage_stats.values())
    total_calcs = sum(len(v) for v in calc_history.values())

    text = (
        "🛠 <b>Адмін-панель</b>\n\n"
        f"👥 Користувачів: <b>{total_users}</b>\n"
        f"🔢 Всього запитів: <b>{total_reqs}</b>\n"
        f"💰 Розрахунків у калькуляторі: <b>{total_calcs}</b>\n\n"
        "Оберіть дію:"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=admin_keyboard())


# ─── Адмін callbacks ──────────────────────────────────────────────────────────
@dp.callback_query(F.data.startswith("adm_"))
async def admin_callbacks(callback: types.CallbackQuery):
    uid = callback.from_user.id
    if not is_admin(uid):
        await callback.answer("⛔ Доступ заборонено.", show_alert=True)
        return

    action = callback.data

    # ── Список користувачів ──────────────────────────────────────────────────
    if action == "adm_users":
        if not user_profiles:
            await callback.answer("Користувачів ще немає.", show_alert=True)
            return

        lines = ["👥 <b>Список користувачів:</b>\n"]
        for i, (uid_u, p) in enumerate(user_profiles.items(), 1):
            reqs  = usage_stats.get(uid_u, 0)
            calcs = len(calc_history.get(uid_u, []))
            flag  = {"uk": "🇺🇦", "en": "🇬🇧", "hu": "🇭🇺"}.get(p["lang"], "🌐")
            lines.append(
                f"{i}. {flag} <b>{p['name']}</b> (@{p['username']})\n"
                f"   ID: <code>{uid_u}</code> | 📅 {p['joined']}\n"
                f"   Запитів: {reqs} | Розрахунків: {calcs}"
            )

        text = "\n\n".join(lines)
        if len(text) <= 4096:
            await callback.message.answer(text, parse_mode="HTML")
        else:
            # Ділимо на частини якщо більше 4096 символів
            chunks, current = [], ""
            for line in lines:
                if len(current) + len(line) + 2 > 4000:
                    chunks.append(current)
                    current = line
                else:
                    current += "\n\n" + line
            chunks.append(current)
            for chunk in chunks:
                await callback.message.answer(chunk, parse_mode="HTML")

        await callback.answer()

    # ── Загальна статистика ──────────────────────────────────────────────────
    elif action == "adm_stats":
        total_users = len(user_profiles)
        total_reqs  = sum(usage_stats.values())
        total_calcs = sum(len(v) for v in calc_history.values())

        lang_counts = {"uk": 0, "en": 0, "hu": 0}
        for p in user_profiles.values():
            lang_counts[p.get("lang", "uk")] = lang_counts.get(p.get("lang", "uk"), 0) + 1

        top_users = sorted(usage_stats.items(), key=lambda x: x[1], reverse=True)[:5]
        top_lines = []
        for rank, (uid_u, cnt) in enumerate(top_users, 1):
            name = user_profiles.get(uid_u, {}).get("name", str(uid_u))
            top_lines.append(f"  {rank}. {name} — {cnt} запитів")

        text = (
            "📈 <b>Загальна статистика</b>\n\n"
            f"👥 Всього користувачів: <b>{total_users}</b>\n"
            f"🔢 Всього запитів: <b>{total_reqs}</b>\n"
            f"💰 Розрахунків: <b>{total_calcs}</b>\n\n"
            "🌍 <b>Мови:</b>\n"
            f"  🇺🇦 Українська: {lang_counts['uk']}\n"
            f"  🇬🇧 English: {lang_counts['en']}\n"
            f"  🇭🇺 Magyar: {lang_counts['hu']}\n\n"
            "🏆 <b>Топ-5 користувачів:</b>\n" +
            "\n".join(top_lines or ["  —"])
        )
        await callback.message.answer(text, parse_mode="HTML")
        await callback.answer()

    # ── Резервна копія JSON ──────────────────────────────────────────────────
    elif action == "adm_backup_json":
        backup = {
            "generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "users": {}
        }
        for uid_u, profile in user_profiles.items():
            backup["users"][str(uid_u)] = {
                "profile":      profile,
                "requests":     usage_stats.get(uid_u, 0),
                "calc_history": calc_history.get(uid_u, []),
            }

        raw   = json.dumps(backup, ensure_ascii=False, indent=2)
        fname = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        file  = BufferedInputFile(raw.encode("utf-8"), filename=fname)
        await callback.message.answer_document(
            file,
            caption=(
                f"💾 <b>Резервна копія JSON</b>\n"
                f"📅 {backup['generated']}\n"
                f"👥 Користувачів: {len(user_profiles)}"
            ),
            parse_mode="HTML"
        )
        await callback.answer()

    # ── Резервна копія CSV (список користувачів) ─────────────────────────────
    elif action == "adm_backup_csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Ім'я", "Username", "Мова", "Дата входу", "Запитів", "Розрахунків"])
        for uid_u, profile in user_profiles.items():
            writer.writerow([
                uid_u,
                profile["name"],
                profile["username"],
                profile["lang"],
                profile["joined"],
                usage_stats.get(uid_u, 0),
                len(calc_history.get(uid_u, [])),
            ])

        fname = f"users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        file  = BufferedInputFile(output.getvalue().encode("utf-8-sig"), filename=fname)
        await callback.message.answer_document(
            file,
            caption=f"📋 <b>Резервна копія CSV</b>\n👥 Користувачів: {len(user_profiles)}",
            parse_mode="HTML"
        )
        await callback.answer()

    # ── Дані калькулятора по всіх користувачах ───────────────────────────────
    elif action == "adm_calc_all":
        if not calc_history:
            await callback.answer("Даних калькулятора ще немає.", show_alert=True)
            return

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Ім'я", "Username", "Час", "Дані"])
        for uid_u, entries in calc_history.items():
            profile = user_profiles.get(uid_u, {})
            for entry in entries:
                writer.writerow([
                    uid_u,
                    profile.get("name", "—"),
                    profile.get("username", "—"),
                    entry["timestamp"],
                    entry["data"],
                ])

        total = sum(len(v) for v in calc_history.values())
        fname = f"calc_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        file  = BufferedInputFile(output.getvalue().encode("utf-8-sig"), filename=fname)
        await callback.message.answer_document(
            file,
            caption=(
                f"🗂 <b>Дані калькулятора</b>\n"
                f"💰 Розрахунків: {total}\n"
                f"👥 Користувачів: {len(calc_history)}"
            ),
            parse_mode="HTML"
        )
        await callback.answer()


# ─── Inline callbacks (звичайні) ──────────────────────────────────────────────
@dp.callback_query(F.data == "contact_dev")
async def cb_contact_dev(callback: types.CallbackQuery):
    uid = callback.from_user.id
    await callback.answer(t(uid, "contact_alert"), show_alert=True)


# ─── Головний роутер повідомлень ──────────────────────────────────────────────
@dp.message()
async def main_router(message: types.Message, state: FSMContext):
    uid = message.from_user.id

    # WebApp дані
    if message.web_app_data:
        track_usage(uid)
        save_profile(message.from_user)
        raw = message.web_app_data.data
        save_calc_data(uid, raw)
        logger.info(f"WebApp дані від {uid}: {raw}")
        try:
            parsed    = json.loads(raw)
            formatted = json.dumps(parsed, ensure_ascii=False, indent=2)
            await message.answer(t(uid, "webapp_result", data=formatted), parse_mode="HTML")
        except (json.JSONDecodeError, TypeError):
            await message.answer(t(uid, "webapp_raw", data=raw), parse_mode="HTML")
        return

    # FSM: очікування відгуку
    current_state = await state.get_state()
    if current_state == BotState.waiting_for_feedback.state:
        if message.text and message.text.startswith("/"):
            await state.clear()
            await message.answer(t(uid, "cancelled"), reply_markup=main_keyboard(uid))
        else:
            logger.info(f"Відгук від {uid}: {message.text}")
            await bot.send_message(
                ADMIN_ID,
                f"📩 Відгук від <b>{message.from_user.full_name}</b> "
                f"(@{message.from_user.username}, id: <code>{uid}</code>):\n\n{message.text}",
                parse_mode="HTML"
            )
            await state.clear()
            await message.answer(t(uid, "feedback_done"), reply_markup=main_keyboard(uid))
        return

    text = message.text or ""

    if text in [TRANSLATIONS[l]["btn_help"] for l in TRANSLATIONS]:
        track_usage(uid)
        await message.answer(t(uid, "help_text"), parse_mode="HTML",
                             reply_markup=help_inline_keyboard(uid))

    elif text in [TRANSLATIONS[l]["btn_stats"] for l in TRANSLATIONS]:
        track_usage(uid)
        count = usage_stats.get(uid, 0)
        total = len(usage_stats)
        await message.answer(t(uid, "stats_text", count=count, total=total), parse_mode="HTML")

    elif text in [TRANSLATIONS[l]["btn_feedback"] for l in TRANSLATIONS]:
        await state.set_state(BotState.waiting_for_feedback)
        await message.answer(t(uid, "feedback_ask"), parse_mode="HTML")

    else:
        await message.answer(t(uid, "fallback"), reply_markup=main_keyboard(uid))


# ─── Запуск ───────────────────────────────────────────────────────────────────
async def main():
    logger.info("Бот запускається...")
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())