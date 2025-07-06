import logging
import re
import json
import time
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

TOKEN = os.environ.get("TELEGRAM_TOKEN")

logging.basicConfig(level=logging.INFO)

def get_simple_earn_offers():
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        driver.get("https://www.binance.com/en/earn/simple-earn")
        time.sleep(7)

        page_source = driver.page_source
        driver.quit()

        match = re.search(r'window\.__APP_DATA__\s*=\s*({.*?})\s*;', page_source, re.DOTALL)
        if not match:
            return "❌ فشل في إيجاد البيانات من الصفحة."

        json_data = json.loads(match.group(1))
        products = json_data["pageData"]["data"]["earnSimpleProducts"]

        if not products:
            return "❌ لا توجد بيانات حالياً."

        message = "📊 *عروض Simple Earn على Binance:*\n\n"
        for product in products[:10]:
            asset = product.get("asset", "")
            apr = product.get("apy", 0) * 100
            duration = product.get("duration", "مرن")
            message += f"🔹 *{asset}* | APR: *{apr:.2f}%* | المدة: `{duration}`\n"

        return message

    except Exception as e:
        return f"⚠️ خطأ أثناء استخدام Selenium:\n{str(e)}"

def simpleearn_command(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    update.message.reply_text("🔄 جاري جلب عروض Simple Earn...")
    message = get_simple_earn_offers()
    context.bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("simpleearn", simpleearn_command))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
