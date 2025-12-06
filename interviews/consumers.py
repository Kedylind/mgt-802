"""
WebSocket consumers for real-time interview chat.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import InterviewSession, Message


class InterviewConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for interview chat with AI interviewer."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interviewer = None
    
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f'interview_{self.session_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Initialize interviewer and send opening message
        await self.initialize_interviewer()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def initialize_interviewer(self):
        """Initialize the interviewer agent and send opening message."""
        session_data = await self.get_session_data()
        
        if session_data and session_data['case_data']:
            from agents.interviewer import InterviewerAgent
            
            self.interviewer = InterviewerAgent(
                case_data=session_data['case_data'],
                interview_mode=session_data['mode']
            )
            
            # Send opening message
            opening_msg = self.interviewer.get_opening_message()
            
            # Save to database
            await self.save_message(opening_msg, 'interviewer')
            
            # Send to client
            await self.send(text_data=json.dumps({
                'message': opening_msg,
                'role': 'interviewer'
            }))
    
    async def receive(self, text_data):
        """Receive message from WebSocket."""
        from case_interview_simulator.security import SecurityValidator
        
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        role = text_data_json.get('role', 'user')
        
        # Validate and sanitize message
        is_valid, sanitized_message, error = SecurityValidator.validate_message(message)
        
        if not is_valid:
            # Send error message back to user
            await self.send(text_data=json.dumps({
                'message': f"⚠️ {error}",
                'role': 'system'
            }))
            return
        
        # Use sanitized message
        message = sanitized_message
        
        # Save user message to database
        await self.save_message(message, role)
        
        # Echo user message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'role': role
            }
        )
        
        # Generate AI response if interviewer is initialized
        if self.interviewer and role == 'user':
            ai_response = await self.generate_ai_response(message)
            
            # Save AI response
            await self.save_message(ai_response, 'interviewer')
            
            # Send AI response to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': ai_response,
                    'role': 'interviewer'
                }
            )
    
    async def chat_message(self, event):
        """Receive message from room group."""
        message = event['message']
        role = event.get('role', 'user')
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'role': role
        }))
    
    @database_sync_to_async
    def get_session_data(self):
        """Get session and case data."""
        try:
            session = InterviewSession.objects.select_related('case').get(id=self.session_id)
            if session.case:
                return {
                    'case_data': {
                        'title': session.case.title,
                        'prompt': session.case.prompt,
                        'context': session.case.context,
                        'exhibits': session.case.exhibits,
                        'case_type': session.case.case_type
                    },
                    'mode': session.mode
                }
            return None
        except InterviewSession.DoesNotExist:
            return None
    
    @database_sync_to_async
    def generate_ai_response(self, user_message):
        """Generate AI response using the interviewer agent."""
        if self.interviewer:
            return self.interviewer.process_candidate_message(user_message)
        return "I'm having trouble connecting to the interviewer. Please try again."
    
    @database_sync_to_async
    def save_message(self, message_content, role='user'):
        """Save message to database."""
        try:
            session = InterviewSession.objects.get(id=self.session_id)
            Message.objects.create(
                session=session,
                role=role,
                content=message_content
            )
        except InterviewSession.DoesNotExist:
            # Handle case where session doesn't exist
            pass

