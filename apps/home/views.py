from django.shortcuts import redirect, render
from apps.main.forms import *

from django.http import FileResponse, Http404
from django.conf import settings
from apps.main.models import Diploma
from diplom import generate_diploma_pdf, generate_sport_diploma_pdf
from apps.main.models import SportDiploma
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
            # Oddiy Diploma modelidan qidirish
            diploma = Diploma.objects.filter(public_code=query).first()

            # Agar topilmasa, SportDiploma modelidan qidirish
            if not diploma:
                diploma = SportDiploma.objects.filter(series=query).first()

    return render(request, "home/index.html", {
        "diploma": diploma,
        "query": query,
    })
    

def download_diploma(request, token):
    diploma = Diploma.objects.filter(unique_token=token).first()
    sport_diploma = None

    if not diploma:
        # Agar Diploma topilmasa, SportDiploma series bo‘yicha qidiramiz
        sport_diploma = SportDiploma.objects.filter(series=token).first()
        if not sport_diploma:
            raise Http404("Diplom topilmadi")

    # PDF nomi har doim bir xil
    output_pdf_path = os.path.join(settings.BASE_DIR, "diplom.pdf")

    if diploma:
        # Oddiy diplom generatsiya
        generate_diploma_pdf(
            name=diploma.full_name,
            series=diploma.series,
            output_pdf=output_pdf_path  # doim diplom.pdf
        )
    else:
        # Sport diplom generatsiya
        generate_sport_diploma_pdf(
            full_name=sport_diploma.full_name,
            sport_type=sport_diploma.sport_type,
            position=sport_diploma.positon,
            series=sport_diploma.series,
            competition_date=sport_diploma.date,
            template_image_path="sertifikat.png",
            output_pdf_path=output_pdf_path  # doim diplom.pdf
        )

    # PDFni foydalanuvchiga yuklab berish
    return FileResponse(open(output_pdf_path, "rb"), as_attachment=True, filename="diplom.pdf")


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

def upload_sport_diplomas(request):
    if request.method == "POST":
        file = request.FILES.get("file")
        if not file:
            messages.error(request, "Iltimos, Excel faylni tanlang.")
            return redirect("upload_sport_diplomas")

        try:
            # Excel faylni o‘qish
            df = pd.read_excel(file)

            # Kerakli ustunlar
            required_columns = ["FISH", "Sport turi", "Daraja", "Musobaqa sanasi"]
            if not all(col in df.columns for col in required_columns):
                messages.error(request, "Excel faylda 'FISH', 'Sport turi', 'Daraja' va 'Musobaqa sanasi' ustunlari bo‘lishi kerak.")
                return redirect("upload_sport_diplomas")

            # Oxirgi seriya raqamini aniqlash
            last_series = SportDiploma.objects.aggregate(Max("series"))["series__max"]
            start_number = 1
            if last_series:
                try:
                    # Masalan: 1-000056 → 57
                    start_number = int(last_series.split("-")[1]) + 1
                except Exception:
                    pass

            created_count = 0

            for _, row in df.iterrows():
                full_name = str(row["FISH"]).strip()
                sport_type = str(row["Sport turi"]).strip()
                position = str(row["Daraja"]).strip()
                competition_date = row["Musobaqa sanasi"]
                
                # Seriya generatsiya
                series = f"1-{start_number:06d}"
                start_number += 1

                # Bazaga yozish
                SportDiploma.objects.create(
                    full_name=full_name,
                    sport_type=sport_type,
                    positon=position,
                    date=competition_date,
                    series=series,
                    shablon=None  # agar shablon kerak bo'lsa keyin qo'shish mumkin
                )
                created_count += 1

            messages.success(request, f"{created_count} ta sport diplom muvaffaqiyatli yuklandi!")
            return redirect("upload_sport_diplomas")

        except Exception as e:
            messages.error(request, f"Xatolik: {e}")
            return redirect("upload_sport_diplomas")

    return render(request, "upload_sport_diplomas.html")