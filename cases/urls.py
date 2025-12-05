"""
URL configuration for cases app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.case_list_view, name='case_list'),
    path('generate/', views.generate_case_view, name='case_generate'),
    path('<int:case_id>/', views.case_detail_view, name='case_detail'),
]

