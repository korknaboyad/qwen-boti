import telebot
import requests
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
QWEN_API_KEY = os.environ.get("QWEN_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)
history = {}

@bot.message_handler(commands=["start"])
def start(m):
    bot.send_message(m.chat.id, "🤖 Привет! Я Qwen AI бот!")

@bot.message_handler(func=lambda m: True)
def handle(m):
    uid = m.from_user.id
    text = m.text
    
    if text.startswith("/"):
        return
    
    bot.send_chat_action(m.chat.id, "typing")
    
    if uid not in history:
        history[uid] = []
    history[uid].append({"role": "user", "content": text})
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {QWEN_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "qwen/qwen-2.5-72b-instruct",
        "messages": history[uid],
        "max_tokens": 500
    }
    
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=60)
        if r.status_code == 200:
            answer = r.json()["choices"][0]["message"]["content"]
            history[uid].append({"role": "assistant", "content": answer})
            bot.send_message(m.chat.id, answer)
        else:
            bot.send_message(m.chat.id, f"❌ Ошибка: {r.status_code}")
    except Exception as e:
        bot.send_message(m.chat.id, f"❌ Ошибка: {e}")

print("✅ Qwen бот запущен!")
bot.infinity_polling()
