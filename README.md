# AI Case Interview Simulator

A Django-based web application for MBA/Master's students to practice consulting and product management case interviews. The system uses multi-agent AI workflows to generate cases, conduct interviews, evaluate performance, and provide coaching feedback.

## Project Status

**Phase 1: Project Setup & Infrastructure** ✅ Complete

- Django project structure initialized
- All core apps created (accounts, interviews, cases, agents, analysis, feedback)
- Database models implemented
- Base templates with Tailwind CSS
- User authentication system
- Dashboard and basic UI

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL database
- Redis (for WebSocket support via Channels)

### Installation

1. **Clone the repository** (if applicable) or navigate to the project directory

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables:**
   - Copy `.env.example` to `.env` (if available)
   - Or create a `.env` file with the following variables:
     ```
     SECRET_KEY=your-secret-key-here
     DEBUG=True
     ALLOWED_HOSTS=localhost,127.0.0.1
     DATABASE_URL=postgresql://user:password@localhost:5432/case_interview_db
     REDIS_URL=redis://localhost:6379/0
     ```

6. **Set up the database:**
   ```bash
   python manage.py migrate
   ```

7. **Create a superuser:**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

9. **Access the application:**
   - Open your browser and navigate to `http://localhost:8000`
   - Access the admin panel at `http://localhost:8000/admin`

## Project Structure

```
mgt-802/
├── manage.py
├── requirements.txt
├── Procfile
├── runtime.txt
├── case_interview_simulator/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── routing.py
├── accounts/          # User authentication and management
├── interviews/        # Core interview functionality
├── cases/             # Case generation and management
├── agents/            # Multi-agent workflow system
├── analysis/          # Performance evaluation
├── feedback/          # Coaching feedback generation
├── templates/         # HTML templates
├── static/            # Static files (CSS, JS, images)
└── media/             # User-uploaded files
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

## Next Steps

See `IMPLEMENTATION_PLAN.md` for the complete implementation roadmap. The next phase will focus on:
- Conversational chat engine with WebSockets
- Case Generator agent
- Interviewer agent

## License

This project is for educational purposes (MGT-802).
