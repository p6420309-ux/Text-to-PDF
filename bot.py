import telebot
from fpdf import FPDF
import os

# Render environment variable se token fetch karna
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hello! Mujhe koi bhi text bhejo aur main use turant PDF mein convert kar dunga. 📄")

@bot.message_handler(func=lambda message: True)
def text_to_pdf(message):
    text = message.text
    chat_id = message.chat.id
    
    bot.reply_to(message, "PDF generate ho raha hai, please wait... ⏳")
    
    try:
        # PDF create karna
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Text ko multi-line format mein PDF mein likhna
        pdf.multi_cell(0, 10, txt=text)
        
        # Temporarily file ko save karna
        file_name = f"document_{chat_id}.pdf"
        pdf.output(file_name)
        
        # User ko PDF send karna
        with open(file_name, 'rb') as pdf_file:
            bot.send_document(chat_id, pdf_file)
            
        # Bhejne ke baad server se file delete kar dena (Space save karne ke liye)
        os.remove(file_name)
        
    except Exception as e:
        bot.reply_to(message, "Sorry, kuch error aa gaya. Kripya English letters/numbers ka hi use karein.")
        print(f"Error: {e}")

print("Bot successfully start ho gaya hai...")
bot.polling(none_stop=True)
