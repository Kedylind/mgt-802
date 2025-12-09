# Code Overview - AI Case Interview Simulator

A detailed technical description of the codebase architecture, components, and implementation.

## Project Overview

This is a Django-based web application for practicing consulting and product management case interviews. The system uses multi-agent AI workflows powered by CrewAI and OpenAI to generate cases, conduct interviews, evaluate performance, and provide coaching feedback.

**Technology Stack:**
- **Backend**: Django 4.2+ (full-stack with templates)
- **Database**: PostgreSQL (production) / SQLite (development)
- **Real-time**: Django Channels with WebSockets
- **AI Framework**: CrewAI for multi-agent orchestration
- **AI Models**: OpenAI GPT-4o-mini (via OpenAI API)
- **Storage**: Cloudflare R2 (optional) for media files
- **Deployment**: Railway
- **Frontend**: Django Templates + Tailwind CSS (via CDN)

---

## Architecture Overview

### Application Structure

The project follows Django's app-based architecture with 6 main applications:

```
mgt-802/
├── case_interview_simulator/  # Main Django project configuration
├── accounts/                   # User authentication & management
├── interviews/                 # Interview sessions & real-time chat
├── cases/                      # Case generation & management
├── agents/                     # Multi-agent AI system (fully implemented)
├── analysis/                   # Performance evaluation & recordings
└── feedback/                   # Coaching feedback generation
```

### Request Flow

1. **HTTP Requests** → Django Views → Templates → Response
2. **WebSocket Requests** → ASGI → WebSocket Consumers → Real-time chat
3. **Admin Interface** → Django Admin for data management

---

## Core Applications

### 1. `accounts/` - User Management

**Purpose**: Handles user authentication, registration, and user profiles.

**Key Files:**
- `models.py`: Custom `User` model extending Django's `AbstractUser`
  - Adds `created_at` and `updated_at` timestamps
  - Uses table name `users`
  - Custom user model configured in `settings.py` via `AUTH_USER_MODEL`
- `views.py`: 
  - `signup_view()`: User registration with form validation
  - `dashboard_view()`: User dashboard (requires login)
- `forms.py`: `UserRegistrationForm` for signup with password validation
- `urls.py`: Routes for login, logout, signup, dashboard
  - Uses Django's built-in `LoginView` and `LogoutView`

**Database Model:**
- `User`: Stores username, email, password (hashed), timestamps
  - Inherits all standard Django user fields
  - Custom table name: `users`

**Authentication Flow:**
- Registration → Form validation → User creation → Auto-login → Dashboard redirect
- Login → Django auth → Session creation → Dashboard redirect
- All interview/case views require `@login_required` decorator

---

### 2. `interviews/` - Interview Sessions

**Purpose**: Manages interview sessions and real-time chat communication via WebSockets.

**Key Files:**
- `models.py`:
  - `InterviewSession`: Tracks interview state, mode, phase, timestamps
    - Fields: user, case (FK), mode, status, current_phase, started_at, completed_at
    - Status choices: not_started, in_progress, completed, abandoned
    - Phase choices: framework, data_analysis, recommendation, pushback, conclusion, completed
  - `Message`: Stores chat messages in interview sessions
    - Fields: session (FK), role (user/assistant/system), content, created_at
- `views.py`: 
  - `interview_list_view()`: List all user's interviews
  - `interview_start_view()`: Start new interview (GET: show form, POST: create session)
  - `interview_detail_view()`: View interview details with evaluation/feedback
  - `evaluate_interview_view()`: Trigger evaluation and feedback generation
  - `evaluate_interview_inline_view()`: JSON endpoint for inline evaluation
  - `complete_interview_view()`: Mark interview as completed (JSON)
  - `upload_recording_view()`: Handle video/audio upload and transcription
  - `feedback_view()`: Display coaching feedback
- `consumers.py`: `InterviewConsumer` - WebSocket consumer for real-time chat
  - Handles WebSocket connections per session
  - Initializes `InterviewerAgent` on connection
  - Processes candidate messages and generates AI responses
  - Manages conversation state and phase transitions
  - Saves all messages to database
- `urls.py`: Routes for interview management

**Database Models:**
- `InterviewSession`: Links user, case, mode, status, current_phase, timestamps
- `Message`: Stores conversation history (role, content, timestamp)

**Interview Modes:**
- `interviewer_led`: Interviewer-Led (McKinsey-style) - guided questioning
- `candidate_led`: Candidate-Led (BCG/Bain-style) - candidate drives structure

**WebSocket Flow:**
1. Client connects to `/ws/interview/<session_id>/`
2. `InterviewConsumer.connect()` initializes interviewer agent
3. Restores conversation history if session exists
4. Sends opening message or resumes from last state
5. On message receive: validates input, saves to DB, generates AI response
6. Broadcasts messages via channel layer groups
7. Updates session phase and completion status

**Key Features:**
- Conversation state persistence (resumes on reconnect)
- Phase-aware interviewing (framework → data → recommendation → pushback → conclusion)
- Input validation and sanitization via `SecurityValidator`
- Automatic phase transitions based on conversation flow

---

### 3. `cases/` - Case Management

**Purpose**: Stores and manages generated interview cases with RAG capabilities.

**Key Files:**
- `models.py`: `Case` model storing case data
  - Fields: title, case_type, prompt, context (JSON), exhibits (JSON), generated_by (FK), timestamps
  - Context stores: client, situation, objective
  - Exhibits are JSON arrays with: title, type (table/bar/pie), data
- `views.py`:
  - `case_list_view()`: List all cases
  - `case_detail_view()`: View case details
  - `generate_case_view()`: Generate new case using `CaseGenerator` agent
    - Accepts topic and case_type (consulting/product_management)
    - Calls `CaseGenerator.generate_case()` (30-60 seconds)
    - Saves to database and redirects to detail view
- `urls.py`: Routes for case browsing and generation
- `management/commands/`: Django management commands
  - `create_sample_cases.py`: Create sample cases
  - `generate_candidate_cases.py`: Pre-generate cases for selection
  - `seed_cases.py`: Seed database with cases

**Database Model:**
- `Case`: Stores title, type, prompt, context (JSON), exhibits (JSON), creator, timestamps

**Case Types:**
- `consulting`: Traditional consulting case interviews
- `product_management`: PM product case interviews

**Case Structure:**
- **Title**: Descriptive case name
- **Prompt**: Initial problem statement (2-3 sentences)
- **Context**: JSON with client info, situation, objective
- **Exhibits**: Array of data visualizations
  - Tables: columns/rows format
  - Bar charts: labels/values/unit
  - Pie charts: labels/values (must sum to 100%)

---

### 4. `agents/` - Multi-Agent System

**Purpose**: AI agent classes for case generation, interviewing, evaluation, and coaching. **Fully implemented.**

**Key Files:**

#### `case_generator.py` - Case Generation Agent
- **Class**: `CaseGenerator`
- **Framework**: Uses CrewAI with multi-agent workflow
- **Agents**:
  - `researcher`: Searches casebook PDF using RAG (PDFSearchTool)
  - `designer`: Designs case structure and narrative
  - `writer`: Converts design to structured JSON
- **RAG Integration**: 
  - Loads `Darden-Case-Book-2018-2019.pdf` from local filesystem or Cloudflare R2
  - Uses `PDFSearchTool` from `crewai_tools` for semantic search
  - Falls back to generation without RAG if PDF unavailable
- **Methods**:
  - `generate_case(topic, case_type)`: Generate single case
  - `generate_candidates(base_topic, n, case_type, save, user)`: Pre-generate multiple cases
  - `_validate_and_fix_case()`: Validates data formatting, fixes pie chart percentages, ensures currency/percentage symbols
  - `_create_fallback_case()`: Creates basic case if generation fails
- **Output**: JSON matching `Case` model structure
- **Validation**: Ensures proper formatting (currency $, percentages %, K/M/B notation, pie charts sum to 100%)

#### `interviewer.py` - Interviewer Agent
- **Class**: `InterviewerAgent`
- **Purpose**: Conducts adaptive case interviews with phase management
- **Initialization**: Takes `case_data` dict and `interview_mode` string
- **State Management**:
  - `conversation_history`: List of message dicts
  - `exhibits_released`: Tracks which exhibits have been shown
  - `current_phase`: Current interview phase
  - `turn_count`: Total conversation turns
  - `phase_turns`: Turn count per phase
- **Phases**:
  1. `framework`: Candidate presents approach
  2. `data_analysis`: Analyzing data and exhibits
  3. `recommendation`: Formulating recommendation
  4. `pushback`: Defending against challenges
  5. `conclusion`: Final summary
  6. `completed`: Interview finished
- **Methods**:
  - `get_opening_message()`: Generates mode-specific opening
  - `process_candidate_message(message)`: Main processing method
    - Detects exhibit requests
    - Handles phase transitions
    - Generates contextual responses via OpenAI
    - Returns: message, phase, completed status
  - `_handle_exhibit_request()`: Releases exhibits on demand (max 3)
  - `_generate_response()`: Uses OpenAI GPT-4o-mini with system prompt
  - `_build_system_prompt()`: Constructs detailed interviewer instructions
  - `_should_transition_phase()`: Determines phase transitions based on keywords and turn count
- **Exhibit Management**: 
  - Maximum 3 exhibits per interview
  - Releases on candidate request
  - Auto-transitions phase when all exhibits provided
- **AI Integration**: Uses OpenAI API with temperature 0.7, max_tokens 300
- **Mode-Specific Behavior**:
  - Interviewer-led: Guides candidate with structured questions
  - Candidate-led: Answers only when asked, provides data on request

#### `evaluator.py` - Evaluator Agent
- **Class**: `EvaluatorAgent`
- **Purpose**: Evaluates candidate performance in interviews
- **Methods**:
  - `evaluate_interview(case_data, conversation_history)`: Main evaluation method
    - Extracts candidate messages
    - Builds evaluation prompt
    - Calls OpenAI GPT-4o-mini
    - Parses structured scores and feedback
- **Scoring Dimensions** (0-100):
  - `structure_score`: Framework and organization
  - `hypothesis_score`: Hypothesis formation and testing
  - `math_score`: Quantitative analysis accuracy
  - `insight_score`: Actionable insights and recommendations
  - `overall_score`: Weighted average
- **Output**: Dict with scores, strengths, areas for improvement, detailed analysis
- **System Prompt**: Defines evaluator role as senior consultant at top firm
- **Parsing**: Extracts scores and feedback from structured text response

#### `coach.py` - Coach Agent
- **Class**: `CoachAgent`
- **Purpose**: Generates personalized coaching feedback and drill recommendations
- **Methods**:
  - `generate_feedback(evaluation_data, case_data)`: Main coaching method
    - Takes evaluation results
    - Generates personalized feedback via OpenAI
    - Parses recommendations and next steps
- **Output**: Dict with summary, strengths, areas for improvement, recommendations, next steps
- **System Prompt**: Defines coach as experienced case interview coach
- **Format**: Structured feedback with drills and actionable next steps

**Agent Integration:**
- All agents use OpenAI API (GPT-4o-mini)
- API keys managed via Django settings and environment variables
- Error handling with fallback responses
- Async-safe (used in WebSocket consumers via `database_sync_to_async`)

---

### 5. `analysis/` - Performance Evaluation

**Purpose**: Handles recording storage, transcription, and performance evaluation.

**Key Files:**
- `models.py`:
  - `Recording`: Stores video/audio files and transcriptions
    - Fields: session (FK), file (FileField), file_type (video/audio), transcription, created_at
    - Upload path: `recordings/%Y/%m/%d/`
  - `Evaluation`: Stores scores and analysis results
    - Fields: session (OneToOne), scores (structure, hypothesis, math, insight), communication scores (body_language, speech_pacing, presence, delivery_clarity), overall_score, content_analysis (JSON), communication_analysis (JSON), timestamps
    - One-to-one relationship with `InterviewSession`

**Database Models:**
- `Recording`: Links to session, stores file path, file_type, transcription
- `Evaluation`: One-to-one with session, stores:
  - Content scores (structure, hypothesis, math, insights) - 0-100
  - Communication scores (body_language, speech_pacing, presence, delivery_clarity) - 0-100
  - Overall score (0-100)
  - Detailed analysis JSON (content_analysis, communication_analysis)

**Recording Flow:**
1. User uploads video/audio file via `upload_recording_view()`
2. File validated (max 100MB)
3. `Recording` model created
4. Transcription triggered asynchronously via `transcribe_recording_async()`
5. Uses OpenAI Whisper API (`whisper-1` model)
6. Transcription saved to `Recording.transcription` field

**Evaluation Flow:**
1. Interview completed
2. `evaluate_interview_view()` called
3. Extracts conversation history from `Message` model
4. Calls `EvaluatorAgent.evaluate_interview()`
5. Creates `Evaluation` model with scores
6. Calls `CoachAgent.generate_feedback()`
7. Creates `Feedback` model

---

### 6. `feedback/` - Coaching Feedback

**Purpose**: Generates and stores coaching recommendations.

**Key Files:**
- `models.py`: `Feedback` model for coaching recommendations
  - Fields: evaluation (OneToOne), summary, strengths (JSON array), areas_for_improvement (JSON array), recommendations (JSON array), timestamps

**Database Model:**
- `Feedback`: One-to-one with evaluation, stores:
  - Summary: Overall feedback summary (text)
  - Strengths: JSON array of identified strengths
  - Areas for improvement: JSON array of improvement areas
  - Recommendations: JSON array of specific drills and recommendations

**Feedback Generation:**
- Triggered automatically after evaluation
- Uses `CoachAgent.generate_feedback()`
- Personalized based on evaluation scores and case type
- Includes specific drills and actionable next steps

---

## Project Configuration

### `case_interview_simulator/` - Main Project Settings

**Key Files:**

1. **`settings.py`**: 
   - Database configuration (PostgreSQL via `DATABASE_URL` / SQLite fallback)
   - Installed apps: accounts, interviews, cases, agents, analysis, feedback, channels, storages
   - Channels/WebSocket configuration
     - Redis channel layer (production) or in-memory (development)
     - Configured via `REDIS_URL` environment variable
   - Security settings
     - CSRF protection
     - Secure cookies in production
     - XSS protection
     - Railway proxy SSL header handling
   - API key management (OpenAI, Anthropic, AssemblyAI, Pinecone)
     - Loaded from environment variables
     - Accessible via `settings.OPENAI_API_KEY`, etc.
   - Static/media file settings
     - WhiteNoise for static files
     - Cloudflare R2 storage (optional) for media files
     - Configured via `CLOUDFLARE_R2_*` environment variables
   - Custom user model: `AUTH_USER_MODEL = 'accounts.User'`
   - Login/logout URLs configured
   - Logging configuration

2. **`urls.py`**: 
   - Root URL configuration
   - Includes app URLs (accounts, interviews, cases)
   - Admin interface routing
   - Static/media file serving in development

3. **`asgi.py`**: 
   - ASGI application for WebSocket support
   - Routes HTTP and WebSocket requests
   - Uses `AuthMiddlewareStack` for authenticated WebSocket connections
   - Imports routing after Django initialization

4. **`routing.py`**: 
   - WebSocket URL patterns
   - Routes WebSocket connections to consumers
   - Pattern: `r'ws/interview/(?P<session_id>\w+)/$'` → `InterviewConsumer`

5. **`wsgi.py`**: 
   - WSGI application for HTTP requests
   - Used by Gunicorn in production

6. **`security.py`**: 
   - `SecurityValidator` class for input validation
   - Methods:
     - `sanitize_input()`: Removes HTML/script tags, limits length
     - `detect_prompt_injection()`: Detects suspicious patterns
     - `validate_message()`: Full message validation pipeline
   - Used in WebSocket consumer to validate user input
   - Blocks prompt injection attempts and malicious content

---

## Database Schema

### Core Relationships

```
User (accounts.User)
  └── One-to-Many → InterviewSession
         └── Foreign Key → Case
         └── One-to-Many → Message
         └── One-to-One → Evaluation
                └── One-to-One → Feedback
         └── One-to-Many → Recording
  └── One-to-Many → Case (as generated_by)
```

### Tables

1. **users** - User accounts (custom table name)
   - Fields: id, username, email, password, first_name, last_name, is_staff, is_active, date_joined, created_at, updated_at

2. **interview_sessions** - Interview instances
   - Fields: id, user_id, case_id, mode, status, current_phase, started_at, completed_at, created_at, updated_at
   - Indexes: user_id, case_id

3. **messages** - Chat conversation history
   - Fields: id, session_id, role, content, created_at
   - Indexes: session_id, created_at

4. **cases** - Generated case scenarios
   - Fields: id, title, case_type, prompt, context (JSON), exhibits (JSON), generated_by_id, created_at, updated_at
   - Indexes: generated_by_id, created_at

5. **recordings** - Video/audio files
   - Fields: id, session_id, file, file_type, transcription, created_at
   - Indexes: session_id, created_at

6. **evaluations** - Performance scores
   - Fields: id, session_id (unique), structure_score, hypothesis_score, math_score, insight_score, body_language_score, speech_pacing_score, presence_score, delivery_clarity_score, overall_score, content_analysis (JSON), communication_analysis (JSON), created_at, updated_at

7. **feedback** - Coaching recommendations
   - Fields: id, evaluation_id (unique), summary, strengths (JSON), areas_for_improvement (JSON), recommendations (JSON), created_at, updated_at

---

## Real-Time Communication

### WebSocket Architecture

**Implementation:**
- Django Channels for WebSocket support
- Redis as channel layer backend (production)
- In-memory channel layer (development fallback)
- ASGI application handles both HTTP and WebSocket

**Flow:**
1. Client connects to WebSocket: `/ws/interview/<session_id>/`
2. `InterviewConsumer.connect()` handles connection
3. Authenticates user via `AuthMiddlewareStack`
4. Joins room group: `interview_{session_id}`
5. Initializes `InterviewerAgent` with case data
6. Restores conversation history if session exists
7. Sends opening message or resumes state
8. On message receive:
   - Validates input via `SecurityValidator`
   - Saves user message to database
   - Generates AI response via `InterviewerAgent`
   - Saves AI response to database
   - Updates session phase
   - Broadcasts to room group
9. Messages saved to database via `database_sync_to_async`

**Files:**
- `asgi.py`: ASGI configuration with protocol routing
- `routing.py`: WebSocket URL patterns
- `interviews/consumers.py`: `InterviewConsumer` - WebSocket message handler

**State Management:**
- Conversation history persisted in `Message` model
- Session phase tracked in `InterviewSession.current_phase`
- Interviewer agent state restored on reconnect
- Phase transitions tracked via `InterviewSession.current_phase`

---

## Authentication & Authorization

### User Flow

1. **Registration**: `accounts/views.py` → `signup_view()`
   - Creates user via `UserRegistrationForm`
   - Validates password strength
   - Authenticates and logs in user automatically
   - Redirects to dashboard

2. **Login**: Django's built-in `LoginView`
   - Template: `accounts/login.html`
   - Redirects to dashboard after login (via `LOGIN_REDIRECT_URL`)

3. **Protected Views**: 
   - Most views use `@login_required` decorator
   - Dashboard, interviews, cases require authentication
   - WebSocket connections authenticated via `AuthMiddlewareStack`

4. **Logout**: Django's built-in `LogoutView`
   - Redirects to login page (via `LOGOUT_REDIRECT_URL`)

---

## Frontend Architecture

### Templates Structure

- **Base Template**: `templates/base.html`
  - Tailwind CSS via CDN
  - Navigation bar with conditional auth links
  - Message display (Django messages framework)
  - Footer
  - Block structure: `title`, `extra_css`, `content`, `extra_js`

- **App Templates**:
  - `accounts/`: login.html, signup.html, dashboard.html
  - `interviews/`: list.html, detail.html, start.html, feedback.html
  - `cases/`: list.html, detail.html, generate.html

### Styling

- **Framework**: Tailwind CSS (via CDN)
- **Responsive**: Mobile-first design
- **Theme**: Indigo color scheme (indigo-600, indigo-700)
- **Components**: Cards, buttons, forms styled with Tailwind utilities

### JavaScript

- WebSocket client code in interview detail template
- Handles real-time chat, message display, phase tracking
- Recording upload functionality
- Evaluation display and feedback rendering

---

## Deployment Configuration

### Railway Deployment

**Files:**
- `Procfile`: Defines web process (Gunicorn + Daphne)
- `railway.json`: Railway-specific deployment config
- `runtime.txt`: Python version specification

**Deployment Steps:**
1. Adds PostgreSQL database service
2. Adds Redis service (for WebSockets)
3. Sets environment variables (DATABASE_URL, REDIS_URL, API keys)
4. Runs migrations automatically
5. Collects static files
6. Starts Gunicorn server (HTTP) and Daphne (WebSocket)

**Environment Variables:**
- `SECRET_KEY`: Django secret key
- `DEBUG`: False in production
- `ALLOWED_HOSTS`: Comma-separated or auto-detected from Railway
- `DATABASE_URL`: Auto-set by Railway PostgreSQL
- `REDIS_URL`: Auto-set by Railway Redis
- `OPENAI_API_KEY`: Required for AI features
- `ANTHROPIC_API_KEY`: Optional (for future use)
- `ASSEMBLYAI_API_KEY`: Optional (for future use)
- `PINECONE_API_KEY`: Optional (for future RAG)
- `CLOUDFLARE_R2_*`: Optional (for media storage)

**Static Files:**
- WhiteNoise middleware serves static files
- Static files collected to `staticfiles/` directory

**Media Files:**
- Local storage: `media/` directory (development)
- Cloudflare R2: Configured via `django-storages` (production, optional)

---

## Data Flow Examples

### Starting an Interview

1. User navigates to "Start Interview" → `interview_start_view()`
2. Selects case and mode (interviewer_led/candidate_led)
3. POST request creates `InterviewSession` in database
4. Redirects to `interview_detail_view(session_id)`
5. Frontend JavaScript connects to WebSocket: `/ws/interview/<session_id>/`
6. `InterviewConsumer.connect()` initializes `InterviewerAgent`
7. Agent sends opening message via WebSocket
8. Opening message saved to `Message` table
9. User types response
10. Message validated, saved, AI response generated
11. Conversation continues with phase transitions

### Case Generation

1. User navigates to "Generate Case" → `generate_case_view()`
2. Enters topic and selects case type
3. POST request triggers `CaseGenerator.generate_case()`
4. CrewAI workflow:
   - Researcher searches casebook PDF (if available)
   - Designer creates case structure
   - Writer formats as JSON
5. Case data validated and fixed
6. `Case` model created in database
7. Redirects to case detail view

### Recording & Evaluation

1. User records video/audio during interview
2. File uploaded via `upload_recording_view()`
3. `Recording` model created
4. Transcription triggered asynchronously (`transcribe_recording_async()`)
5. OpenAI Whisper API transcribes audio
6. Transcription saved to `Recording.transcription`
7. Interview completed → `complete_interview_view()`
8. User triggers evaluation → `evaluate_interview_view()`
9. `EvaluatorAgent.evaluate_interview()` analyzes conversation
10. `Evaluation` model created with scores
11. `CoachAgent.generate_feedback()` creates recommendations
12. `Feedback` model created
13. User views feedback via `feedback_view()`

---

## Security Features

### Current Implementation

- **CSRF Protection**: Django's CSRF middleware on all POST requests
- **Authentication**: Django's auth system with custom user model
- **SQL Injection Protection**: Django ORM (parameterized queries)
- **Environment Variables**: Sensitive data in env vars (not in code)
- **Input Validation**: `SecurityValidator` class in `security.py`
  - Sanitizes user input (removes HTML/script tags)
  - Detects prompt injection attempts
  - Validates message length (max 5000 chars)
  - Blocks suspicious patterns
- **WebSocket Security**: Authenticated via `AuthMiddlewareStack`
- **File Upload Validation**: Max file size (100MB), content type checking
- **Secure Cookies**: Enabled in production (SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE)
- **XSS Protection**: SECURE_BROWSER_XSS_FILTER, SECURE_CONTENT_TYPE_NOSNIFF
- **Frame Options**: X_FRAME_OPTIONS = 'DENY'

### Security Validator

**Class**: `SecurityValidator` in `case_interview_simulator/security.py`

**Methods:**
- `sanitize_input(text, max_length)`: Removes HTML/script, limits length
- `detect_prompt_injection(text)`: Detects suspicious patterns
- `validate_message(message)`: Full validation pipeline

**Suspicious Patterns Detected:**
- "ignore previous instructions"
- "system:"
- Prompt injection markers
- Excessive special characters

**Usage**: Called in `InterviewConsumer.receive()` before processing messages

---

## Development Workflow

### Local Setup

1. Create virtual environment: `python -m venv venv`
2. Activate: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Unix)
3. Install dependencies: `pip install -r requirements.txt`
4. Set environment variables in `.env`:
   ```
   SECRET_KEY=your-secret-key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   OPENAI_API_KEY=your-openai-key
   ```
5. Run migrations: `python manage.py migrate`
6. Create superuser: `python manage.py createsuperuser`
7. (Optional) Load casebook PDF to project root
8. Run server: `python manage.py runserver`

### Database

- **Development**: SQLite (`db.sqlite3`) - auto-created
- **Production**: PostgreSQL (via Railway `DATABASE_URL`)

### Code Quality

- **Formatting**: Black (`black .`)
- **Linting**: Flake8 (`flake8 .`)
- **Type Checking**: MyPy (`mypy .`)
- **Testing**: Pytest + pytest-django (`pytest`)

### Management Commands

- `python manage.py createsuperuser`: Create admin user
- `python manage.py migrate`: Run database migrations
- `python manage.py collectstatic`: Collect static files
- `python manage.py generate_candidate_cases`: Pre-generate cases

---

## Current Implementation Status

### ✅ Completed Features

**Phase 1: Infrastructure**
- Django project structure
- All apps created and configured
- Database models implemented
- User authentication system
- Base templates with Tailwind CSS
- WebSocket infrastructure

**Phase 2: AI Agents**
- ✅ Case Generator agent (CrewAI with RAG)
- ✅ Interviewer agent (phase-aware, adaptive)
- ✅ Evaluator agent (performance scoring)
- ✅ Coach agent (personalized feedback)

**Phase 3: Real-Time Communication**
- ✅ WebSocket consumer with state management
- ✅ Conversation persistence
- ✅ Phase tracking and transitions
- ✅ Input validation and security

**Phase 4: Recording & Analysis**
- ✅ Recording upload
- ✅ Transcription (OpenAI Whisper)
- ✅ Evaluation generation
- ✅ Feedback generation

**Phase 5: Security**
- ✅ Input sanitization
- ✅ Prompt injection detection
- ✅ CSRF protection
- ✅ Authentication on all views

**Phase 6: Storage**
- ✅ Local file storage
- ✅ Cloudflare R2 integration (optional)

---

## Key Dependencies

**Core Framework:**
- `Django>=4.2,<5.0`: Web framework
- `channels>=4.0.0`: WebSocket support
- `channels-redis>=4.1.0`: Redis channel layer
- `daphne>=4.0.0`: ASGI server

**Database:**
- `psycopg2-binary>=2.9.0`: PostgreSQL adapter

**AI/ML:**
- `openai>=1.0.0`: OpenAI API client
- `anthropic>=0.7.0`: Anthropic API (optional)
- `crewai>=0.1.0`: Multi-agent framework
- `crewai_tools>=0.1.0`: CrewAI tools (PDF search)

**Storage:**
- `django-storages>=1.14.0`: Cloud storage backends
- `boto3>=1.28.0`: AWS S3/R2 client

**Utilities:**
- `python-dotenv>=1.0.0`: Environment variable loading
- `django-environ>=0.11.0`: Django environment management
- `whitenoise>=6.6.0`: Static file serving
- `Pillow>=10.0.0`: Image processing

**Development:**
- `pytest>=7.4.0`: Testing framework
- `pytest-django>=4.7.0`: Django test integration
- `black>=23.0.0`: Code formatter
- `flake8>=6.1.0`: Linter
- `mypy>=1.5.0`: Type checker

**Production:**
- `gunicorn>=21.2.0`: WSGI server
- `redis>=5.0.0`: Redis client

---

## File Naming Conventions

- **Models**: `models.py` in each app
- **Views**: `views.py` in each app
- **URLs**: `urls.py` in each app
- **Templates**: `templates/<app_name>/<view_name>.html`
- **Migrations**: `migrations/0001_initial.py`, etc.
- **Management Commands**: `management/commands/<command_name>.py`
- **Agents**: `agents/<agent_name>.py` (e.g., `interviewer.py`, `case_generator.py`)

---

## Summary

This Django application implements a complete AI-powered case interview simulator with:

- **Multi-agent AI system**: CrewAI for case generation, OpenAI for interviewing/evaluation/coaching
- **Real-time communication**: WebSocket-based chat with state persistence
- **RAG capabilities**: Casebook PDF search for realistic case generation
- **Performance evaluation**: Automated scoring and personalized feedback
- **Security**: Input validation, prompt injection protection, CSRF protection
- **Scalable architecture**: Modular app structure, optional cloud storage

The system is production-ready with all core features implemented, including case generation, real-time interviewing, evaluation, and coaching feedback.
