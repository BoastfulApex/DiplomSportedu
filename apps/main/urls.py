from django.urls import path 
from .views import index


urlpatterns = [

    path('', index, name='web_app_page_home'),
]
