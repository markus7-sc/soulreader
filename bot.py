from openai import OpenAI
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# === ТВОИ ДАННЫЕ ===
TELEGRAM_TOKEN = "8238447344:AAEGyx0vrzEJWnEUSUysN_Kzx9x_cldV4a0"
YANDEX_API_KEY = "AQVN0oAM9vpNkN_7DJf1xJIXT1MNWWRIPyptZctQ"
CATALOG_ID = "b1gun4bqv02fa2smeqbq"

client = OpenAI(
    api_key=YANDEX_API_KEY,
    base_url="https://rest-assistant.api.cloud.yandex.net/v1"
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup([["Попробовать"]], resize_keyboard=True)
    await update.message.reply_text(
        "Привет! 👋 Я Soulreader.\n\nНапиши своё имя — и я скажу, каким ты кажешься со стороны. 😏",
        reply_markup=keyboard
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ Просто напиши имя на русском — и получишь честный (но добрый) портрет.\n\n"
        "Команды:\n"
        "/start — начать заново\n"
        "/help — эта справка\n\n"
        "P.S. Можно просто нажать «Попробовать» 😉"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    if text == "Попробовать":
        await update.message.reply_text("Отлично! 💫 Напиши своё имя:")
        return

    if not (text.isalpha() and all('а' <= c.lower() <= 'я' or c == 'ё' for c in text)):
        await update.message.reply_text("Пожалуйста, пришли только имя на русском 🙏")
        return

    try:
        response = client.responses.create(
            model=f"gpt://{CATALOG_ID}/yandexgpt/latest",
            input=[{"role": "user", "content": f"Имя: {text}"}],
            instructions=(
                "Ты — стендап-комик в стиле Колбасенко. Опиши имя в 2 предложениях:\n"
                "1) Реалистичная ассоциация: известный человек, типаж или поведение в быту/работе.\n"
                "2) Жёсткая шутка с двойным дном, лёгкой пошлостью или сарказмом (без упоминания ориентации).\n"
                "Факты могут быть приукрашены, но не вымышлены полностью. "
                "Пиши на разговорном русском 2026 года. Добавь 1–2 эмодзи. Уложись в 250 символов."
            ),
            temperature=0.88,
            max_output_tokens=80
        )
        reply = response.output_text.strip()

        if len(reply) > 280:
            reply = reply[:277] + "..."

    except Exception as e:
        print(f"Ошибка Yandex: {e}")
        reply = f"{text}? Похоже, он уже знает, где ты живёшь... и чьи трусы лежат у тебя под кроватью. 😏"

    await update.message.reply_text(reply)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("restart", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Бот запущен с Yandex GPT!")
    app.run_polling()

if __name__ == "__main__":
    main()
