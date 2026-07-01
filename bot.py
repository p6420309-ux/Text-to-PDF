import telebot
from fpdf import FPDF
import matplotlib.pyplot as plt
import os

# Telegram Bot Token setup
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# UPDATE 1: Image ke aas-paas ka extra space remove kiya gaya hai
def text_to_math_image(text_line, filename):
    fig = plt.figure()
    # Font size thoda bada rakha hai taaki clear dikhe
    fig.text(0, 0, text_line, fontsize=14, va='bottom', ha='left')
    
    # pad_inches=0.02 se extra transparent space cut ho jayega
    plt.savefig(filename, bbox_inches='tight', pad_inches=0.02, dpi=300, transparent=True)
    plt.close(fig)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "Welcome to Advanced Maths PDF Bot! 🧮📄\n\n"
        "Aap mujhe normal text ke sath-sath Mathematical Equations bhi bhej sakte hain.\n\n"
        "💡 **Maths Equation likhne ka tarika:**\n"
        "Apni equation ko dollar symbols `$` ke beech mein likhein.\n\n"
        "**Example:**\n"
        "Solve this: $f(x) = \\frac{x^2 + 2x}{x - 1}$"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def process_message(message):
    chat_id = message.chat.id
    raw_text = message.text

    bot.reply_to(message, "PDF generate ho raha hai, please wait... ⏳")

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
                
                # UPDATE 2: w=180 hata kar h=10 kar diya gaya hai!
                # Isse height text ke barabar ho jayegi aur width apne aap adjust hogi.
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

print("Bot with fixed math size is running...")
bot.polling(none_stop=True)
