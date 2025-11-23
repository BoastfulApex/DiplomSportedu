import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.colors import Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def generate_diploma_pdf(name, series):
    # diplom.pdf ni project papkasida saqlaymiz
    pdfmetrics.registerFont(TTFont('Palladio', 'palladio-bold.ttf'))
    
    output_pdf = os.path.join("diplom.pdf")

    # A4 ni landscape (albom) qilamiz
    page = landscape(A4)
    width, height = page
    

    c = canvas.Canvas(output_pdf, pagesize=page)

    # Shablon rasm joyi
    bg_path = os.path.join("shablon.png")

    if os.path.exists(bg_path):
        # Fon rasmi butun sahifaga joylashtiriladi
        c.drawImage(bg_path, 0, 0, width=width, height=height)
    else:
        print("⚠️ Shablon rasm topilmadi:", bg_path)

    # Siz bergan rang: RGBColor(0x4C, 0x7F, 0xBF)
    text_color = Color(0x4C / 255, 0x7F / 255, 0xBF / 255)  # Normalization
    c.setFillColor(text_color)
    
    # Matn markazga chiziladi
    c.setFont("Palladio", 32)
    c.drawCentredString(width / 2, height / 2 + 30, name)

    c.setFont("Palladio", 26)
    c.drawCentredString(width / 2, height / 2 + 90, series)

    c.save()
    return output_pdf


generate_diploma_pdf("John Doe", "AB123456")