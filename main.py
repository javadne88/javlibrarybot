from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ConversationHandler, CallbackContext
import json, os

BOT_TOKEN = "7498944853:AAEhV8PWIG44ZIOjd7MErM-DHt2rPzBTjmo"

# تابع راست‌چین‌کننده
def rtl(text):
    return '\u200F' + text

# مراحل مکالمه
(NAME, AUTHOR, TRANSLATOR, YEAR, SUBJECT, PLACE, STAGE, MATRIX, PHOTO, DESC) = range(10)

DATA_FILE = "books.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def start(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton(rtl("➕ افزودن کتاب جدید"), callback_data="add_book")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(rtl("سلام! به کتابخانه شخصی خوش آمدید."), reply_markup=reply_markup)

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    if query.data == "add_book":
        context.user_data["book"] = {}
        query.message.reply_text(rtl("نام کتاب؟"))
        return NAME

def receive_name(update, context):
    context.user_data["book"]["name"] = update.message.text
    update.message.reply_text(rtl("نام نویسنده؟"))
    return AUTHOR

def receive_author(update, context):
    context.user_data["book"]["author"] = update.message.text
    update.message.reply_text(rtl("نام مترجم؟"))
    return TRANSLATOR

def receive_translator(update, context):
    context.user_data["book"]["translator"] = update.message.text
    update.message.reply_text(rtl("سال چاپ؟"))
    return YEAR

def receive_year(update, context):
    context.user_data["book"]["year"] = update.message.text
    update.message.reply_text(rtl("موضوع کتاب؟"))
    return SUBJECT

def receive_subject(update, context):
    context.user_data["book"]["subject"] = update.message.text
    update.message.reply_text(rtl("محل خرید کتاب؟"))
    return PLACE

def receive_place(update, context):
    context.user_data["book"]["place"] = update.message.text
    update.message.reply_text(rtl("مرحله مطالعه؟ (مثلاً: خوانده شده، در حال مطالعه، نخوانده)"))
    return STAGE

def receive_stage(update, context):
    context.user_data["book"]["stage"] = update.message.text
    update.message.reply_text(rtl("ماتریس اهمیت/فوریت؟ (مثلاً: مهم و فوری)"))
    return MATRIX

def receive_matrix(update, context):
    context.user_data["book"]["matrix"] = update.message.text
    update.message.reply_text(rtl("لطفاً عکس جلد کتاب را ارسال کنید."))
    return PHOTO

def receive_photo(update, context):
    photo = update.message.photo[-1]
    file_id = photo.file_id
    context.user_data["book"]["photo_id"] = file_id
    update.message.reply_text(rtl("توضیحات کتاب؟"))
    return DESC

def receive_desc(update, context):
    context.user_data["book"]["description"] = update.message.text
    user_id = str(update.message.from_user.id)

    all_data = load_data()
    if user_id not in all_data:
        all_data[user_id] = []
    all_data[user_id].append(context.user_data["book"])
    save_data(all_data)

    update.message.reply_text(rtl("✅ کتاب با موفقیت ذخیره شد."))
    return ConversationHandler.END

def cancel(update, context):
    update.message.reply_text(rtl("عملیات لغو شد."))
    return ConversationHandler.END

if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler)],
        states={
            NAME: [MessageHandler(filters.TEXT, receive_name)],
            AUTHOR: [MessageHandler(filters.TEXT, receive_author)],
            TRANSLATOR: [MessageHandler(filters.TEXT, receive_translator)],
            YEAR: [MessageHandler(filters.TEXT, receive_year)],
            SUBJECT: [MessageHandler(filters.TEXT, receive_subject)],
            PLACE: [MessageHandler(filters.TEXT, receive_place)],
            STAGE: [MessageHandler(filters.TEXT, receive_stage)],
            MATRIX: [MessageHandler(filters.TEXT, receive_matrix)],
            PHOTO: [MessageHandler(filters.PHOTO, receive_photo)],
            DESC: [MessageHandler(filters.TEXT, receive_desc)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)

    print("🤖 ربات در حال اجراست...")
    app.run_polling()