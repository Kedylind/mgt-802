# AI Case Interview Simulator - Implementation Plan

## Project Overview
Build a Django-based web application for MBA/Master's students to practice consulting and product management case interviews. The system will use multi-agent AI workflows to generate cases, conduct interviews, evaluate performance, and provide coaching feedback.

## Architecture Decisions
- **Backend**: Django (full-stack with templates, no separate frontend framework)
- **Database**: PostgreSQL
- **Deployment**: Railway
- **AI Integration**: Multiple models (OpenAI, Anthropic, or similar) for different agents
- **Media Processing**: Video/audio recording in-browser, transcription and analysis via APIs

## Implementation Steps

### Phase 1: Project Setup & Infrastructure (Week 1)

#### 1.1 Django Project Initialization
- Create Django project structure (`django-admin startproject`)
- Set up virtual environment and requirements.txt
- Configure PostgreSQL database connection
- Set up Django settings for development and production environments
- Create `.env` file structure for environment variables (API keys, database URLs)
- Initialize Git repository and create `.gitignore`

#### 1.2 Core Django Apps Structure
Create modular Django apps:
- `accounts`: User authentication and management
- `interviews`: Core interview functionality (sessions, modes)
- `cases`: Case generation and management
- `agents`: Multi-agent workflow system
- `analysis`: Performance evaluation and scoring
- `feedback`: Coaching feedback generation

#### 1.3 Database Models
Design and implement core models:
- `User` (extend Django's User model)
- `InterviewSession`: Track interview state, mode, timestamps
- `Case`: Generated case data, exhibits, metadata
- `Message`: Chat conversation history
- `Recording`: Video/audio file storage references
- `Evaluation`: Performance scores and analysis results
- `Feedback`: Coaching recommendations

#### 1.4 Basic UI Foundation
- Set up base templates with modern CSS framework (Tailwind CSS or Bootstrap)
- Create navigation and layout structure
- Implement user authentication views (login, signup, logout)
- Design dashboard/homepage

### Phase 2: Core Interview Functionality (Week 1-2)

#### 2.1 Mode Selection Interface
- Create interview mode selection page
- Implement three modes: interviewer-led, candidate-led, PM product case
- Add mode-specific configuration options
- Store mode selection in session

#### 2.2 Conversational Chat Engine
- Implement WebSocket or Server-Sent Events for real-time chat
- Create chat interface UI component
- Build message handling system (send/receive)
- Implement chat history persistence
- Add typing indicators and message status

#### 2.3 Case Generator Agent
- Design Case Generator agent class
- Implement case generation prompts for different interview types
- Create case structure (prompt, context, exhibits)
- Integrate with LLM API (OpenAI/Anthropic)
- Add case validation and quality checks
- Store generated cases in database

#### 2.4 Interviewer Agent
- Design Interviewer agent class with mode-specific behavior
- Implement adaptive questioning logic
- Create exhibit release mechanism (controlled, based on candidate requests)
- Build follow-up question generation
- Integrate with conversational chat engine

### Phase 3: RAG & Case Knowledge Base (Week 2)

#### 3.1 RAG Infrastructure Setup
- Set up vector database (Pinecone, Weaviate, or ChromaDB)
- Create embedding pipeline for case documents
- Implement document chunking strategy
- Build retrieval system for relevant case examples

#### 3.2 Case Knowledge Base
- Collect and prepare case interview examples
- Process and embed case documents
- Create retrieval functions for similar cases
- Integrate RAG into Case Generator agent
- Implement context injection for case generation

### Phase 4: Recording & Media Processing (Week 2)

#### 4.1 Browser Recording Implementation
- Implement MediaRecorder API for video/audio capture
- Create recording UI component with start/stop controls
- Add recording status indicators
- Implement file upload to Django backend
- Store recordings (local filesystem or cloud storage like S3)

#### 4.2 Transcription Service
- Integrate transcription API (OpenAI Whisper, AssemblyAI, or similar)
- Create async task for transcription processing
- Store transcriptions linked to recordings
- Handle transcription errors and retries

### Phase 5: Analysis & Evaluation (Week 3)

#### 5.1 Content Analysis (Evaluator Agent)
- Design Evaluator agent for content quality assessment
- Implement evaluation dimensions:
  - Structure and framework usage
  - Hypothesis formation
  - Mathematical accuracy
  - Insight quality
- Create scoring algorithms
- Generate structured evaluation results

#### 5.2 Communication Style Analysis
- Integrate vision API for video analysis (movement, presence)
- Integrate voice analysis API for pacing and delivery
- Create communication metrics:
  - Body language and movement
  - Speech pacing
  - Presence and confidence
  - Delivery clarity
- Combine vision and audio analysis results

#### 5.3 Coach Agent
- Design Coach agent for feedback generation
- Create feedback templates based on evaluation results
- Implement recommendation system for drills and practice areas
- Generate personalized coaching guidance
- Link feedback to specific interview moments

### Phase 6: Security & Safety (Week 3)

#### 6.1 Prompt Injection Protection
- Implement input sanitization functions
- Create prompt injection detection patterns
- Add input validation middleware
- Implement controlled exhibit release (prevent premature data access)
- Test against common prompt injection attacks

#### 6.2 API Security
- Secure API key storage (environment variables)
- Implement rate limiting
- Add request validation
- Create error handling that doesn't leak sensitive info

### Phase 7: UI/UX Polish (Week 3)

#### 7.1 Interview Interface
- Polish chat interface design
- Add exhibit display components (tables, charts, images)
- Implement smooth transitions and animations
- Add progress indicators
- Create responsive design for mobile/tablet

#### 7.2 Results & Feedback Display
- Design scorecard visualization (charts, progress bars)
- Create feedback presentation page
- Add drill recommendations UI
- Implement comparison views (multiple sessions)

#### 7.3 User Experience Enhancements
- Add loading states and spinners
- Implement error messages and recovery
- Create help/tutorial system
- Add keyboard shortcuts

### Phase 8: Testing & Quality Assurance (Week 3)

#### 8.1 Unit Tests
- Write tests for each agent class
- Test database models and relationships
- Test API integrations (mocked)
- Test utility functions
- Achieve minimum 70% code coverage

#### 8.2 Integration Tests
- Test full interview workflow
- Test recording and analysis pipeline
- Test multi-agent interactions
- Test error handling scenarios

#### 8.3 Code Quality
- Add docstrings to all functions and classes
- Add type hints throughout codebase
- Refactor large functions into smaller, focused ones
- Ensure consistent code style (use Black, flake8)

### Phase 9: Railway Deployment (Week 3)

#### 9.1 Railway Setup
- Create Railway account and project
- Connect GitHub repository
- Configure PostgreSQL database on Railway
- Set up environment variables in Railway dashboard

#### 9.2 Deployment Configuration
- Create `Procfile` for Railway
- Configure `runtime.txt` (Python version)
- Set up `requirements.txt` with all dependencies
- Configure `settings.py` for production (DEBUG=False, allowed hosts)
- Set up static files serving (WhiteNoise or Railway static files)
- Configure media files storage (Railway volumes or external storage)

#### 9.3 Deployment Testing
- Test deployment on Railway staging
- Verify database migrations run correctly
- Test all functionality in production environment
- Verify API integrations work with production URLs
- Test video upload and storage

#### 9.4 Domain & SSL
- Configure custom domain (if needed)
- Verify SSL certificate
- Test HTTPS functionality

### Phase 10: Documentation (Week 3)

#### 10.1 Code Documentation
- Ensure all modules have docstrings
- Create architecture documentation
- Document API endpoints and agent interfaces
- Document environment variable requirements

#### 10.2 User Documentation
- Create user guide/README
- Document how to run locally
- Document deployment process
- Create troubleshooting guide

#### 10.3 Project Report
- Write project description document
- Document technical accomplishments
- Explain utility and use cases
- Include citations for academic work and software used
- Document code structure and key design decisions

## Key Technical Accomplishments Checklist
- [x] Hosted web application (Django on Railway)
- [x] Search-Augmented Retrieval (RAG for case generation)
- [x] Conversational chat (WebSocket/SSE real-time chat)
- [x] Multiple APIs (LLM APIs, transcription, vision, voice analysis)
- [x] Multiple models (different agents use different models)
- [x] Multiple media (video and audio processing)
- [x] Multiple API calls (sequential agent workflows)
- [x] Prompt injection resistance (input filtering, controlled access)
- [x] Sophisticated agent workflows (hierarchical: Case Generator → Interviewer → Evaluator → Coach)
- [x] Non-standard tools (custom agent classes)

## File Structure Preview
```
mgt-802/
├── manage.py
├── requirements.txt
├── Procfile
├── runtime.txt
├── .env.example
├── .gitignore
├── case_interview_simulator/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── accounts/
├── interviews/
├── cases/
├── agents/
│   ├── case_generator.py
│   ├── interviewer.py
│   ├── evaluator.py
│   └── coach.py
├── analysis/
├── feedback/
├── static/
├── media/
└── templates/
```

## Critical Dependencies
- Django 4.2+
- PostgreSQL adapter (psycopg2)
- OpenAI/Anthropic SDKs
- WebSocket support (Django Channels or similar)
- Media processing libraries
- Vector database client
- Testing frameworks (pytest-django)

## Implementation Todos

### Phase 1: Setup
- [ ] Initialize Django project with PostgreSQL, create app structure, set up environment configuration
- [ ] Design and implement database models (User, InterviewSession, Case, Message, Recording, Evaluation, Feedback)
- [ ] Create base templates, authentication views, and dashboard UI

### Phase 2: Core Functionality
- [ ] Implement conversational chat engine with WebSocket/SSE for real-time communication
- [ ] Build Case Generator agent with LLM integration for generating interview cases
- [ ] Build Interviewer agent with mode-specific behavior and adaptive questioning

### Phase 3: RAG
- [ ] Set up RAG infrastructure with vector database and integrate into case generation

### Phase 4: Recording
- [ ] Implement browser-based video/audio recording and file upload to backend
- [ ] Integrate transcription API and process recordings asynchronously

### Phase 5: Analysis
- [ ] Build Evaluator agent for content quality assessment (structure, hypothesis, math, insights)
- [ ] Integrate vision and voice analysis APIs for communication style evaluation
- [ ] Build Coach agent for generating personalized feedback and drill recommendations

### Phase 6: Security
- [ ] Implement prompt injection protection, input sanitization, and controlled exhibit release

### Phase 7: UI/UX
- [ ] Polish interview interface, results display, and add UX enhancements

### Phase 8: Testing
- [ ] Write unit tests, integration tests, add docstrings and type hints

### Phase 9: Deployment
- [ ] Configure and deploy application to Railway with PostgreSQL, environment variables, and static/media files

### Phase 10: Documentation
- [ ] Create code documentation, user guide, and project report with citations

## Notes
- All API keys must be stored in environment variables, never committed
- Use Django's async capabilities where beneficial (Channels for WebSockets)
- Consider using Celery for long-running tasks (transcription, analysis)
- Implement proper logging for debugging in production
- Use Django's built-in security features (CSRF, XSS protection)

