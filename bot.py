import telebot
from fpdf import FPDF
import os
import requests
import urllib.parse

# Telegram Bot Token setup
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# UPDATE: Matplotlib hata kar QuickChart LaTeX API ka use
def text_to_math_image(text_line, filename):
    # $ sign hata kar sirf pure equation nikalna
    clean_math = text_line.replace('$', '').strip()
    
    # Text ko URL ke liye safe format mein encode karna
    encoded_math = urllib.parse.quote(clean_math)
    
    # QuickChart LaTeX API (Yeh har tarah ke math function support karti hai)
    url = f"https://quickchart.io/latex?formula={encoded_math}&dpi=300&background=FFFFFF"
    
    # Image download karke save karna
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
    else:
        raise Exception("API se equation render nahi ho payi.")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "Welcome to Advanced Maths PDF Bot! 🧮📄\n\n"
        "Aap mujhe normal text aur equations bhej sakte hain.\n"
        "**Note:** Math equation ko apni ek alag line mein `$` ke andar likhein."
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def process_message(message):
    chat_id = message.chat.id
    raw_text = message.text

    bot.reply_to(message, "Advanced PDF generate ho raha hai, please wait... ⏳")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)

    lines = raw_text.split('\n')
    temp_files = []

    try:
        for idx, line in enumerate(lines):
            if '$' in line:
                img_name = f"math_{chat_id}_{idx}.png"
                text_to_math_image(line, img_name)
                temp_files.append(img_name)
                
                # Image ko PDF mein lagana
                pdf.image(img_name, x=10, h=10)
                pdf.ln(2)
            else:
                if line.strip() == "":
                    pdf.ln(5)
                else:
                    pdf.multi_cell(0, 8, txt=line)
                    pdf.ln(2)

        pdf_output = f"Math_Document_{chat_id}.pdf"
        pdf.output(pdf_output)

        with open(pdf_output, 'rb') as pdf_file:
            bot.send_document(chat_id, pdf_file)

        os.remove(pdf_output)
        for img in temp_files:
            if os.path.exists(img):
                os.remove(img)

    except Exception as e:
        bot.reply_to(message, f"Oops! Kuch error aaya: {str(e)}")
        for img in temp_files:
            if os.path.exists(img): os.remove(img)

print("Bot with Powerful LaTeX API is running...")
bot.polling(none_stop=True)
