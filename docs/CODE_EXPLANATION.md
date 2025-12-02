# AI Case Interview Simulator - Complete Code Explanation

This document provides a comprehensive explanation of all code in the AI Case Interview Simulator project. The project is a Django-based web application for practicing consulting and product management case interviews using AI agents.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture & Structure](#architecture--structure)
3. [Core Configuration Files](#core-configuration-files)
4. [Django Apps](#django-apps)
5. [Database Models](#database-models)
6. [Views & URL Routing](#views--url-routing)
7. [WebSocket & Real-time Communication](#websocket--real-time-communication)
8. [Deployment Configuration](#deployment-configuration)
9. [Dependencies & Requirements](#dependencies--requirements)

---

## Project Overview

### Purpose
The AI Case Interview Simulator helps MBA/Master's students practice consulting and product management case interviews. It uses multi-agent AI workflows to:
- Generate realistic case scenarios
- Conduct interactive mock interviews
- Record and analyze performance
- Provide structured scoring and coaching feedback

### Technology Stack
- **Backend Framework**: Django 4.2+ (Python web framework)
- **Database**: PostgreSQL (production) / SQLite (local development)
- **Real-time Communication**: Django Channels (WebSocket support)
- **Task Queue**: Redis (for WebSocket channel layers)
- **Deployment**: Railway
- **AI Integration**: OpenAI, Anthropic (configured for future use)

---

## Architecture & Structure

### Project Layout
```
mgt-802/
├── manage.py                          # Django command-line utility
├── requirements.txt                   # Python dependencies
├── Procfile                          # Railway deployment commands
├── runtime.txt                       # Python version specification
├── railway.json                      # Railway deployment configuration
├── db.sqlite3                        # SQLite database (local only)
│
├── case_interview_simulator/         # Main Django project directory
│   ├── __init__.py
│   ├── settings.py                   # Project-wide configuration
│   ├── urls.py                       # Root URL routing
│   ├── wsgi.py                       # WSGI application (HTTP)
│   ├── asgi.py                       # ASGI application (HTTP + WebSocket)
│   ├── routing.py                    # WebSocket URL routing
│   └── templatetags/
│       └── custom_filters.py        # Custom Django template filters
│
├── accounts/                         # User authentication app
├── cases/                            # Case generation & management app
├── interviews/                       # Interview sessions app
├── agents/                           # AI agent system (Phase 2)
├── analysis/                         # Performance evaluation app
├── feedback/                         # Coaching feedback app
│
├── templates/                        # HTML templates
├── static/                           # Static files (CSS, JS, images)
└── media/                            # User-uploaded files
```

### Django Apps Organization
The project uses Django's app-based architecture for modularity:

- **accounts**: Handles user registration, login, authentication
- **cases**: Manages case generation and storage
- **interviews**: Core interview session functionality
- **agents**: Future AI agent implementations
- **analysis**: Performance evaluation and scoring
- **feedback**: Coaching recommendations

---

## Core Configuration Files

### 1. `manage.py`
**Location**: Root directory  
**Purpose**: Django's command-line utility for administrative tasks

```python
# Key functionality:
# - Sets default Django settings module
# - Provides access to Django management commands
# - Used for: runserver, migrate, createsuperuser, etc.
```

**Commands you'll use**:
- `python manage.py runserver` - Start development server
- `python manage.py migrate` - Apply database migrations
- `python manage.py createsuperuser` - Create admin user
- `python manage.py collectstatic` - Collect static files for deployment

---

### 2. `case_interview_simulator/settings.py`
**Location**: `case_interview_simulator/settings.py`  
**Purpose**: Central configuration file for the entire Django project

#### Key Sections Explained:

##### **Base Configuration** (Lines 8-33)
```python
BASE_DIR = Path(__file__).resolve().parent.parent
```
- Defines the project root directory
- Uses `pathlib.Path` for cross-platform path handling

##### **Environment Variables** (Lines 11-20)
```python
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
SECRET_KEY = env('SECRET_KEY', default='...')
```
- Uses `django-environ` to read configuration from `.env` file
- Keeps secrets out of code (security best practice)
- Falls back to defaults if environment variables aren't set

##### **Security Settings** (Lines 19-33)
```python
SECRET_KEY = env('SECRET_KEY', default='...')
DEBUG = env('DEBUG', default=False)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])
```
- `SECRET_KEY`: Used for cryptographic signing (sessions, CSRF tokens)
- `DEBUG`: Shows detailed error pages in development (False in production)
- `ALLOWED_HOSTS`: Prevents HTTP Host header attacks (which domains can access the app)

##### **Installed Apps** (Lines 36-50)
```python
INSTALLED_APPS = [
    'django.contrib.admin',        # Admin interface
    'django.contrib.auth',         # Authentication system
    'django.contrib.contenttypes', # Content type framework
    'django.contrib.sessions',     # Session framework
    'django.contrib.messages',     # Messaging framework
    'django.contrib.staticfiles',  # Static file management
    'channels',                    # WebSocket support
    'accounts',                    # Our custom apps
    'interviews',
    'cases',
    'agents',
    'analysis',
    'feedback',
]
```
Each app provides specific functionality. Django's built-in apps handle authentication, sessions, etc., while our custom apps contain business logic.

##### **Middleware** (Lines 52-61)
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',  # Security headers
    'whitenoise.middleware.WhiteNoiseMiddleware',      # Static file serving
    'django.contrib.sessions.middleware.SessionMiddleware',  # Session management
    'django.middleware.common.CommonMiddleware',       # Common operations
    'django.middleware.csrf.CsrfViewMiddleware',       # CSRF protection
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # User authentication
    'django.contrib.messages.middleware.MessageMiddleware',  # Flash messages
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Clickjacking protection
]
```
Middleware are functions that process requests/responses globally. They run in order, wrapping your views.

##### **Database Configuration** (Lines 84-97)
```python
if env('DATABASE_URL', default=None):
    DATABASES = {'default': env.db('DATABASE_URL')}  # PostgreSQL (production)
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',  # SQLite (local development)
        }
    }
```
- **Local Development**: Uses SQLite (file-based, no setup needed)
- **Production (Railway)**: Automatically uses PostgreSQL via `DATABASE_URL`
- This dual setup allows easy local development while supporting production databases

##### **Custom User Model** (Line 140)
```python
AUTH_USER_MODEL = 'accounts.User'
```
- Tells Django to use our custom User model instead of the default
- Important: Must be set before first migration
- Allows extending user functionality (added `created_at`, `updated_at` fields)

##### **Channels Configuration** (Lines 147-165)
```python
if REDIS_URL:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {"hosts": [REDIS_URL]},
        },
    }
else:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        },
    }
```
- **Redis (Production)**: Distributed channel layer for WebSockets across multiple servers
- **In-Memory (Local)**: Simple local development, doesn't persist across restarts
- Enables real-time WebSocket communication for interview chat

##### **Security Settings for Production** (Lines 175-182)
```python
if not DEBUG:
    SECURE_SSL_REDIRECT = True        # Force HTTPS
    SESSION_COOKIE_SECURE = True      # Only send session cookies over HTTPS
    CSRF_COOKIE_SECURE = True         # Only send CSRF cookies over HTTPS
    SECURE_BROWSER_XSS_FILTER = True  # Enable browser XSS filtering
    SECURE_CONTENT_TYPE_NOSNIFF = True  # Prevent MIME type sniffing
    X_FRAME_OPTIONS = 'DENY'          # Prevent embedding in iframes
```
Only enabled in production (`DEBUG=False`) to enhance security.

---

### 3. `case_interview_simulator/urls.py`
**Location**: `case_interview_simulator/urls.py`  
**Purpose**: Root URL routing - maps URLs to views

```python
urlpatterns = [
    path('admin/', admin.site.urls),           # Django admin at /admin/
    path('', include('accounts.urls')),        # Account routes at root (/login, /signup)
    path('interviews/', include('interviews.urls')),  # Interview routes
    path('cases/', include('cases.urls')),     # Case routes
]

# Serve media files in development only
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

**URL Structure**:
- `/` → Account routes (login, signup, dashboard)
- `/admin/` → Django admin interface
- `/interviews/` → Interview-related pages
- `/cases/` → Case browsing pages

The `include()` function delegates URL routing to each app's `urls.py` file for modularity.

---

### 4. `case_interview_simulator/wsgi.py`
**Location**: `case_interview_simulator/wsgi.py`  
**Purpose**: WSGI (Web Server Gateway Interface) application entry point

```python
application = get_wsgi_application()
```

- Used by production servers (Gunicorn, uWSGI) to serve HTTP requests
- WSGI is the standard Python web server interface
- Handles traditional HTTP requests (GET, POST, etc.)

---

### 5. `case_interview_simulator/asgi.py`
**Location**: `case_interview_simulator/asgi.py`  
**Purpose**: ASGI (Asynchronous Server Gateway Interface) application entry point

```python
application = ProtocolTypeRouter({
    "http": django_asgi_app,              # Handle HTTP requests
    "websocket": AuthMiddlewareStack(      # Handle WebSocket connections
        URLRouter(routing.websocket_urlpatterns)
    ),
})
```

**Key Differences from WSGI**:
- **ASGI** supports both HTTP and WebSocket connections
- **WSGI** only supports HTTP
- Django Channels requires ASGI for real-time features

**What it does**:
1. Routes HTTP requests to Django's normal request handler
2. Routes WebSocket connections through authentication middleware
3. Then routes to the appropriate WebSocket consumer (interview chat)

---

### 6. `case_interview_simulator/routing.py`
**Location**: `case_interview_simulator/routing.py`  
**Purpose**: WebSocket URL routing

```python
websocket_urlpatterns = [
    re_path(r'ws/interview/(?P<session_id>\w+)/$', consumers.InterviewConsumer.as_asgi()),
]
```

**WebSocket URL Pattern**:
- Pattern: `ws/interview/{session_id}/`
- Example: `ws://localhost:8000/ws/interview/123/`
- Matches the session ID from the URL path
- Routes to `InterviewConsumer` (handles chat messages)

The `(?P<session_id>\w+)` is a named regex group that captures the session ID.

---

## Django Apps

### 1. Accounts App (`accounts/`)
**Purpose**: User authentication and account management

#### **Models** (`accounts/models.py`)

```python
class User(AbstractUser):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Explanation**:
- Extends Django's `AbstractUser` (gets username, email, password, etc.)
- Adds `created_at` and `updated_at` timestamps
- Uses custom database table name: `users`
- Sets `AUTH_USER_MODEL = 'accounts.User'` in settings

**Inherited Fields from AbstractUser**:
- `username`, `email`, `password`
- `first_name`, `last_name`
- `is_staff`, `is_superuser`, `is_active`
- `date_joined`, `last_login`

#### **Forms** (`accounts/forms.py`)

```python
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
```

**Explanation**:
- Extends Django's `UserCreationForm`
- Adds email, first_name, last_name fields
- `password1` and `password2` are automatically validated (matching, strength)
- `save()` method ensures email is properly set

#### **Views** (`accounts/views.py`)

##### **signup_view** (Lines 12-32)
```python
@require_http_methods(["GET", "POST"])
def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')  # Already logged in
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Create user in database
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)  # Log them in automatically
                messages.success(request, f'Welcome, {username}!')
                return redirect('dashboard')
    else:
        form = UserRegistrationForm()  # GET request - show empty form
    
    return render(request, 'accounts/signup.html', {'form': form})
```

**Flow**:
1. Check if user is already logged in → redirect to dashboard
2. If POST (form submitted):
   - Validate form data
   - Save new user to database
   - Authenticate and log them in
   - Redirect to dashboard
3. If GET → show empty registration form

##### **dashboard_view** (Lines 35-38)
```python
@login_required
def dashboard_view(request):
    return render(request, 'accounts/dashboard.html')
```

- `@login_required` decorator redirects unauthenticated users to login
- Simple view that renders the dashboard template

#### **URLs** (`accounts/urls.py`)

```python
urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),        # / → Dashboard
    path('signup/', views.signup_view, name='signup'),       # /signup/ → Registration
    path('login/', auth_views.LoginView.as_view(...), name='login'),   # /login/ → Login
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),   # /logout/ → Logout
]
```

Django's built-in `LoginView` and `LogoutView` handle authentication logic automatically.

---

### 2. Cases App (`cases/`)
**Purpose**: Manage interview case scenarios

#### **Models** (`cases/models.py`)

```python
class Case(models.Model):
    CONSULTING = 'consulting'
    PRODUCT_MANAGEMENT = 'product_management'
    
    CASE_TYPE_CHOICES = [
        (CONSULTING, 'Consulting'),
        (PRODUCT_MANAGEMENT, 'Product Management'),
    ]
    
    title = models.CharField(max_length=200)
    case_type = models.CharField(max_length=20, choices=CASE_TYPE_CHOICES)
    prompt = models.TextField(help_text='The main case prompt/question')
    context = models.JSONField(default=dict, help_text='Additional context')
    exhibits = models.JSONField(default=list, help_text='Tables, charts, data')
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Fields Explained**:
- `title`: Human-readable case name
- `case_type`: Choice field (consulting or product management)
- `prompt`: The main question/scenario for the case
- `context`: JSON field for flexible additional data (background, company info, etc.)
- `exhibits`: JSON array for data tables, charts, financials
- `generated_by`: Foreign key to User (who created it, nullable)
- Timestamps automatically set

**JSON Fields**:
- Store structured data without defining every possible field
- Flexible for future case variations
- Examples: `context: {"industry": "tech", "revenue": "$1B"}`

#### **Views** (`cases/views.py`)

##### **case_list_view** (Lines 9-13)
```python
@login_required
def case_list_view(request):
    cases = Case.objects.all()
    return render(request, 'cases/list.html', {'cases': cases})
```

- Fetches all cases from database
- Passes them to template for display

##### **case_detail_view** (Lines 16-20)
```python
@login_required
def case_detail_view(request, case_id):
    case = get_object_or_404(Case, id=case_id)
    return render(request, 'cases/detail.html', {'case': case})
```

- `get_object_or_404()`: Returns case if found, 404 error if not
- Displays full case details (prompt, context, exhibits)

#### **URLs** (`cases/urls.py`)

```python
urlpatterns = [
    path('', views.case_list_view, name='case_list'),              # /cases/ → List
    path('<int:case_id>/', views.case_detail_view, name='case_detail'),  # /cases/1/ → Detail
]
```

- `<int:case_id>` captures integer from URL and passes to view

---

### 3. Interviews App (`interviews/`)
**Purpose**: Core interview session functionality

#### **Models** (`interviews/models.py`)

##### **InterviewSession** (Lines 8-56)
```python
class InterviewSession(models.Model):
    INTERVIEWER_LED = 'interviewer_led'
    CANDIDATE_LED = 'candidate_led'
    PM_PRODUCT_CASE = 'pm_product_case'
    
    MODE_CHOICES = [
        (INTERVIEWER_LED, 'Interviewer-Led'),
        (CANDIDATE_LED, 'Candidate-Led'),
        (PM_PRODUCT_CASE, 'PM Product Case'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    case = models.ForeignKey('cases.Case', on_delete=models.SET_NULL, null=True)
    mode = models.CharField(max_length=20, choices=MODE_CHOICES)
    status = models.CharField(max_length=20, default='not_started', choices=[...])
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Key Relationships**:
- `user`: Foreign key to User (one user can have many sessions)
- `case`: Foreign key to Case (optional, can be null)
- `on_delete=models.CASCADE`: If user is deleted, delete their sessions
- `on_delete=models.SET_NULL`: If case is deleted, set to null (keep session)

**Status Choices**:
- `not_started`: Created but not begun
- `in_progress`: Currently active
- `completed`: Finished successfully
- `abandoned`: Started but never finished

##### **Message** (Lines 58-84)
```python
class Message(models.Model):
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=[
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ])
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
```

**Purpose**: Stores chat messages in interview sessions

**Relationships**:
- `session`: Each message belongs to one session
- One session can have many messages (`related_name='messages'`)

**Role Types**:
- `user`: Candidate's message
- `assistant`: AI interviewer's response
- `system`: System notifications (e.g., "Interview started")

#### **Views** (`interviews/views.py`)

##### **interview_list_view** (Lines 9-13)
```python
@login_required
def interview_list_view(request):
    sessions = InterviewSession.objects.filter(user=request.user)
    return render(request, 'interviews/list.html', {'sessions': sessions})
```

- Only shows current user's sessions (privacy)
- `request.user` is automatically available (set by authentication middleware)

##### **interview_detail_view** (Lines 23-27)
```python
@login_required
def interview_detail_view(request, session_id):
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    return render(request, 'interviews/detail.html', {'session': session})
```

- Ensures user can only view their own sessions (`user=request.user`)
- Prevents unauthorized access

##### **interview_start_view** (Lines 16-20)
```python
@login_required
def interview_start_view(request):
    return render(request, 'interviews/start.html')
```

- Placeholder for starting new interviews (Phase 2 implementation)

#### **WebSocket Consumer** (`interviews/consumers.py`)

```python
class InterviewConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f'interview_{self.session_id}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
```

**Purpose**: Handles real-time WebSocket communication for interview chat

**Methods Explained**:

1. **connect()**: Called when WebSocket connection is established
   - Extracts `session_id` from URL
   - Creates a "room group" for this session
   - Adds this connection to the group
   - Accepts the connection

2. **disconnect()**: Called when connection closes
   - Removes connection from room group

3. **receive()**: Called when client sends a message
   ```python
   async def receive(self, text_data):
       text_data_json = json.loads(text_data)
       message = text_data_json['message']
       
       await self.save_message(message)  # Save to database
       
       await self.channel_layer.group_send(
           self.room_group_name,
           {'type': 'chat_message', 'message': message}
       )
   ```
   - Parses JSON message from client
   - Saves to database
   - Broadcasts to all connections in the room group

4. **chat_message()**: Receives message from group
   - Sends message back to WebSocket client
   - This is called for all connections in the group

5. **save_message()**: Database operation
   ```python
   @database_sync_to_async
   def save_message(self, message_content):
       session = InterviewSession.objects.get(id=self.session_id)
       Message.objects.create(
           session=session,
           role='user',
           content=message_content
       )
   ```
   - `@database_sync_to_async`: Converts synchronous database call to async
   - Creates Message record in database

**How WebSockets Work**:
1. Client connects: `ws://localhost:8000/ws/interview/123/`
2. Consumer creates group: `interview_123`
3. User sends message → saved to database → broadcast to group
4. All connected clients (including AI) receive the message
5. AI processes and responds through same WebSocket

---

### 4. Analysis App (`analysis/`)
**Purpose**: Performance evaluation and scoring

#### **Models** (`analysis/models.py`)

##### **Recording** (Lines 8-34)
```python
class Recording(models.Model):
    session = models.ForeignKey('interviews.InterviewSession', on_delete=models.CASCADE)
    file = models.FileField(upload_to='recordings/%Y/%m/%d/')
    file_type = models.CharField(max_length=10, choices=[('video', 'Video'), ('audio', 'Audio')])
    transcription = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

**Purpose**: Stores video/audio recordings from interview sessions

**Fields**:
- `file`: FileField stores actual video/audio file
- `upload_to`: Organizes files by date (`recordings/2024/12/02/file.mp4`)
- `transcription`: Text transcription (from AssemblyAI or similar)

##### **Evaluation** (Lines 36-74)
```python
class Evaluation(models.Model):
    session = models.OneToOneField('interviews.InterviewSession', on_delete=models.CASCADE)
    
    # Content quality scores (0-100)
    structure_score = models.IntegerField(default=0)
    hypothesis_score = models.IntegerField(default=0)
    math_score = models.IntegerField(default=0)
    insight_score = models.IntegerField(default=0)
    
    # Communication scores (0-100)
    body_language_score = models.IntegerField(default=0)
    speech_pacing_score = models.IntegerField(default=0)
    presence_score = models.IntegerField(default=0)
    delivery_clarity_score = models.IntegerField(default=0)
    
    # Overall score
    overall_score = models.IntegerField(default=0)
    
    # Detailed analysis
    content_analysis = models.JSONField(default=dict)
    communication_analysis = models.JSONField(default=dict)
```

**Purpose**: Stores detailed performance evaluation results

**Relationship**:
- `OneToOneField`: One evaluation per session (enforced at database level)

**Scoring Dimensions**:
- **Content**: Structure, hypothesis, math accuracy, insights
- **Communication**: Body language, pacing, presence, clarity

**JSON Fields**:
- Store detailed analysis without rigid structure
- Example: `content_analysis: {"strengths": [...], "weaknesses": [...]}`

---

### 5. Feedback App (`feedback/`)
**Purpose**: Coaching feedback and recommendations

#### **Models** (`feedback/models.py`)

```python
class Feedback(models.Model):
    evaluation = models.OneToOneField('analysis.Evaluation', on_delete=models.CASCADE)
    summary = models.TextField(help_text='Overall feedback summary')
    strengths = models.JSONField(default=list)
    areas_for_improvement = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
```

**Purpose**: Provides actionable coaching feedback based on evaluation

**Relationship**:
- `OneToOneField` with Evaluation (one feedback per evaluation)

**Structure**:
- `summary`: Overall written feedback
- `strengths`: List of positive points
- `areas_for_improvement`: List of weaknesses
- `recommendations`: Specific drills/practice suggestions

---

### 6. Agents App (`agents/`)
**Purpose**: Multi-agent AI workflow system (Phase 2)

**Current Status**: Placeholder for future implementation

**Planned Agents**:
- **Case Generator**: Generate realistic case scenarios
- **Interviewer**: Conduct the interview with adaptive questions
- **Evaluator**: Analyze content quality
- **Coach**: Generate personalized feedback

---

## Database Models

### Model Relationships Diagram

```
User (accounts.User)
  ├── One-to-Many → InterviewSession
  └── One-to-Many → Case (generated_by)

Case
  └── One-to-Many → InterviewSession

InterviewSession
  ├── One-to-Many → Message
  ├── One-to-One → Evaluation
  └── One-to-Many → Recording

Evaluation
  └── One-to-One → Feedback
```

### Key Relationships Explained

1. **User → InterviewSession**: One user can have many interview sessions
2. **Case → InterviewSession**: One case can be used in many sessions
3. **InterviewSession → Message**: One session has many chat messages
4. **InterviewSession → Evaluation**: One session has one evaluation (OneToOne)
5. **Evaluation → Feedback**: One evaluation has one feedback (OneToOne)

### Database Tables Created

When migrations run, Django creates these tables:

- `users` - User accounts
- `cases` - Case scenarios
- `interview_sessions` - Interview sessions
- `messages` - Chat messages
- `recordings` - Video/audio files
- `evaluations` - Performance scores
- `feedback` - Coaching recommendations

Plus Django's built-in tables:
- `auth_permission`, `auth_group` - Permissions
- `django_session` - Session storage
- `django_migrations` - Migration history
- etc.

---

## Views & URL Routing

### Request Flow Example

1. **User visits** `/cases/1/`
2. **Django checks** `case_interview_simulator/urls.py`
   - Matches `path('cases/', include('cases.urls'))`
3. **Django checks** `cases/urls.py`
   - Matches `path('<int:case_id>/', views.case_detail_view)`
   - Extracts `case_id=1`
4. **Django calls** `case_detail_view(request, case_id=1)`
5. **View executes**:
   - Fetches Case from database
   - Renders template with case data
6. **Response sent** to browser

### URL Patterns

```
Root URLs (case_interview_simulator/urls.py):
├── / → accounts.urls
├── /admin/ → Django admin
├── /interviews/ → interviews.urls
└── /cases/ → cases.urls

Accounts URLs:
├── / → dashboard
├── /signup/ → registration
├── /login/ → login
└── /logout/ → logout

Interviews URLs:
├── /interviews/ → list
├── /interviews/start/ → start new
└── /interviews/<id>/ → detail

Cases URLs:
├── /cases/ → list
└── /cases/<id>/ → detail
```

---

## WebSocket & Real-time Communication

### How WebSockets Work in This Project

1. **Connection**: Client JavaScript connects to `ws://localhost:8000/ws/interview/123/`
2. **Routing**: ASGI routes to `InterviewConsumer`
3. **Group**: Consumer adds connection to `interview_123` group
4. **Messaging**: 
   - User sends message → saved to DB → broadcast to group
   - AI processes message → sends response → broadcast to group
   - All connected clients receive updates

### WebSocket vs HTTP

| HTTP | WebSocket |
|------|-----------|
| Request-response | Persistent connection |
| Stateless | Stateful |
| Client initiates | Bidirectional |
| Good for pages | Good for chat |

### Channel Layers

**Purpose**: Allows multiple servers/processes to communicate

- **Redis (Production)**: Shared across all server instances
- **In-Memory (Local)**: Single process only

When a message is sent:
1. Saved to database
2. Sent to channel layer (Redis)
3. Channel layer broadcasts to all connections in group
4. Each consumer receives and forwards to client

---

## Deployment Configuration

### 1. `Procfile`
**Purpose**: Defines processes for Railway deployment

```
web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn case_interview_simulator.wsgi:application --bind 0.0.0.0:$PORT
worker: python manage.py runworker
```

**Processes**:
- **web**: Main HTTP server
  - Runs migrations
  - Collects static files
  - Starts Gunicorn server
- **worker**: Background worker for Channels (WebSocket support)

### 2. `railway.json`
**Purpose**: Railway-specific deployment configuration

```json
{
  "deploy": {
    "startCommand": "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn case_interview_simulator.wsgi:application --bind 0.0.0.0:$PORT"
  }
}
```

Defines the command Railway runs on deployment.

### 3. `runtime.txt`
**Purpose**: Specifies Python version

```
python-3.11.6
```

Railway uses this to select the Python runtime.

### 4. `requirements.txt`
**Purpose**: Python package dependencies

**Key Packages**:
- `Django>=4.2,<5.0` - Web framework
- `channels>=4.0.0` - WebSocket support
- `channels-redis>=4.1.0` - Redis channel layer
- `psycopg2-binary>=2.9.0` - PostgreSQL adapter
- `whitenoise>=6.6.0` - Static file serving
- `gunicorn>=21.2.0` - Production WSGI server
- `openai>=1.0.0`, `anthropic>=0.7.0` - AI APIs (Phase 2)

### Deployment Flow on Railway

1. **Push to Git** → Railway detects changes
2. **Build**: Installs dependencies from `requirements.txt`
3. **Deploy**: Runs commands from `Procfile` or `railway.json`
   - Migrations run automatically
   - Static files collected
   - Server starts
4. **Runtime**: 
   - Reads `DATABASE_URL` from Railway's PostgreSQL service
   - Reads `REDIS_URL` from Railway's Redis service
   - Serves application on Railway's domain

---

## Dependencies & Requirements

### Core Django Packages

- **Django 4.2+**: Web framework
- **psycopg2-binary**: PostgreSQL database adapter
- **python-dotenv**: Loads `.env` files
- **django-environ**: Environment variable management

### Real-time Communication

- **channels**: WebSocket support for Django
- **channels-redis**: Redis backend for channel layers

### Deployment

- **gunicorn**: Production WSGI server
- **whitenoise**: Serves static files in production

### Development Tools

- **pytest**: Testing framework
- **black**: Code formatter
- **flake8**: Linter
- **mypy**: Type checking

### AI Integration (Phase 2)

- **openai**: OpenAI API client
- **anthropic**: Anthropic (Claude) API client

---

## Custom Template Filters

### `case_interview_simulator/templatetags/custom_filters.py`

```python
@register.filter
def pprint(value):
    """Pretty print JSON data."""
    if isinstance(value, (dict, list)):
        return json.dumps(value, indent=2)
    return str(value)
```

**Usage in Templates**:
```html
{{ case.context|pprint }}
```

Converts JSON fields to formatted, readable strings in templates.

---

## Security Features

### 1. CSRF Protection
- `CsrfViewMiddleware` validates CSRF tokens on POST requests
- Prevents cross-site request forgery attacks

### 2. Authentication
- `AuthenticationMiddleware` attaches user to request
- `@login_required` decorator protects views

### 3. SQL Injection Prevention
- Django ORM automatically escapes SQL queries
- Never write raw SQL queries

### 4. XSS Protection
- Template auto-escaping prevents script injection
- Security headers enabled in production

### 5. Password Security
- Passwords are hashed (never stored in plain text)
- Password validators enforce strength requirements

---

## Data Flow Examples

### Example 1: User Registration

1. User fills form at `/signup/`
2. POST request to `signup_view`
3. `UserRegistrationForm` validates data
4. `form.save()` creates User in database
5. User authenticated and logged in
6. Redirect to dashboard

### Example 2: Starting Interview

1. User clicks "Start Interview" at `/interviews/start/`
2. View creates `InterviewSession` record
3. Redirects to `/interviews/{session_id}/`
4. JavaScript connects WebSocket to `ws/interview/{session_id}/`
5. `InterviewConsumer` handles connection
6. User can chat in real-time

### Example 3: Sending Chat Message

1. User types message in browser
2. JavaScript sends via WebSocket
3. `InterviewConsumer.receive()` receives message
4. Message saved to `Message` table
5. Message broadcast to channel layer
6. All connected clients (including AI) receive message
7. AI processes and responds
8. Response saved and broadcast back

---

## Future Implementation (Phase 2+)

### Planned Features

1. **Case Generator Agent**
   - Uses LLM to generate realistic case scenarios
   - Stores in `Case` model

2. **Interviewer Agent**
   - Conducts interview with adaptive questions
   - Different behavior based on mode (interviewer-led vs candidate-led)

3. **Evaluator Agent**
   - Analyzes content quality from messages
   - Analyzes communication from video/audio
   - Creates `Evaluation` records

4. **Coach Agent**
   - Generates personalized feedback
   - Creates `Feedback` records with recommendations

5. **RAG Integration**
   - Vector database for case knowledge
   - Retrieval-augmented generation for better cases

---

## Common Django Concepts Explained

### 1. Models
- Python classes that represent database tables
- Define fields (columns) and relationships
- Django ORM converts to SQL automatically

### 2. Views
- Functions/classes that handle HTTP requests
- Return HTTP responses (HTML, JSON, redirects)

### 3. Templates
- HTML files with Django template syntax
- Can include variables, loops, conditionals

### 4. URLs
- Map URL patterns to views
- Can extract parameters from URLs

### 5. Migrations
- Track database schema changes
- Allow version control of database structure
- Run with `python manage.py migrate`

### 6. Middleware
- Functions that process requests/responses
- Run in order, wrapping views
- Examples: authentication, CSRF protection

---

## Summary

This codebase is a Django web application for practicing case interviews with AI. It uses:

- **Django** for web framework and ORM
- **Django Channels** for WebSocket real-time communication
- **PostgreSQL** for production database
- **Redis** for WebSocket channel layers
- **Modular app structure** for organization

The project is currently in Phase 1 (infrastructure), with core models, authentication, and WebSocket infrastructure in place. Future phases will add AI agents for case generation, interviewing, evaluation, and coaching.

---

*Last Updated: December 2024*

