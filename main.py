import os
import json
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "Token here"
Channel_Id = "channel link"


async def save_to_json(user, msg_type, content):
    data = {
        "user_id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "message_type": msg_type,
        "content": content,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    file_path = "user_messages.json"

    if os.path.exists(file_path):
        with open(file_path, "r+") as file:
            try:
                existing_data = json.load(file)
                existing_data.append(data)
            except json.JSONDecodeError:
                existing_data = [data]
            file.seek(0)
            json.dump(existing_data, file, indent=4)
    else:
        with open(file_path, "w") as file:
            json.dump([data], file, indent=4)


async def send_to_channel(update: Update, context: ContextTypes.DEFAULT_TYPE, msg_type: str):
    user = update.effective_user
    message = update.message

    caption = f"Muallif: {user.first_name}\nUsername: @{user.username or 'Anonim'}\nID: {user.id}"

    try:
        if msg_type == "text" and message.text:
            await save_to_json(user, "Text", message.text)
            await context.bot.send_message(chat_id=Channel_Id, text=f"{message.text}\n\n{caption}")
        elif msg_type == "photo" and message.photo:
            await save_to_json(user, "Photo", message.photo[-1].file_id)
            await context.bot.send_photo(chat_id=Channel_Id, photo=message.photo[-1].file_id, caption=caption)
        elif msg_type == "video" and message.video:
            await save_to_json(user, "Video", message.video.file_id)
            await context.bot.send_video(chat_id=Channel_Id, video=message.video.file_id, caption=caption)
        elif msg_type == "audio" and message.audio:
            audio = message.audio
            print(f"Audio object: {audio}")  # Log the full audio object
            audio_file_id = audio.file_id
            print(f"Audio file ID: {audio_file_id}")  # Log the audio file ID
            await save_to_json(user, "Audio", audio_file_id)
            await context.bot.send_audio(chat_id=Channel_Id, audio=audio_file_id, caption=caption)
        elif msg_type == "animation" and message.animation:
            animation_file_id = message.animation.file_id
            print(f"Animation received: {animation_file_id}")  # Debugging line
            await save_to_json(user, "Animation", animation_file_id)
            await context.bot.send_animation(chat_id=Channel_Id, animation=animation_file_id, caption=caption)
        else:
            await update.message.reply_text("Xabarni yuborishda xatolik yuz berdi yoki noto'g'ri format yuborildi.")
            return

        await update.message.reply_text("Xabar qabul qilindi.")

    except Exception as e:
        await update.message.reply_text(f"Xatolik yuz berdi: {str(e)}")


async def request_content(update: Update, context: ContextTypes.DEFAULT_TYPE, content_type: str):
    await update.message.reply_text(f"Iltimos, {content_type} yuboring.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Salom, {user.first_name}! Quyidagi buyruqlarni ishlatib kontent yuborishingiz mumkin:\n"
        "/text - Matn yuborish\n"
        "/photo - Rasm yuborish\n"
        "/video - Video yuborish\n"
        "/audio - Audio yuborish\n"
        "/animation - Animatsiya yuborish"
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await request_content(update, context, "matn")
    context.user_data["expected_type"] = "text"


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await request_content(update, context, "rasm")
    context.user_data["expected_type"] = "photo"


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await request_content(update, context, "video")
    context.user_data["expected_type"] = "video"


async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await request_content(update, context, "audio")
    context.user_data["expected_type"] = "audio"


async def handle_animation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await request_content(update, context, "animatsiya")
    context.user_data["expected_type"] = "animation"


async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    expected_type = context.user_data.get("expected_type")
    if expected_type:
        print(f"Expected media type: {expected_type}")  # Debugging line
        await send_to_channel(update, context, expected_type)
        del context.user_data["expected_type"]
    else:
        await update.message.reply_text("Iltimos, oldin buyruqni tanlang va ko'rsatmalarga amal qiling.")


app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("text", handle_text))
app.add_handler(CommandHandler("photo", handle_photo))
app.add_handler(CommandHandler("video", handle_video))
app.add_handler(CommandHandler("audio", handle_audio))
app.add_handler(CommandHandler("animation", handle_animation))

app.add_handler(MessageHandler(filters.ALL, process_message))

if __name__ == "__main__":
    print("Bot ishga tushdi...")
    app.run_polling()
