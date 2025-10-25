from django.shortcuts import redirect, render
from apps.main.forms import *

from django.http import FileResponse, Http404
from django.conf import settings
from apps.main.models import Diploma
from diplom import generate_diploma_pdf
import os
import tempfile
import pandas as pd
import secrets
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Max

def diploma_search(request):
    diploma = None
    query = ""

    if request.method == "POST":
        query = request.POST.get("code")
        if query:
            diploma = Diploma.objects.filter(public_code=query).first()

    return render(request, "home/index.html", {
        "diploma": diploma,
        "query": query,
    })
    

def download_diploma(request, token):
    # 1️⃣ Diplomni bazadan token orqali topamiz
    diploma = Diploma.objects.filter(unique_token=token).first()
    if not diploma:
        raise Http404("Diplom topilmadi")

    # 2️⃣ Vaqtinchalik chiqish fayl manzili
    temp_dir = tempfile.gettempdir()

    # 3️⃣ Shablon yo‘lini belgilaymiz (masalan templates ichida)
    template_path = os.path.join(settings.BASE_DIR, "templates", "diploma_template.docx")

    # 4️⃣ PDF generatsiya
    generate_diploma_pdf(
        name=diploma.full_name,
        series=diploma.series,
    )

    # 5️⃣ Tayyor PDF faylni foydalanuvchiga yuklab beramiz
    return FileResponse(open('diplom.pdf', "rb"), as_attachment=True, filename=f"{diploma.series}.pdf")




def upload_diplomas(request):
    if request.method == "POST":
        file = request.FILES.get("file")
        if not file:
            messages.error(request, "Iltimos, Excel faylni tanlang.")
            return redirect("upload_diplomas")

        try:
            # Excel faylni o‘qish
            df = pd.read_excel(file)

            # Kerakli ustunlar (endi 'Tuman' yo‘q)
            required_columns = ["Hudud", "FISH", "Login"]
            if not all(col in df.columns for col in required_columns):
                messages.error(request, "Excel faylda 'Hudud', 'FISH' va 'Login' ustunlari bo‘lishi kerak.")
                return redirect("upload_diplomas")

            # Oxirgi seriya raqamini aniqlash
            last_series = Diploma.objects.aggregate(Max("series"))["series__max"]
            start_number = 1
            if last_series:
                try:
                    # Masalan: 1-000056 → 57
                    start_number = int(last_series.split("-")[1]) + 1
                except Exception:
                    pass

            created_count = 0

            for _, row in df.iterrows():
                region = str(row["Hudud"]).strip()
                full_name = str(row["FISH"]).strip()
                public_code = str(row["Login"]).strip()

                # Seriya generatsiya
                series = f"1-{start_number:06d}"
                start_number += 1

                # Ma'lumotni bazaga yozish
                Diploma.objects.create(
                    full_name=full_name,
                    region=region,
                    public_code=public_code,
                    series=series,
                    unique_token=secrets.token_urlsafe(12),
                )
                created_count += 1

            messages.success(request, f"{created_count} ta diplom muvaffaqiyatli yuklandi!")
            return redirect("upload_diplomas")

        except Exception as e:
            messages.error(request, f"Xatolik: {e}")
            return redirect("upload_diplomas")

    return render(request, "upload_diplomas.html")