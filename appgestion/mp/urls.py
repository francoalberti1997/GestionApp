from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name=''),
    path('check/<str:token>/', views.check_pro_render, name=''),
]
