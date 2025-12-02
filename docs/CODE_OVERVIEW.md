# Code Overview - AI Case Interview Simulator

A high-level explanation of the codebase architecture and components.

## Project Overview

This is a Django-based web application for practicing consulting and product management case interviews. The system uses multi-agent AI workflows to generate cases, conduct interviews, evaluate performance, and provide coaching feedback.

**Technology Stack:**
- **Backend**: Django 4.2+ (full-stack with templates)
- **Database**: PostgreSQL (production) / SQLite (development)
- **Real-time**: Django Channels with WebSockets
- **Deployment**: Railway
- **Frontend**: Django Templates + Tailwind CSS

---

## Architecture Overview

### Application Structure

The project follows Django's app-based architecture with 6 main applications:

```
mgt-802/
├── case_interview_simulator/  # Main Django project configuration
├── accounts/                   # User authentication & management
├── interviews/                 # Interview sessions & chat
├── cases/                      # Case generation & management
├── agents/                     # Multi-agent AI system (to be implemented)
├── analysis/                   # Performance evaluation
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
- `views.py`: 
  - `signup_view()`: User registration
  - `dashboard_view()`: User dashboard (requires login)
- `forms.py`: `UserRegistrationForm` for signup
- `urls.py`: Routes for login, logout, signup, dashboard

**Database Model:**
- `User`: Stores username, email, password, timestamps

---

### 2. `interviews/` - Interview Sessions

**Purpose**: Manages interview sessions and real-time chat communication.

**Key Files:**
- `models.py`:
  - `InterviewSession`: Tracks interview state, mode, timestamps
  - `Message`: Stores chat messages in interview sessions
- `views.py`: 
  - `interview_list_view()`: List all user's interviews
  - `interview_start_view()`: Start new interview
  - `interview_detail_view()`: View interview details
- `consumers.py`: `InterviewConsumer` - WebSocket consumer for real-time chat
- `urls.py`: Routes for interview management

**Database Models:**
- `InterviewSession`: Links user, case, mode, status, timestamps
- `Message`: Stores conversation history (role, content, timestamp)

**Interview Modes:**
- Interviewer-Led (McKinsey-style)
- Candidate-Led (BCG/Bain-style)
- PM Product Case

---

### 3. `cases/` - Case Management

**Purpose**: Stores and manages generated interview cases.

**Key Files:**
- `models.py`: `Case` model storing case data
- `views.py`:
  - `case_list_view()`: List all cases
  - `case_detail_view()`: View case details
- `urls.py`: Routes for case browsing

**Database Model:**
- `Case`: Stores title, type, prompt, context (JSON), exhibits (JSON), creator

**Case Types:**
- Consulting
- Product Management

---

### 4. `agents/` - Multi-Agent System

**Purpose**: Will contain AI agent classes for case generation, interviewing, evaluation, and coaching.

**Current Status**: Placeholder - to be implemented in Phase 2

**Planned Agents:**
- Case Generator Agent
- Interviewer Agent
- Evaluator Agent
- Coach Agent

---

### 5. `analysis/` - Performance Evaluation

**Purpose**: Handles recording storage and performance evaluation.

**Key Files:**
- `models.py`:
  - `Recording`: Stores video/audio files and transcriptions
  - `Evaluation`: Stores scores and analysis results

**Database Models:**
- `Recording`: Links to session, stores file path, transcription
- `Evaluation`: One-to-one with session, stores:
  - Content scores (structure, hypothesis, math, insights)
  - Communication scores (body language, speech pacing, presence, delivery)
  - Overall score
  - Detailed analysis JSON

---

### 6. `feedback/` - Coaching Feedback

**Purpose**: Generates and stores coaching recommendations.

**Key Files:**
- `models.py`: `Feedback` model for coaching recommendations

**Database Model:**
- `Feedback`: One-to-one with evaluation, stores:
  - Summary
  - Strengths (JSON array)
  - Areas for improvement (JSON array)
  - Recommendations (JSON array)

---

## Project Configuration

### `case_interview_simulator/` - Main Project Settings

**Key Files:**

1. **`settings.py`**: 
   - Database configuration (PostgreSQL/SQLite)
   - Installed apps configuration
   - Channels/WebSocket configuration
   - Security settings
   - API key management (OpenAI, Anthropic, etc.)
   - Static/media file settings

2. **`urls.py`**: 
   - Root URL configuration
   - Includes app URLs (accounts, interviews, cases)
   - Admin interface routing

3. **`asgi.py`**: 
   - ASGI application for WebSocket support
   - Routes HTTP and WebSocket requests
   - Uses `AuthMiddlewareStack` for authenticated WebSocket connections

4. **`routing.py`**: 
   - WebSocket URL patterns
   - Routes WebSocket connections to consumers

5. **`wsgi.py`**: 
   - WSGI application for HTTP requests
   - Used by Gunicorn in production

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
```

### Tables

1. **users** - User accounts
2. **interview_sessions** - Interview instances
3. **messages** - Chat conversation history
4. **cases** - Generated case scenarios
5. **recordings** - Video/audio files
6. **evaluations** - Performance scores
7. **feedback** - Coaching recommendations

---

## Real-Time Communication

### WebSocket Architecture

**Implementation:**
- Django Channels for WebSocket support
- Redis as channel layer backend (production)
- In-memory channel layer (development fallback)

**Flow:**
1. Client connects to WebSocket: `/ws/interview/<session_id>/`
2. `InterviewConsumer` handles connection
3. Messages broadcast via channel layer groups
4. Messages saved to database via async ORM

**Files:**
- `asgi.py`: ASGI configuration
- `routing.py`: WebSocket URL patterns
- `interviews/consumers.py`: WebSocket message handler

---

## Authentication & Authorization

### User Flow

1. **Registration**: `accounts/views.py` → `signup_view()`
   - Creates user via `UserRegistrationForm`
   - Authenticates and logs in user
   - Redirects to dashboard

2. **Login**: Django's built-in `LoginView`
   - Template: `accounts/login.html`
   - Redirects to dashboard after login

3. **Protected Views**: 
   - Most views use `@login_required` decorator
   - Dashboard, interviews, cases require authentication

---

## Frontend Architecture

### Templates Structure

- **Base Template**: `templates/base.html`
  - Tailwind CSS via CDN
  - Navigation bar
  - Message display
  - Footer

- **App Templates**:
  - `accounts/`: login, signup, dashboard
  - `interviews/`: list, detail, start
  - `cases/`: list, detail

### Styling

- **Framework**: Tailwind CSS (via CDN)
- **Responsive**: Mobile-first design
- **Theme**: Indigo color scheme

---

## Deployment Configuration

### Railway Deployment

**Files:**
- `Procfile`: Defines web and worker processes
- `railway.json`: Railway-specific deployment config
- `runtime.txt`: Python version specification

**Deployment Steps:**
1. Adds PostgreSQL database service
2. Adds Redis service (for WebSockets)
3. Sets environment variables (DATABASE_URL, REDIS_URL, API keys)
4. Runs migrations automatically
5. Collects static files
6. Starts Gunicorn server

**Environment Variables:**
- `SECRET_KEY`: Django secret key
- `DEBUG`: False in production
- `DATABASE_URL`: Auto-set by Railway PostgreSQL
- `REDIS_URL`: Auto-set by Railway Redis
- API keys (OpenAI, Anthropic, AssemblyAI, Pinecone)

---

## Data Flow Examples

### Starting an Interview

1. User clicks "Start Interview" → `interview_start_view()`
2. Creates `InterviewSession` in database
3. User connects via WebSocket to session
4. AI agent (future) sends case prompt
5. Messages exchanged via WebSocket
6. Messages saved to `Message` table

### Recording & Evaluation

1. User records video/audio during interview
2. File uploaded → `Recording` model created
3. Transcription processed (future)
4. Evaluator agent analyzes (future)
5. `Evaluation` created with scores
6. Coach agent generates feedback (future)
7. `Feedback` created with recommendations

---

## Security Features

### Current Implementation

- **CSRF Protection**: Django's CSRF middleware
- **Authentication**: Django's auth system
- **SQL Injection Protection**: Django ORM
- **Environment Variables**: Sensitive data in env vars (not in code)

### Planned (Phase 6)

- Prompt injection protection
- Input sanitization
- Controlled exhibit release

---

## Development Workflow

### Local Setup

1. Create virtual environment
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variables in `.env`
4. Run migrations: `python manage.py migrate`
5. Create superuser: `python manage.py createsuperuser`
6. Run server: `python manage.py runserver`

### Database

- **Development**: SQLite (`db.sqlite3`)
- **Production**: PostgreSQL (via Railway)

### Code Quality

- **Formatting**: Black
- **Linting**: Flake8
- **Type Checking**: MyPy
- **Testing**: Pytest + pytest-django

---

## Current Implementation Status

### ✅ Completed (Phase 1)

- Django project structure
- All apps created
- Database models implemented
- User authentication system
- Basic views and templates
- WebSocket infrastructure (consumer skeleton)
- Base UI with Tailwind CSS

### 🚧 To Be Implemented

- **Phase 2**: Conversational chat engine, Case Generator agent, Interviewer agent
- **Phase 3**: RAG infrastructure
- **Phase 4**: Recording upload and transcription
- **Phase 5**: Evaluator and Coach agents
- **Phase 6**: Security enhancements
- **Phase 7**: UI/UX polish

---

## Key Dependencies

- **Django 4.2+**: Web framework
- **channels**: WebSocket support
- **channels-redis**: Redis channel layer
- **psycopg2-binary**: PostgreSQL adapter
- **whitenoise**: Static file serving
- **gunicorn**: Production WSGI server
- **openai / anthropic**: AI model APIs (future)
- **python-dotenv / django-environ**: Environment variable management

---

## File Naming Conventions

- **Models**: `models.py` in each app
- **Views**: `views.py` in each app
- **URLs**: `urls.py` in each app
- **Templates**: `templates/<app_name>/<view_name>.html`
- **Migrations**: `migrations/0001_initial.py`, etc.

---

## Summary

This Django application follows a modular, app-based architecture with clear separation of concerns:

- **accounts**: User management
- **interviews**: Interview sessions and real-time chat
- **cases**: Case data management
- **analysis**: Performance evaluation
- **feedback**: Coaching recommendations
- **agents**: AI agent system (to be built)

The foundation is in place for Phase 1, with database models, authentication, basic views, and WebSocket infrastructure ready. Future phases will add AI agents, recording/analysis, and enhanced UI/UX features.

