from docx import Document
from docx2pdf import convert
import tempfile
import os
import shutil
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
import os
import tempfile
from datetime import date


def generate_diploma_pdf(name, series):
    output_pdf="diplom.pdf"
    # 1. Word shablonni ochamiz
    doc = Document('diploma_template.docx')

    # 2. Joylarni almashtiramiz
    for p in doc.paragraphs:
        if "{{Name}}" in p.text:
            p.text = p.text.replace("{{Name}}", name)
            for run in p.runs:
                run.font.name = "Palladio"
                run.font.size = Pt(24)
                run.font.color.rgb = RGBColor(0x4C, 0x7F, 0xBF)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER

        if "{{Seria}}" in p.text:
            p.text = p.text.replace("{{Seria}}", series)
            for run in p.runs:
                run.font.name = "Arial"
                run.bold = True
                run.font.size = Pt(30)
                run.font.color.rgb = RGBColor(0x4C, 0x7F, 0xBF)

    # 3. Vaqtinchalik fayl nomi (ochiq holda emas!)
    temp_docx_path = os.path.join(tempfile.gettempdir(), f"{series}.docx")
    doc.save(temp_docx_path)

    # 4. Vaqtinchalik chiqish papkasi
    temp_output_dir = tempfile.mkdtemp()

    # 5. Word -> PDF konvertatsiya
    convert(temp_docx_path, temp_output_dir)

    # 6. Hosil bo‘lgan PDF faylni topamiz
    pdf_file = os.path.join(
        temp_output_dir, os.path.basename(temp_docx_path).replace(".docx", ".pdf")
    )

    # 7. PDF ni kerakli joyga ko‘chiramiz
    shutil.move(pdf_file, output_pdf)

    # 8. Endi vaqtinchalik faylni o‘chirish xavfsiz
    try:
        os.remove(temp_docx_path)
    except PermissionError:
        pass  # Word hali yopilmagan bo‘lsa, bu xato muhim emas

    print(f"✅ Diplom tayyor: {os.path.abspath(output_pdf)}")
import os
from datetime import date
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.colors import Color
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.colors import HexColor  # qo'shish kerak

def generate_sport_diploma_pdf(
    full_name: str,
    sport_type: str,
    position: str,  # 1,2,3 kabi raqam kiradi
    series: str,
    competition_date: date,
    template_image_path: str = "sertifikat.png",
    output_pdf_path: str = "diplom.pdf"
):
    # Fontni ro'yxatga qo'shish
    pdfmetrics.registerFont(TTFont('Palladio', 'palladio-bold.ttf'))
    pdfmetrics.registerFont(TTFont('Arimo-Bold', 'Arimo-Bold.ttf'))

    # Sahifa o'lchami
    page = landscape(A4)
    width, height = page

    # Canvas yaratish
    c = canvas.Canvas(output_pdf_path, pagesize=page)

    # Fon shablon rasm
    if os.path.exists(template_image_path):
        c.drawImage(template_image_path, 0, 0, width=width, height=height)
    else:
        print("⚠️ Shablon rasm topilmadi:", template_image_path)

    # Matn rangi
    text_color = HexColor("#042a6a")  # chuqur ko‘k
    c.setFillColor(text_color)

    # Full name
    c.setFont("Palladio", 32)
    c.drawCentredString(width / 2, height / 2 -30, full_name)

    c.setFont("Arimo-Bold", 13)

    # Matn uzunligini tekshirish
    sport_text = sport_type.upper()
    offset = 0
    if len(sport_text) > 5:
        offset = (len(sport_text) - 5) * 5  # har bir ortiqcha harf uchun 5 point chapga

    # drawCentredString bilan chapga surish
    c.drawCentredString(width / 2 - 160 + offset, height / 2 + 36, sport_text)

    pos_map = {"1": "BIRINCHI", "2": "IKKINCHI", "3": "UCHINCHI"}

    # position qiymati string yoki int bo‘lishi mumkin
    pos_text = pos_map.get(str(position), str(position))  # agar xarita topilmasa o‘zi chiqadi

    # Font va rang
    c.setFont("Arimo-Bold", 13)

    # Markazlashgan, chapga surish
    x_coord = width / 2 - 50
    y_coord = height / 2 + 18.5
    c.drawCentredString(x_coord, y_coord, pos_text)

    pos_map = {"1": "I", "2": "II", "3": "III"}

    # position qiymati string yoki int bo‘lishi mumkin
    pos_text = pos_map.get(str(position), str(position))  # agar xarita topilmasa o‘zi chiqadi

    # Font va rang
    c.setFont("Arimo-Bold", 28)

    # Markazlashgan, chapga surish
    x_coord = width / 2 - 80
    y_coord = height / 2 - 79
    c.drawCentredString(x_coord, y_coord, pos_text)
    
    # Musobaqa sanasi
    import locale
    locale.setlocale(locale.LC_TIME, "uz_UZ.UTF-8")  # O'zbekcha

    months_uz = {
        1:"YANVAR", 2:"FEVRAL", 3:"MART", 4:"APREL", 5:"MAY",
        6:"IYUN", 7:"IYUL", 8:"AVGUST", 9:"SENTYABR", 10:"OKTYABR",
        11:"NOYABR", 12:"DEKABR"
    }

    # Sana misol
    day = competition_date.day
    month = months_uz[competition_date.month]
    year = competition_date.year

    # Matn
    date_text = f"{year}-YIL {day}-{month}"

    # Dinamik o'ngga surish
    offset = 0
    if len(month) > 4:
        offset = (len(month) - 4) * 5  # har bir ortiqcha harf uchun 5 point

    # PDF chizish
    c.setFont("Arimo-Bold", 13)
    c.drawCentredString(width / 2 + 195 + offset, height / 2 + 71.5, date_text)
    # PDF saqlash
    c.save()

    print(f"✅ Sport diplom tayyorlandi: {os.path.abspath(output_pdf_path)}")
    
from datetime import date

# generate_sport_diploma_pdf(
#     full_name="Ali Valiyev",
#     sport_type="Arqon tortish",
#     position="2",
#     series="SP-2025-001",
#     competition_date=date(2025, 7, 14),
#     template_image_path="sertifikat.png",  # sizning shablon rasm manzilingiz
# )
