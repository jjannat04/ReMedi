from django.urls import path
from . import views

urlpatterns = [
    path('', views.marketplace, name='marketplace'),
    path('verify-queue/', views.verification_queue, name='verification_queue'),
    path('verify/<int:med_id>/', views.verify_medicine, name='verify_medicine'),
]