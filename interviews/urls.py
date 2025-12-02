"""
URL configuration for interviews app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.interview_list_view, name='interview_list'),
    path('start/', views.interview_start_view, name='interview_start'),
    path('<int:session_id>/', views.interview_detail_view, name='interview_detail'),
]

