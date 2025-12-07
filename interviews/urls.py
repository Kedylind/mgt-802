"""
URL configuration for interviews app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.interview_list_view, name='interview_list'),
    path('start/', views.interview_start_view, name='interview_start'),
    path('<int:session_id>/', views.interview_detail_view, name='interview_detail'),
    path('<int:session_id>/evaluate/', views.evaluate_interview_view, name='evaluate_interview'),
    path('<int:session_id>/evaluate-inline/', views.evaluate_interview_inline_view, name='evaluate_interview_inline'),
    path('<int:session_id>/feedback/', views.feedback_view, name='feedback_view'),
    path('<int:session_id>/upload-recording/', views.upload_recording_view, name='upload_recording'),
]

