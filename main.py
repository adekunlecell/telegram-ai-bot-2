import logging
import os
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# === CONFIG ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
USER_MEMORY = {}

# === LOGGER ===
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# === AI REPLY FUNCTION ===
def generate_reply(message: str) -> str:
    url = "https://api.together.xyz/inference"
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json",
    }

    prompt = f"""
    You are a helpful, witty AI assistant for crypto enthusiasts and gamers.
    User: {message}
    AI:
    """

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "max_tokens": 300,
        "temperature": 0.8,
        "top_k": 50,
        "top_p": 0.9,
        "repetition_penalty": 1.1,
        "stop": ["User:", "AI:"],
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json().get("output", "Hmm... didn't quite catch that.")
        elif response.status_code == 429:
            return "⚠️ I'm being rate-limited. Please slow down a little."
        else:
            return f"❌ API Error {response.status_code}: Please try again later."
    except Exception as e:
        return f"❌ Error contacting AI: {e}"

# === COMMAND HANDLERS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Yo! I'm your AI sidekick for all things crypto & gaming. Let's chat 💬🎮💸"
    )

async def myname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        name = " ".join(context.args)
        USER_MEMORY[update.effective_user.id] = name
        await update.message.reply_text(f"Cool! I'll remember your name as {name} 😎")
    else:
        await update.message.reply_text("Usage: /myname YourName")

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📩 Contact the developer:
Email: abdulrahmonadekunle7@gmail.com
WhatsApp: +2348148887864"
    )

async def crypto_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /price btc")
        return
    symbol = context.args[0].lower()
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if symbol in data:
                price = data[symbol]["usd"]
                await update.message.reply_text(f"💰 {symbol.upper()} price: ${price}")
            else:
                await update.message.reply_text(
                    "❌ Invalid symbol. Try something like btc or eth."
                )
        else:
            await update.message.reply_text("⚠️ Couldn't fetch price. Try again later.")
    except Exception as e:
        await update.message.reply_text(f"Error fetching price: {e}")

async def gaming_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://newsapi.org/v2/top-headlines?category=technology&q=gaming&apiKey=19e812f417cb4b9c8db14b9ab56f9c8d"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            articles = response.json().get("articles", [])[:3]
            if articles:
                reply = "🕹️ Top Gaming News:

"
                for article in articles:
                    title = article.get("title", "Untitled")
                    link = article.get("url", "")
                    reply += f"📰 *{title}*
{link}

"
                await update.message.reply_text(reply, parse_mode="Markdown")
            else:
                await update.message.reply_text("No gaming news found.")
        else:
            await update.message.reply_text("⚠️ Failed to fetch news.")
    except Exception as e:
        await update.message.reply_text(f"Error fetching news: {e}")

# === MAIN CHAT HANDLER ===
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text
    if user_id in USER_MEMORY:
        user_message = f"My name is {USER_MEMORY[user_id]}. {user_message}"
    await update.message.chat.send_action(action="typing")
    reply = generate_reply(user_message)
    await update.message.reply_text(reply)

# === MAIN FUNCTION ===
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("myname", myname))
    app.add_handler(CommandHandler("contact", contact))
    app.add_handler(CommandHandler("price", crypto_price))
    app.add_handler(CommandHandler("news", gaming_news))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
