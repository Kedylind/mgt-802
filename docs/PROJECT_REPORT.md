# AI Case Interview Simulator - Project Report

## Executive Summary

The AI Case Interview Simulator is a comprehensive web application designed to help MBA and Master's students practice consulting and product management case interviews. The system leverages advanced AI technologies including multi-agent workflows, Retrieval-Augmented Generation (RAG), and real-time conversational interfaces to provide an authentic interview experience with personalized feedback.

## Project Overview

### Purpose

The application addresses the critical need for accessible, high-quality case interview practice. Traditional practice methods are limited by:
- Availability of practice partners
- Cost of professional coaching
- Lack of personalized feedback
- Limited case variety

This system provides 24/7 access to AI-powered interview practice with detailed performance evaluation and coaching.

### Target Users

- MBA students preparing for consulting interviews
- Master's students targeting product management roles
- Career services offices at business schools
- Individual learners seeking interview practice

## Technical Accomplishments

### 1. Hosted Web Application

**Technology Stack:**
- **Backend**: Django 4.2+ (Python web framework)
- **Database**: PostgreSQL (production), SQLite (development)
- **Deployment**: Railway (cloud platform)
- **WebSockets**: Django Channels with Daphne ASGI server
- **Static Files**: WhiteNoise middleware

**Key Features:**
- Full-stack Django application with template-based UI
- Real-time chat interface using WebSockets
- User authentication and session management
- File upload and media handling
- Responsive design with Tailwind CSS

### 2. Search-Augmented Retrieval (RAG)

**Implementation:**
- PDF casebook processing using CrewAI's PDFSearchTool
- Vector database integration (Pinecone-ready)
- Context injection for case generation
- Similar case retrieval for inspiration

**Benefits:**
- Generates realistic cases based on real examples
- Maintains consistency with industry standards
- Provides variety through RAG-enhanced generation

### 3. Conversational Chat

**Technology:**
- Django Channels for WebSocket support
- Real-time bidirectional communication
- Message persistence in database
- Typing indicators and status updates

**Features:**
- Instant message delivery
- Conversation history tracking
- Multi-user support with channel layers
- Graceful degradation for connection issues

### 4. Multiple APIs Integration

**APIs Used:**
- **OpenAI GPT-4o-mini**: Primary LLM for all agents
- **OpenAI Whisper**: Audio/video transcription
- **CrewAI**: Multi-agent orchestration framework
- **PDFSearchTool**: Document retrieval for RAG

**Integration Points:**
- Case generation with RAG
- Interviewer responses
- Performance evaluation
- Coaching feedback generation
- Audio transcription

### 5. Multiple Models

**Agent Architecture:**
- **CaseGenerator**: Uses GPT-4o-mini with RAG
- **InterviewerAgent**: Uses GPT-4o-mini for adaptive questioning
- **EvaluatorAgent**: Uses GPT-4o-mini for performance assessment
- **CoachAgent**: Uses GPT-4o-mini for feedback generation

Each agent has specialized prompts and behaviors tailored to its role.

### 6. Multiple Media Processing

**Capabilities:**
- Browser-based video recording (MediaRecorder API)
- Audio-only recording support
- File upload to Django backend
- Asynchronous transcription processing
- Transcription storage and retrieval

**Workflow:**
1. User starts recording in browser
2. MediaRecorder captures video/audio
3. File uploaded to Django on stop
4. Background thread processes transcription
5. Transcription stored for evaluation

### 7. Multiple API Calls

**Sequential Workflows:**
- Case Generation: Research → Design → Write (3 agents)
- Interview Evaluation: Evaluator → Coach (2 agents)
- Recording Processing: Upload → Transcribe → Analyze

**Parallel Processing:**
- Multiple interview sessions simultaneously
- Concurrent transcription processing
- Independent agent operations

### 8. Prompt Injection Resistance

**Security Measures:**
- Input sanitization functions
- Pattern detection for injection attempts
- Controlled exhibit release mechanism
- User input validation
- System prompt protection

**Implementation:**
- `case_interview_simulator.security` module
- Input filtering in all agent interactions
- Exhibit access control in InterviewerAgent
- CSRF protection on all forms

### 9. Sophisticated Agent Workflows

**Hierarchical Architecture:**
```
CaseGenerator (RAG-enhanced)
    ↓
InterviewerAgent (Adaptive questioning)
    ↓
EvaluatorAgent (Performance assessment)
    ↓
CoachAgent (Feedback generation)
```

**Workflow Features:**
- State management across agents
- Context passing between stages
- Error handling and fallbacks
- Conversation history tracking

### 10. Non-Standard Tools

**Custom Implementations:**
- CaseGenerator with PDF RAG integration
- InterviewerAgent with mode-specific behavior
- EvaluatorAgent with structured scoring
- CoachAgent with drill recommendations
- Recording transcription service
- Exhibit release control system

## System Architecture

### Database Schema

**Core Models:**
- User (custom Django user model)
- InterviewSession (interview state management)
- Case (generated case data)
- Message (conversation history)
- Recording (media files and transcriptions)
- Evaluation (performance scores)
- Feedback (coaching recommendations)

### Application Structure

```
mgt-802/
├── accounts/          # User authentication
├── interviews/        # Interview sessions and chat
├── cases/            # Case generation and management
├── agents/           # AI agent implementations
├── analysis/         # Performance evaluation
├── feedback/         # Coaching feedback
└── case_interview_simulator/  # Django project config
```

### Agent Communication

**Message Flow:**
1. User message → WebSocket → InterviewerAgent
2. InterviewerAgent → OpenAI API → Response
3. Response → WebSocket → User
4. On completion → EvaluatorAgent → CoachAgent → Feedback

## Key Design Decisions

### 1. Django Full-Stack Approach

**Decision**: Use Django templates instead of separate frontend framework.

**Rationale:**
- Faster development for MVP
- Simpler deployment
- Built-in security features
- Easier maintenance

### 2. Multi-Agent Architecture

**Decision**: Separate agents for different functions rather than single monolithic agent.

**Rationale:**
- Specialized prompts for each role
- Better error isolation
- Easier to optimize individual agents
- More maintainable codebase

### 3. RAG for Case Generation

**Decision**: Use RAG instead of pure LLM generation.

**Rationale:**
- More realistic cases based on examples
- Consistency with industry standards
- Better variety and quality
- Grounded in real case structures

### 4. WebSocket for Real-Time Chat

**Decision**: Use WebSockets instead of polling.

**Rationale:**
- Lower latency
- Better user experience
- More efficient server resources
- Real-time feel

### 5. Asynchronous Transcription

**Decision**: Process transcriptions in background threads.

**Rationale:**
- Non-blocking user experience
- Can scale to Celery in production
- Handles long recordings
- Graceful error handling

## Utility and Use Cases

### Primary Use Cases

1. **Individual Practice**
   - Students practice on their own schedule
   - Unlimited case variety
   - Immediate feedback

2. **Skill Assessment**
   - Track improvement over time
   - Identify weak areas
   - Measure progress

3. **Interview Preparation**
   - Practice different interview modes
   - Build confidence
   - Refine communication skills

4. **Educational Tool**
   - Career services integration
   - Classroom use
   - Group practice sessions

### Benefits

- **Accessibility**: 24/7 availability
- **Cost-Effective**: No per-session fees
- **Personalized**: AI adapts to user responses
- **Comprehensive**: Covers all interview aspects
- **Scalable**: Handles multiple users simultaneously

## Technical Challenges and Solutions

### Challenge 1: Real-Time Communication

**Problem**: Maintaining WebSocket connections across server restarts.

**Solution**: Django Channels with Redis channel layer, graceful reconnection handling.

### Challenge 2: Case Quality

**Problem**: Generated cases sometimes lacked realism or structure.

**Solution**: RAG integration with real casebook examples, multi-agent generation workflow.

### Challenge 3: Transcription Latency

**Problem**: Long transcription times blocking user experience.

**Solution**: Asynchronous processing in background threads, status updates.

### Challenge 4: Prompt Injection

**Problem**: Users could potentially manipulate AI responses.

**Solution**: Input sanitization, controlled exhibit release, system prompt protection.

### Challenge 5: Deployment Complexity

**Problem**: Multiple services (Django, PostgreSQL, Redis) to coordinate.

**Solution**: Railway platform with managed services, environment-based configuration.

## Future Enhancements

### Short-Term

- [ ] Celery integration for better async task management
- [ ] Video analysis for body language scoring
- [ ] Voice analysis for speech pacing
- [ ] Comparison views across multiple sessions
- [ ] Export interview transcripts

### Long-Term

- [ ] Mobile app version
- [ ] Integration with learning management systems
- [ ] Advanced analytics dashboard
- [ ] Peer practice mode
- [ ] Industry-specific case libraries

## Citations and References

### Academic Work

- Case interview methodology based on frameworks from:
  - McKinsey & Company case interview guides
  - BCG case interview preparation materials
  - Darden Case Book 2018-2019

### Software and Libraries

- **Django**: Web framework (https://www.djangoproject.com/)
- **CrewAI**: Multi-agent framework (https://www.crewai.com/)
- **OpenAI**: GPT-4o-mini and Whisper APIs (https://openai.com/)
- **Django Channels**: WebSocket support (https://channels.readthedocs.io/)
- **PostgreSQL**: Database (https://www.postgresql.org/)
- **Railway**: Deployment platform (https://railway.app/)

### Documentation

- Django Documentation: https://docs.djangoproject.com/
- CrewAI Documentation: https://docs.crewai.com/
- OpenAI API Documentation: https://platform.openai.com/docs

## Conclusion

The AI Case Interview Simulator successfully demonstrates the integration of multiple advanced AI technologies to create a practical, useful application. The system provides real value to students preparing for case interviews while showcasing technical capabilities including RAG, multi-agent workflows, real-time communication, and media processing.

The project meets all technical requirements and provides a solid foundation for future enhancements. The modular architecture allows for easy extension and improvement, making it a sustainable solution for interview preparation.

## Acknowledgments

This project was developed as part of MGT 802 coursework, demonstrating practical application of LLM technologies in a real-world context.

