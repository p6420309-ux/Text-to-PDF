import telebot
from fpdf import FPDF
import matplotlib.pyplot as plt
import os
import re

# Telegram Bot Token setup
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# Function: Jo maths ke text ko image mein badlega
def text_to_math_image(text_line, filename):
    # Matplotlib setting taaki transparent aur clean background mile
    fig = plt.figure(figsize=(6.5, 0.6))
    fig.text(0.01, 0.5, text_line, fontsize=12, va='center', ha='left')
    
    # Bina borders ke save karna
    plt.savefig(filename, bbox_inches='tight', dpi=300, transparent=True)
    plt.close(fig)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "Welcome to Advanced Maths PDF Bot! 🧮📄\n\n"
        "Aap mujhe normal text ke sath-sath Mathematical Equations bhi bhej sakte hain.\n\n"
        "💡 **Maths Equation likhne ka tarika:**\n"
        "Apni equation ko dollar symbols `$` ke beech mein likhein (LaTeX format).\n\n"
        "**Example:**\n"
        "Solve this: $f(x) = \\frac{x^2 + 2x}{x - 1}$"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def process_message(message):
    chat_id = message.chat.id
    raw_text = message.text

    bot.reply_to(message, "Advanced PDF generate ho raha hai, please wait... ⏳")

    # PDF Initialize karna
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)

    # Line by line process karna
    lines = raw_text.split('\n')
    temp_files = []

    try:
        for idx, line in enumerate(lines):
            # Check karna ki line mein maths equation ($...$) hai ya nahi
            if '$' in line:
                # Agar maths hai toh uski image banayein
                img_name = f"math_{chat_id}_{idx}.png"
                text_to_math_image(line, img_name)
                temp_files.append(img_name)
                
                # Image ko PDF mein insert karna
                pdf.image(img_name, x=10, w=180)
                pdf.ln(2) # thoda sa gap
            else:
                # Agar normal text hai toh normal write karna
                if line.strip() == "":
                    pdf.ln(5) # Khali line ke liye space
                else:
                    pdf.multi_cell(0, 8, txt=line)
                    pdf.ln(2)

        # PDF save karna
        pdf_output = f"Math_Document_{chat_id}.pdf"
        pdf.output(pdf_output)

        # User ko send karna
        with open(pdf_output, 'rb') as pdf_file:
            bot.send_document(chat_id, pdf_file)

        # Cleanup: Saari temporary files delete karna
        os.remove(pdf_output)
        for img in temp_files:
            if os.path.exists(img):
                os.remove(img)

    except Exception as e:
        bot.reply_to(message, f"Oops! Kuch error aaya: {str(e)}")
        # Backup cleanup
        for img in temp_files:
            if os.path.exists(img): os.remove(img)

print("Advanced Bot dynamically running...")
bot.polling(none_stop=True)
