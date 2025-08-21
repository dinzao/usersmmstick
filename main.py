# --- ASCII баннер ---
ascii_banner = r"""
██╗░░░██╗░██████╗███████╗██████╗░░██████╗███╗░░░███╗███╗░░░███╗░██████╗████████╗██╗░█████╗░██╗░░██╗
██║░░░██║██╔════╝██╔════╝██╔══██╗██╔════╝████╗░████║████╗░████║██╔════╝╚══██╔══╝██║██╔══██╗██║░██╔╝
██║░░░██║╚█████╗░█████╗░░██████╔╝╚█████╗░██╔████╔██║██╔████╔██║╚█████╗░░░░██║░░░██║██║░░╚═╝█████═╝░
██║░░░██║░╚═══██╗██╔══╝░░██╔══██╗░╚═══██╗██║╚██╔╝██║██║╚██╔╝██║░╚═══██╗░░░██║░░░██║██║░░██╗██╔═██╗░
╚██████╔╝██████╔╝███████╗██║░░██║██████╔╝██║░╚═╝░██║██║░╚═╝░██║██████╔╝░░░██║░░░██║╚█████╔╝██║░╚██╗
░╚═════╝░╚═════╝░╚══════╝╚═╝░░╚═╝╚═════╝░╚═╝░░░░░╚═╝╚═╝░░░░░╚═╝╚═════╝░░░░╚═╝░░░╚═╝░╚════╝░╚═╝░░╚═╝
"""
print(ascii_banner)

# --- Подключение Telethon и другие импорты ---
from telethon import TelegramClient, events
import asyncio
import os

# === Чтение config.txt ===
CONFIG_FILE = "config.txt"

if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
        config = {}
        for line in lines:
            if "=" in line:
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()
    api_id = int(config.get("api_id", 0))
    api_hash = config.get("api_hash", "")
    phone = config.get("phone", "")
else:
    raise FileNotFoundError("❌ Файл config.txt не найден! Создай его рядом с ботом.")

if not api_id or not api_hash or not phone:
    raise ValueError("❌ Проверь config.txt — api_id, api_hash или phone пустые!")

# === Файлы для сохранения ===
WORDS_FILE = "words.txt"
STICKER_FILE = "sticker.txt"
OWNER_FILE = "owner.txt"

# === Функции для слов ===
def load_words():
    if os.path.exists(WORDS_FILE):
        with open(WORDS_FILE, "r", encoding="utf-8") as f:
            return [w.strip() for w in f.read().split(",") if w.strip()]
    return ["Привет", "Как", "Дячсаячс", "?"]

def save_words(words):
    with open(WORDS_FILE, "w", encoding="utf-8") as f:
        f.write(",".join(words))

# === Функции для ID стикера ===
def load_sticker_id():
    if os.path.exists(STICKER_FILE):
        with open(STICKER_FILE, "r", encoding="utf-8") as f:
            return int(f.read().strip())
    return 5287541904622245199  # дефолтный id

def save_sticker_id(sticker_id):
    with open(STICKER_FILE, "w", encoding="utf-8") as f:
        f.write(str(sticker_id))

# === Функции для Owner ID ===
def load_owner_id():
    if os.path.exists(OWNER_FILE):
        with open(OWNER_FILE, "r", encoding="utf-8") as f:
            return int(f.read().strip())
    return 0

def save_owner_id(owner_id):
    with open(OWNER_FILE, "w", encoding="utf-8") as f:
        f.write(str(owner_id))

# Загружаем данные при старте
WORDS = load_words()
TARGET_STICKER_ID = load_sticker_id()
OWNER_ID = load_owner_id()

client = TelegramClient("my_userbot", api_id, api_hash)

# === Обработчик новых сообщений ===
@client.on(events.NewMessage)
async def handler(event):
    global WORDS, TARGET_STICKER_ID, OWNER_ID
    msg = event.message

    # Игнорируем всех, кроме овнера
    if msg.sender_id != OWNER_ID:
        return

    # --- .setwords ---
    if msg.raw_text and msg.raw_text.startswith(".setwords"):
        new_words_str = msg.raw_text[len(".setwords"):].strip()
        if new_words_str:
            WORDS = [w.strip() for w in new_words_str.split(",") if w.strip()]
            save_words(WORDS)
            await event.respond(f"✅ Слова обновлены: {', '.join(WORDS)}")
        else:
            await event.respond("⚠️ Напиши слова через запятую после команды!")
        return

    # --- .setstickerid ---
    if msg.raw_text and msg.raw_text.startswith(".setstickerid"):
        new_id_str = msg.raw_text[len(".setstickerid"):].strip()
        if new_id_str.isdigit():
            TARGET_STICKER_ID = int(new_id_str)
            save_sticker_id(TARGET_STICKER_ID)
            await event.respond(f"✅ Sticker ID обновлён: {TARGET_STICKER_ID}")
        else:
            await event.respond("⚠️ Укажи правильный числовой ID!")
        return

    # --- .stickerid ---
    if msg.raw_text and msg.raw_text.startswith(".stickerid"):
        reply = await event.get_reply_message()
        if reply and reply.sticker:
            sticker_id = reply.media.document.id
            await event.respond(f"🆔 ID этого стикера: `{sticker_id}`")
        else:
            await event.respond("⚠️ Ответь этой командой на стикер!")
        return

    # --- Реакция на стикер ---
    if msg.sticker:
        doc = msg.media.document
        if doc.id == TARGET_STICKER_ID:
            print("✅ Получен стикер c нужным id!")
            for word in WORDS:
                await event.respond(word)  
                await asyncio.sleep(0.1)

# === Запуск ===
async def main():
    global OWNER_ID

    await client.start(phone)
    me = await client.get_me()

    # Если OWNER_ID ещё не сохранён — устанавливаем его
    if OWNER_ID == 0:
        OWNER_ID = me.id
        save_owner_id(OWNER_ID)

    # Отправляем приветственное сообщение при КАЖДОМ запуске
    await client.send_message(
        OWNER_ID,
        "<b>🎉 Usersmmstick Был Успешно Запущен\n\n"
        f"👑 Твой Owner Id: {OWNER_ID}\n\n"
        "✅ Доступные команды:\n"
        "<blockquote>"
        ".setwords  - \"слово 1, слово 2, слово 3, и т.д\"\n"
        ".stickerid  - ответь на сообщение и скрипт напишет id этого стикера (понадобится для команды .setstickerid)\n"
        ".setstickerid  - \"Id стикера\"  После, сообщения будут написано только в случае отправки стикера с этим id"
        "</blockquote>\n\n"
        "| Made by @oesxzu | ❤️</b>",
        parse_mode="html"
    )

    print("✅ Юзербот запущен! Проверяй сообщения в ЛС.")
    await client.run_until_disconnected()

if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
