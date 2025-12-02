"""
WebSocket routing for case_interview_simulator project.
"""
from django.urls import re_path
from interviews import consumers

websocket_urlpatterns = [
    re_path(r'ws/interview/(?P<session_id>\w+)/$', consumers.InterviewConsumer.as_asgi()),
]

