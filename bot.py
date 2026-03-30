import logging
import os
import random
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
)

TOKEN = os.getenv("TOKEN")
ALLOWED_USER_ID = 8150629289
ASSETS = ["EURUSD", "GBPUSD", "AUDCAD", "BTCUSDT"]

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

user_modes = {}
auto_enabled = {}

def main_keyboard(user_id: int):
    mode = user_modes.get(user_id, "precise")
    auto = auto_enabled.get(user_id, True)

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"{'✅ ' if mode == 'fast' else ''}Быстрый",
                callback_data="mode_fast"
            ),
            InlineKeyboardButton(
                f"{'✅ ' if mode == 'precise' else ''}Точный",
                callback_data="mode_precise"
            ),
        ],
        [InlineKeyboardButton("🎯 Получить сигнал", callback_data="get_signal")],
        [
            InlineKeyboardButton(
                f"{'🔔 Авто: ВКЛ' if auto else '🔕 Авто: ВЫКЛ'}",
                callback_data="toggle_auto"
            )
        ],
        [InlineKeyboardButton("📊 Статус", callback_data="status")]
    ])

def is_allowed(update: Update) -> bool:
    user = update.effective_user
    return bool(user and user.id == ALLOWED_USER_ID)

def generate_signal(mode: str) -> str:
    asset = random.choice(ASSETS)

    if mode == "fast":
        score = random.randint(6, 9)
        direction = random.choice(["ВВЕРХ", "ВНИЗ"])
        entry = random.choice(["сейчас", "ждать 1 свечу"])
        expiry = random.choice(["1 минута", "2 минуты"])
        reason = random.choice([
            "импульс по 1М",
            "быстрый отскок от уровня",
            "RSI подтверждает импульс",
            "движение по локальному тренду",
        ])
    else:
        score = random.randint(8, 10)
        direction = random.choice(["ВВЕРХ", "ВНИЗ"])
        entry = random.choice(["сейчас", "ждать подтверждение"])
        expiry = random.choice(["3 минуты", "5 минут"])
        reason = random.choice([
            "совпадение 1М и 5М",
            "тренд + RSI + уровень",
            "подтверждающая свеча",
            "сильный чистый импульс",
        ])

    no_signal_chance = 0.35 if mode == "precise" else 0.2
    if random.random() < no_signal_chance:
        return "Нет хорошего входа, жди."

    return (
        f"📊 Актив: {asset}\n"
        f"📈 Направление: {direction}\n"
        f"⏱ Вход: {entry}\n"
        f"⌛ Время сделки: {expiry}\n"
        f"🔥 Сила сигнала: {score}/10\n"
        f"🧠 Режим: {'Быстрый' if mode == 'fast' else 'Точный'}\n"
        f"📍 Причина: {reason}"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        return

    user_id = update.effective_user.id
    user_modes.setdefault(user_id, "precise")
    auto_enabled.setdefault(user_id, True)

    text = (
        "🤖 Бот запущен.\n\n"
        "Выбирай режим и жми «Получить сигнал».\n"
        "Бот работает только для тебя."
    )

    await update.message.reply_text(
        text,
        reply_markup=main_keyboard(user_id)
    )

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        return

    user_id = update.effective_user.id
    mode = user_modes.get(user_id, "precise")

    await update.message.reply_text(
        generate_signal(mode),
        reply_markup=main_keyboard(user_id)
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        return

    user_id = update.effective_user.id
    mode = user_modes.get(user_id, "precise")
    auto = auto_enabled.get(user_id, True)

    text = (
        f"📊 Статус бота\n\n"
        f"Режим: {'Быстрый' if mode == 'fast' else 'Точный'}\n"
        f"Автоуведомления: {'ВКЛ' if auto else 'ВЫКЛ'}\n"
        f"Активы: {', '.join(ASSETS)}"
    )

    await update.message.reply_text(
        text,
        reply_markup=main_keyboard(user_id)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ALLOWED_USER_ID:
        return

    user_id = query.from_user.id
    data = query.data

    user_modes.setdefault(user_id, "precise")
    auto_enabled.setdefault(user_id, True)

    if data == "mode_fast":
        user_modes[user_id] = "fast"
        await query.message.reply_text(
            "⚡ Режим переключен: Быстрый",
            reply_markup=main_keyboard(user_id)
        )

    elif data == "mode_precise":
        user_modes[user_id] = "precise"
        await query.message.reply_text(
            "🎯 Режим переключен: Точный",
            reply_markup=main_keyboard(user_id)
        )

    elif data == "get_signal":
        mode = user_modes.get(user_id, "precise")
        await query.message.reply_text(
            generate_signal(mode),
            reply_markup=main_keyboard(user_id)
        )

    elif data == "toggle_auto":
        auto_enabled[user_id] = not auto_enabled.get(user_id, True)
        await query.message.reply_text(
            f"{'🔔 Автоуведомления включены' if auto_enabled[user_id] else '🔕 Автоуведомления выключены'}",
            reply_markup=main_keyboard(user_id)
        )

    elif data == "status":
        mode = user_modes.get(user_id, "precise")
        auto = auto_enabled.get(user_id, True)

        text = (
            f"📊 Статус бота\n\n"
            f"Режим: {'Быстрый' if mode == 'fast' else 'Точный'}\n"
            f"Автоуведомления: {'ВКЛ' if auto else 'ВЫКЛ'}\n"
            f"Активы: {', '.join(ASSETS)}"
        )

        await query.message.reply_text(
            text,
            reply_markup=main_keyboard(user_id)
        )

async def auto_signal_job(context: ContextTypes.DEFAULT_TYPE):
    user_id = ALLOWED_USER_ID
    if not auto_enabled.get(user_id, True):
        return

    mode = user_modes.get(user_id, "precise")
    text = "🔔 Автосигнал\n\n" + generate_signal(mode)

    await context.bot.send_message(
        chat_id=user_id,
        text=text,
        reply_markup=main_keyboard(user_id)
    )

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal", signal))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.job_queue.run_repeating(auto_signal_job, interval=900, first=30)

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
