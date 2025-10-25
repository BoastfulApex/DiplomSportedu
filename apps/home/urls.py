from django.urls import path
from apps.home import views

urlpatterns = [
    path("", views.diploma_search, name="home"),
    path('download/<str:token>/', views.download_diploma, name='download_diploma'),
    path('upload/', views.upload_diplomas, name='upload_diplomas'),

]
