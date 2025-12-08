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
        
        # Check if session is completed before initializing
        session_status = await self.get_session_status()
        if session_status == 'completed':
            # Don't initialize for completed interviews
            return
        
        # Initialize interviewer and send opening message
        await self.initialize_interviewer()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def initialize_interviewer(self):
        """Initialize the interviewer agent and restore state from existing messages."""
        try:
            session_data = await self.get_session_data()
            
            if not session_data or not session_data.get('case_data'):
                await self.send(text_data=json.dumps({
                    'message': 'Error: Could not load case data. Please refresh and try again.',
                    'role': 'system'
                }))
                return
            
            # Create a fresh interviewer instance for this interview
            from agents.interviewer import InterviewerAgent
            
            self.interviewer = InterviewerAgent(
                case_data=session_data['case_data'],
                interview_mode=session_data['mode']
            )
            
            # Get existing messages for this session
            existing_messages = await self.get_existing_messages()
            
            # If there are existing messages, restore the interviewer state
            if existing_messages:
                # Reconstruct conversation history
                for msg in existing_messages:
                    # Map 'assistant' role from DB to 'interviewer' for internal use
                    role = 'interviewer' if msg['role'] == 'assistant' else 'candidate' if msg['role'] == 'user' else msg['role']
                    self.interviewer.conversation_history.append({
                        'role': role,
                        'content': msg['content']
                    })
                
                # Restore the current phase from the session data
                current_phase = session_data.get('current_phase', 'framework')
                self.interviewer.current_phase = current_phase
                
                # Calculate turn count from message history (only count user messages)
                user_messages = [m for m in existing_messages if m['role'] == 'user']
                self.interviewer.turn_count = len(user_messages)
                
                # Estimate phase turns (messages in current phase)
                # This is approximate since we don't store phase per message
                phase_user_messages = max(1, len(user_messages) // 5)  # Rough estimate
                self.interviewer.phase_turns[current_phase] = phase_user_messages
                
                # Don't send opening message - resume from where we left off
                # No system message needed, just restore silently
                await self.send(text_data=json.dumps({
                    'message': '',
                    'role': 'system',
                    'phase': current_phase,
                    'completed': False,
                    'resumed': True
                }))
            else:
                # First time starting - send opening message
                opening_msg = self.interviewer.get_opening_message()
                current_phase = self.interviewer.get_current_phase()
                
                # Save to database
                await self.save_message(opening_msg, 'assistant')
                
                # Send to client with phase information
                await self.send(text_data=json.dumps({
                    'message': opening_msg,
                    'role': 'interviewer',
                    'phase': current_phase,
                    'completed': False
                }))
        except Exception as e:
            import traceback
            error_msg = f"Error initializing interview: {str(e)}"
            print(f"Initialize interviewer error: {traceback.format_exc()}")
            await self.send(text_data=json.dumps({
                'message': error_msg,
                'role': 'system'
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
            response_data = await self.generate_ai_response(message)
            
            # Save AI response (use 'assistant' for consistency with Message model)
            await self.save_message(response_data['message'], 'assistant')
            
            # Update session phase
            await self.update_session_phase(response_data['phase'], response_data['completed'])
            
            # Send AI response to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': response_data['message'],
                    'role': 'interviewer',
                    'phase': response_data['phase'],
                    'completed': response_data['completed']
                }
            )
    
    async def chat_message(self, event):
        """Receive message from room group."""
        message = event['message']
        role = event.get('role', 'user')
        phase = event.get('phase', None)
        completed = event.get('completed', False)
        
        # Send message to WebSocket
        response_data = {
            'message': message,
            'role': role
        }
        
        if phase:
            response_data['phase'] = phase
        if completed:
            response_data['completed'] = True
        
        await self.send(text_data=json.dumps(response_data))
    
    @database_sync_to_async
    def get_session_data(self):
        """Get session and case data, and mark it as in progress."""
        try:
            session = InterviewSession.objects.select_related('case').get(id=self.session_id)
            
            # Mark session as in progress if not already started
            if session.status != 'completed':
                session.status = 'in_progress'
                if not session.started_at:
                    from django.utils import timezone
                    session.started_at = timezone.now()
                session.save()
            
            if session.case:
                return {
                    'case_data': {
                        'title': session.case.title,
                        'prompt': session.case.prompt,
                        'context': session.case.context,
                        'exhibits': session.case.exhibits,
                        'case_type': session.case.case_type
                    },
                    'mode': session.mode,
                    'current_phase': session.current_phase
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
    
    @database_sync_to_async
    def update_session_phase(self, phase, completed):
        """Update the session's current phase and completion status."""
        try:
            session = InterviewSession.objects.get(id=self.session_id)
            session.current_phase = phase
            if completed:
                session.status = 'completed'
            session.save()
        except InterviewSession.DoesNotExist:
            pass
    
    @database_sync_to_async
    def get_existing_messages(self):
        """Get all existing messages for this session."""
        try:
            session = InterviewSession.objects.get(id=self.session_id)
            messages = Message.objects.filter(session=session).order_by('created_at')
            return [{'role': msg.role, 'content': msg.content} for msg in messages]
        except InterviewSession.DoesNotExist:
            return []
    
    @database_sync_to_async
    def get_session_status(self):
        """Get the status of the session."""
        try:
            session = InterviewSession.objects.get(id=self.session_id)
            return session.status
        except InterviewSession.DoesNotExist:
            return 'not_started'

