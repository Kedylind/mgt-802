# AI Case Interview Simulator

A Django-based web application for MBA/Master's students to practice consulting and product management case interviews. The system uses multi-agent AI workflows powered by CrewAI and OpenAI to generate cases, conduct interviews, evaluate performance, and provide coaching feedback.

## Project Status

**Core Features** ✅ Complete

- ✅ User authentication and management
- ✅ AI-powered case generation with RAG (CrewAI)
- ✅ Real-time interview sessions via WebSockets
- ✅ Adaptive interviewer agent with phase management
- ✅ Performance evaluation and scoring
- ✅ Personalized coaching feedback
- ✅ Recording upload and transcription
- ✅ Security features (input validation, prompt injection protection)

## Features

### Case Generation
- **AI-Powered**: Uses CrewAI with multi-agent workflow (Researcher, Designer, Writer)
- **RAG Integration**: Searches casebook PDF for realistic case patterns
- **Case Types**: Consulting and Product Management cases
- **Structured Output**: JSON format with context, exhibits (tables, charts), and prompts

### Interview Sessions
- **Real-Time Chat**: WebSocket-based conversation with AI interviewer
- **Two Modes**: Interviewer-led (McKinsey-style) and Candidate-led (BCG/Bain-style)
- **Phase Management**: Automatic transitions through framework → data analysis → recommendation → pushback → conclusion
- **Exhibit Release**: On-demand data release (max 3 exhibits per interview)
- **State Persistence**: Resumes conversations on reconnect

### Evaluation & Feedback
- **Automated Scoring**: Evaluates structure, hypothesis, math, and insights (0-100 scale)
- **Personalized Feedback**: AI-generated coaching recommendations
- **Recording Analysis**: Video/audio upload with automatic transcription (OpenAI Whisper)
- **Detailed Reports**: Strengths, areas for improvement, and specific drills

## Project Structure

```
mgt-802/
├── manage.py
├── requirements.txt
├── Procfile                    # Railway deployment config
├── runtime.txt                 # Python version
├── case_interview_simulator/   # Main Django project
│   ├── settings.py            # Django settings
│   ├── urls.py               # Root URL configuration
│   ├── wsgi.py               # WSGI application
│   ├── asgi.py               # ASGI application (WebSockets)
│   ├── routing.py            # WebSocket routing
│   └── security.py           # Security validation utilities
├── accounts/                  # User authentication & management
│   ├── models.py            # Custom User model
│   ├── views.py             # Signup, dashboard views
│   ├── forms.py              # Registration form
│   └── urls.py               # Account URLs
├── interviews/                # Interview sessions & chat
│   ├── models.py            # InterviewSession, Message models
│   ├── views.py             # Interview views
│   ├── consumers.py         # WebSocket consumer
│   └── urls.py               # Interview URLs
├── cases/                     # Case generation & management
│   ├── models.py            # Case model
│   ├── views.py             # Case views
│   ├── urls.py              # Case URLs
│   └── management/commands/ # Django management commands
├── agents/                    # Multi-agent AI system
│   ├── case_generator.py    # Case generation agent (CrewAI)
│   ├── interviewer.py       # Interviewer agent
│   ├── evaluator.py          # Evaluator agent
│   └── coach.py             # Coach agent
├── analysis/                  # Performance evaluation
│   └── models.py            # Recording, Evaluation models
├── feedback/                  # Coaching feedback
│   └── models.py            # Feedback model
├── templates/                 # HTML templates
│   ├── base.html            # Base template
│   ├── accounts/            # Auth templates
│   ├── interviews/          # Interview templates
│   └── cases/               # Case templates
├── static/                   # Static files (CSS, JS)
└── media/                    # User-uploaded files
```

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
flake8 .
```

### Management Commands

```bash
# Generate sample cases
python manage.py create_sample_cases

# Pre-generate candidate cases
python manage.py generate_candidate_cases

# Seed database with cases
python manage.py seed_cases
```

## Technology Stack

- **Backend**: Django 4.2+
- **Real-time**: Django Channels (WebSockets)
- **AI Framework**: CrewAI (multi-agent orchestration)
- **AI Models**: OpenAI GPT-4o-mini, Whisper
- **Database**: PostgreSQL (production) / SQLite (development)
- **Cache/Queue**: Redis (optional, falls back to in-memory)
- **Storage**: Cloudflare R2
- **Frontend**: Django Templates + Tailwind CSS
- **Deployment**: Railway

## Key Components

### Agents

- **CaseGenerator**: Generates cases using CrewAI with RAG (PDF casebook search)
- **InterviewerAgent**: Conducts adaptive interviews with phase management
- **EvaluatorAgent**: Scores performance across multiple dimensions
- **CoachAgent**: Generates personalized feedback and recommendations

### Models

- **User**: Custom user model with timestamps
- **Case**: Generated case scenarios with context and exhibits
- **InterviewSession**: Interview instances with phase tracking
- **Message**: Conversation history
- **Recording**: Video/audio files with transcriptions
- **Evaluation**: Performance scores and analysis
- **Feedback**: Coaching recommendations

## Security

- Input validation and sanitization
- Prompt injection detection
- CSRF protection
- Authentication on all views
- Secure WebSocket connections
- File upload validation

## Deployment

The application is configured for deployment on Railway. See `docs/RAILWAY_DEPLOYMENT.md` for details.

**Environment Variables Required:**
- `SECRET_KEY`
- `OPENAI_API_KEY`
- `DATABASE_URL` (auto-set by Railway)
- `REDIS_URL` (auto-set by Railway, optional)

## Documentation

- `docs/CODE_OVERVIEW.md`: Detailed technical documentation
- `docs/API_DOCUMENTATION.md`: API endpoints documentation
- `docs/USER_GUIDE.md`: User-facing documentation
- `docs/IMPLEMENTATION_PLAN.md`: Development roadmap

## License

This project is for educational purposes (MGT-802).
