from docx import Document
from docx2pdf import convert
import tempfile
import os
import shutil
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH


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
    
