import telebot
from fpdf import FPDF
import os
import requests
import urllib.parse
from flask import Flask
import threading

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is active!"

def text_to_math_image(text_line, filename):
    clean_math = text_line.replace('$', '').strip()
    encoded_math = urllib.parse.quote(clean_math)
    headers = {"User-Agent": "Mozilla/5.0"}
    url = f"https://latex.codecogs.com/png.image?\\dpi{{300}}\\bg{{white}} {encoded_math}"
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
        else:
            # Backup API
            backup_url = f"https://quickchart.io/latex?formula={encoded_math}&dpi=300&background=FFFFFF"
            resp2 = requests.get(backup_url, headers=headers, timeout=15)
            with open(filename, 'wb') as f:
                f.write(resp2.content)
    except Exception as e:
        raise Exception(f"Math Error: {str(e)}")

@bot.message_handler(func=lambda message: True)
def process_message(message):
    chat_id = message.chat.id
    raw_text = message.text
    bot.reply_to(message, "PDF generate ho raha hai... ⏳")

    pdf = FPDF()
    pdf.add_page()
    
    # Unicode Font add karna (Yeh jaruri hai error rokne ke liye)
    # FPDF2 mein ye automatic system font ya default unicode font leta hai
    pdf.set_font("Helvetica", size=12)

    lines = raw_text.split('\n')
    temp_files = []

    try:
        for idx, line in enumerate(lines):
            if '$' in line:
                img_name = f"math_{chat_id}_{idx}.png"
                text_to_math_image(line, img_name)
                temp_files.append(img_name)
                pdf.image(img_name, x=10, h=10)
                pdf.ln(2)
            else:
                # Text ko saaf karna (Unicode support ke liye)
                clean_line = line.encode('utf-8', 'ignore').decode('utf-8')
                if clean_line.strip() == "":
                    pdf.ln(5)
                else:
                    pdf.multi_cell(0, 8, txt=clean_line)
                    pdf.ln(2)

        pdf_output = f"Document_{chat_id}.pdf"
        pdf.output(pdf_output)

        with open(pdf_output, 'rb') as f:
            bot.send_document(chat_id, f)

        os.remove(pdf_output)
        for img in temp_files:
            if os.path.exists(img): os.remove(img)

    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")
        for img in temp_files:
            if os.path.exists(img): os.remove(img)

def run_bot():
    bot.polling(none_stop=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
