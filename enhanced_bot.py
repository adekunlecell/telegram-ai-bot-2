#!/usr/bin/env python3
import logging
import requests
import base64
from io import BytesIO
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Configuration
BOT_TOKEN = "8178415768:AAHzNHTBl_AUXupLr7RrFAhgEhhhfaEvRTI"
TOGETHER_API_KEY = "16d7cc269119c81c465bebd4af7c6f136b80c18014f18dc39997ce51efa8b263"
MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
USER_MEMORY = {}

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def generate_reply(message: str, user_id: int = None) -> str:
    """Generate AI response using Together API"""
    url = "https://api.together.xyz/inference"
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Add user memory context if available
    if user_id and user_id in USER_MEMORY:
        message = f"My name is {USER_MEMORY[user_id]}. {message}"
    
    prompt = f"""
You are a sharp, witty AI companion built for crypto traders and gamers.
Your style is casual, a bit meme-heavy, sometimes sarcastic, but very helpful.

You love talking about:
- Crypto trends, coins, security, NFTs
- Games, streamers, builds, patch notes
- Geeky tech stuff

Use casual slang, emojis, gaming/crypto references when relevant.
Stay helpful, but make it fun.

User: {message}
AI:
"""
    
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "max_tokens": 350,
        "temperature": 0.8,
        "top_k": 50,
        "top_p": 0.9,
        "repetition_penalty": 1.1,
        "stop": ["User:", "AI:"],
        "stream_tokens": False
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if "output" in result and "choices" in result["output"]:
                return result["output"]["choices"][0]["text"].strip()
            return result.get("output", "Sorry, I didn't quite catch that.")
        elif response.status_code == 429:
            return "I'm being rate limited. Let's slow down a bit."
        else:
            return f"Error {response.status_code}: Something went wrong."
    except Exception as e:
        logger.error(f"API Error: {e}")
        return "Sorry, I'm having connection issues right now."

def generate_image(prompt: str) -> bytes:
    """Generate image using Together AI"""
    try:
        url = "https://api.together.xyz/inference"
        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "black-forest-labs/FLUX.1-schnell-Free",
            "prompt": prompt,
            "width": 1024,
            "height": 1024,
            "steps": 4
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code == 200:
            result = response.json()
            if "output" in result and "choices" in result["output"]:
                image_data = result["output"]["choices"][0]["image_base64"]
                return base64.b64decode(image_data)
        raise Exception("Failed to generate image")
    except Exception as e:
        logger.error(f"Image generation error: {e}")
        raise Exception(f"Image generation failed: {str(e)}")

def generate_strategy(strategy_type: str, topic: str) -> str:
    """Generate gaming or crypto strategy"""
    url = "https://api.together.xyz/inference"
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    if strategy_type == "gaming":
        prompt = f"""
Create a detailed gaming strategy guide for {topic}. Include:
- Key tactics and techniques
- Common mistakes to avoid
- Pro tips and advanced strategies
- Meta considerations
- Resource management

Make it comprehensive but fun to read.

Topic: {topic}
Strategy Guide:
"""
    else:  # crypto
        prompt = f"""
Create a comprehensive crypto strategy analysis for {topic}. Include:
- Market analysis approach
- Risk management techniques
- Entry and exit strategies
- Technical indicators to watch
- Current market considerations

Keep it informative but accessible.

Topic: {topic}
Crypto Strategy:
"""
    
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "max_tokens": 500,
        "temperature": 0.7,
        "stop": ["Topic:", "Strategy Guide:", "Crypto Strategy:"]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if "output" in result and "choices" in result["output"]:
                return result["output"]["choices"][0]["text"].strip()
            return "Strategy generation failed."
        return "API error occurred."
    except Exception as e:
        return f"Error: {str(e)}"

def write_letter(letter_type: str, content: str) -> str:
    """Generate professional letters"""
    url = "https://api.together.xyz/inference"
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
Write a professional {letter_type} letter with the following details:
{content}

Make it formal, well-structured, and appropriate for business use.
Include proper formatting and tone.

Letter:
"""
    
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "max_tokens": 400,
        "temperature": 0.6,
        "stop": ["Letter:"]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if "output" in result and "choices" in result["output"]:
                return result["output"]["choices"][0]["text"].strip()
            return "Letter generation failed."
        return "API error occurred."
    except Exception as e:
        return f"Error: {str(e)}"

# Command Handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    if update.message:
        await update.message.reply_text(
            "Yo! I'm your AI sidekick for all things crypto & gaming. Let's chat 💬🎮💸"
        )

async def myname_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /myname command"""
    if update.message and update.effective_user:
        if context.args:
            name = " ".join(context.args)
            USER_MEMORY[update.effective_user.id] = name
            await update.message.reply_text(f"Got it! I'll remember your name as {name} 💾")
        else:
            await update.message.reply_text("Tell me your name like this: /myname John")

async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /contact command"""
    if update.message:
        contact_info = (
            "👨‍💻 Developer Contact Info\n"
            "Email: abdulrahmonadekunle7@gmail.com\n"
            "WhatsApp: +2348148887864"
        )
        await update.message.reply_text(contact_info)

async def crypto_price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /price command for crypto prices"""
    if update.message and update.effective_user:
        if not context.args:
            await update.message.reply_text("Usage: /price BTC")
            return
        
        symbol = context.args[0].lower()
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if symbol in data:
                    price = data[symbol]['usd']
                    await update.message.reply_text(f"💰 {symbol.upper()} price: ${price}")
                else:
                    await update.message.reply_text("Couldn't find that coin. Check spelling or try a different one.")
            else:
                await update.message.reply_text("API error. Try again later.")
        except Exception as e:
            await update.message.reply_text("Connection error. Try again later.")

async def gaming_news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /news command for gaming news"""
    if update.message:
        url = "https://newsapi.org/v2/top-headlines?category=technology&q=gaming&apiKey=19e812f417cb4b9c8db14b9ab56f9c8d"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                articles = response.json().get("articles", [])[:3]
                reply = "🕹️ Top Gaming News:\n"
                for article in articles:
                    reply += f"\n📰 {article['title']}\n{article['url']}\n"
                await update.message.reply_text(reply)
            else:
                await update.message.reply_text("Couldn't fetch gaming news. Try again later.")
        except Exception as e:
            await update.message.reply_text("Connection error. Try again later.")

async def image_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /image command for image generation"""
    if update.message and context.args:
        if not context.args:
            await update.message.reply_text("Usage: /image a futuristic gaming setup")
            return
        
        prompt = " ".join(context.args)
        await update.message.reply_text("🎨 Generating your image... This might take a moment!")
        
        try:
            image_data = generate_image(prompt)
            await update.message.reply_photo(photo=BytesIO(image_data), caption=f"Generated: {prompt}")
        except Exception as e:
            await update.message.reply_text("Sorry, couldn't generate the image. Try a different prompt.")

async def gaming_strategy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /gaming command for gaming strategies"""
    if update.message:
        if not context.args:
            await update.message.reply_text("Usage: /gaming League of Legends ADC")
            return
        
        topic = " ".join(context.args)
        await update.message.reply_text("🎮 Generating gaming strategy... Hold on!")
        
        strategy = generate_strategy("gaming", topic)
        await update.message.reply_text(f"🎮 Gaming Strategy for {topic}:\n\n{strategy}")

async def crypto_strategy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /crypto command for crypto strategies"""
    if update.message:
        if not context.args:
            await update.message.reply_text("Usage: /crypto Bitcoin trading")
            return
        
        topic = " ".join(context.args)
        await update.message.reply_text("💰 Generating crypto strategy... Hold on!")
        
        strategy = generate_strategy("crypto", topic)
        await update.message.reply_text(f"💰 Crypto Strategy for {topic}:\n\n{strategy}")

async def letter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /letter command for letter writing"""
    if update.message and context.args:
        if len(context.args) < 2:
            await update.message.reply_text("Usage: /letter cover job application for software engineer")
            return
        
        letter_type = context.args[0]
        content = " ".join(context.args[1:])
        await update.message.reply_text("Writing your letter... Please wait!")
        
        letter = write_letter(letter_type, content)
        await update.message.reply_text(f"{letter_type.title()} Letter:\n\n{letter}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages"""
    if update.message and update.message.text and update.effective_user:
        user_id = update.effective_user.id
        user_message = update.message.text
        
        logger.info(f"Received message: {user_message}")
        
        # Show typing indicator
        await update.message.chat.send_action(action="typing")
        
        # Generate and send reply
        reply = generate_reply(user_message, user_id)
        await update.message.reply_text(reply)

def main():
    """Start the bot"""
    print("🤖 Starting Enhanced Telegram AI Chat Bot...")
    
    # Create application
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("myname", myname_command))
    app.add_handler(CommandHandler("contact", contact_command))
    app.add_handler(CommandHandler("price", crypto_price_command))
    app.add_handler(CommandHandler("news", gaming_news_command))
    app.add_handler(CommandHandler("image", image_command))
    app.add_handler(CommandHandler("gaming", gaming_strategy_command))
    app.add_handler(CommandHandler("crypto", crypto_strategy_command))
    app.add_handler(CommandHandler("letter", letter_command))
    
    # Add message handler for regular chat
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Enhanced bot is ready with new features!")
    print("📱 Bot username: @Familytest2_bot")
    print("💬 Available commands:")
    print("  /start - Welcome message")
    print("  /myname <name> - Remember your name")
    print("  /contact - Developer contact info")
    print("  /price <crypto> - Get crypto prices")
    print("  /news - Latest gaming news")
    print("  /image <prompt> - Generate images")
    print("  /gaming <topic> - Gaming strategies")
    print("  /crypto <topic> - Crypto strategies")
    print("  /letter <type> <content> - Write letters")
    
    # Start polling
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Bot error: {e}")