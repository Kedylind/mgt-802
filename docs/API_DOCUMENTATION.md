# AI Case Interview Simulator - API Documentation

## Overview

This document describes the API endpoints, agent interfaces, and data structures used in the AI Case Interview Simulator.

## Architecture

The system uses a multi-agent architecture with the following components:

1. **CaseGenerator**: Generates interview cases using RAG
2. **InterviewerAgent**: Conducts interviews with adaptive questioning
3. **EvaluatorAgent**: Evaluates candidate performance
4. **CoachAgent**: Generates personalized feedback

## Django Models

### InterviewSession

Represents an interview session.

**Fields:**
- `user`: ForeignKey to User
- `case`: ForeignKey to Case (nullable)
- `mode`: CharField (interviewer_led, candidate_led)
- `status`: CharField (not_started, in_progress, completed, abandoned)
- `started_at`: DateTimeField (nullable)
- `completed_at`: DateTimeField (nullable)
- `created_at`: DateTimeField (auto)
- `updated_at`: DateTimeField (auto)

### Message

Chat messages in an interview session.

**Fields:**
- `session`: ForeignKey to InterviewSession
- `role`: CharField (user, assistant, system)
- `content`: TextField
- `created_at`: DateTimeField (auto)

### Case

Generated case data.

**Fields:**
- `title`: CharField
- `case_type`: CharField (consulting, product_management)
- `prompt`: TextField
- `context`: JSONField
- `exhibits`: JSONField
- `created_at`: DateTimeField (auto)

### Recording

Video/audio recording from an interview session.

**Fields:**
- `session`: ForeignKey to InterviewSession
- `file`: FileField
- `file_type`: CharField (video, audio)
- `transcription`: TextField (nullable)
- `created_at`: DateTimeField (auto)

### Evaluation

Performance evaluation results.

**Fields:**
- `session`: OneToOneField to InterviewSession
- `structure_score`: IntegerField (0-100)
- `hypothesis_score`: IntegerField (0-100)
- `math_score`: IntegerField (0-100)
- `insight_score`: IntegerField (0-100)
- `body_language_score`: IntegerField (0-100)
- `speech_pacing_score`: IntegerField (0-100)
- `presence_score`: IntegerField (0-100)
- `delivery_clarity_score`: IntegerField (0-100)
- `overall_score`: IntegerField (0-100)
- `content_analysis`: JSONField
- `communication_analysis`: JSONField
- `created_at`: DateTimeField (auto)
- `updated_at`: DateTimeField (auto)

### Feedback

Coaching feedback linked to an evaluation.

**Fields:**
- `evaluation`: OneToOneField to Evaluation
- `summary`: TextField
- `strengths`: JSONField
- `areas_for_improvement`: JSONField
- `recommendations`: JSONField
- `created_at`: DateTimeField (auto)

## HTTP Endpoints

### Authentication

All endpoints require authentication unless specified.

### Interview Endpoints

#### List Interviews
```
GET /interviews/
```
Returns a list of all interview sessions for the authenticated user.

#### Start Interview
```
GET /interviews/start/
POST /interviews/start/
```
- GET: Shows interview start form
- POST: Creates a new interview session
  - Body: `case_id`, `mode`

#### Interview Detail
```
GET /interviews/<session_id>/
```
Returns the interview detail page with chat interface.

#### Evaluate Interview
```
POST /interviews/<session_id>/evaluate/
```
Triggers evaluation and feedback generation for a completed interview.

#### View Feedback
```
GET /interviews/<session_id>/feedback/
```
Displays evaluation results and coaching feedback.

#### Upload Recording
```
POST /interviews/<session_id>/upload-recording/
```
Uploads a video/audio recording file.
- Body: `recording` (file), `session_id`
- Returns: JSON with `success`, `recording_id`, `message`

### Case Endpoints

#### List Cases
```
GET /cases/
```
Returns a list of all available cases.

#### Generate Case
```
GET /cases/generate/
POST /cases/generate/
```
- GET: Shows case generation form
- POST: Generates a new case
  - Body: `topic`, `case_type`

#### Case Detail
```
GET /cases/<case_id>/
```
Returns details of a specific case.

## WebSocket Endpoints

### Interview Chat
```
WS /ws/interview/<session_id>/
```
Real-time chat interface for interviews.

**Message Format:**
```json
{
  "message": "Candidate response text"
}
```

**Response Format:**
```json
{
  "message": "Interviewer response text",
  "role": "assistant"
}
```

## Agent Interfaces

### CaseGenerator

**Class:** `agents.case_generator.CaseGenerator`

**Methods:**

#### `generate_case(topic: str, case_type: str = "consulting") -> Dict[str, Any]`

Generates a case interview scenario using RAG.

**Parameters:**
- `topic`: The industry or topic (e.g., "Airline Profitability")
- `case_type`: "consulting" or "product_management"

**Returns:**
```python
{
    "title": str,
    "case_type": str,
    "prompt": str,
    "context": {
        "client": str,
        "situation": str,
        "objective": str
    },
    "exhibits": [
        {
            "title": str,
            "type": str,  # "table" or "chart"
            "data": dict or str
        }
    ]
}
```

### InterviewerAgent

**Class:** `agents.interviewer.InterviewerAgent`

**Methods:**

#### `__init__(case_data: Dict[str, Any], interview_mode: str) -> None`

Initialize the interviewer with a case and mode.

**Parameters:**
- `case_data`: The generated case dictionary
- `interview_mode`: "interviewer_led" or "candidate_led"

#### `get_opening_message() -> str`

Returns the opening message for the interview.

#### `process_candidate_message(message: str) -> str`

Processes a candidate message and generates an interviewer response.

**Parameters:**
- `message`: The candidate's message text

**Returns:** Interviewer response string

### EvaluatorAgent

**Class:** `agents.evaluator.EvaluatorAgent`

**Methods:**

#### `evaluate_interview(case_data: Dict[str, Any], conversation_history: List[Dict[str, str]]) -> Dict[str, Any]`

Evaluates candidate performance.

**Parameters:**
- `case_data`: The case that was used
- `conversation_history`: List of messages with "role" and "content"

**Returns:**
```python
{
    "structure_score": int,  # 0-100
    "hypothesis_score": int,  # 0-100
    "math_score": int,  # 0-100
    "insights_score": int,  # 0-100
    "overall_score": int,  # 0-100
    "detailed_analysis": str,
    "strengths": List[str],
    "areas_for_improvement": List[str]
}
```

### CoachAgent

**Class:** `agents.coach.CoachAgent`

**Methods:**

#### `generate_feedback(evaluation_data: Dict[str, Any], case_data: Dict[str, Any]) -> Dict[str, Any]`

Generates personalized coaching feedback.

**Parameters:**
- `evaluation_data`: Results from EvaluatorAgent
- `case_data`: The case that was used

**Returns:**
```python
{
    "summary": str,
    "strengths": List[str],
    "areas_for_improvement": List[str],
    "recommendations": List[str],
    "next_steps": List[str],
    "full_feedback": str
}
```

## Transcription Service

### `transcribe_recording_async(recording_id: int) -> None`

Transcribes a recording using OpenAI Whisper API.

**Parameters:**
- `recording_id`: The ID of the Recording model instance

**Process:**
1. Retrieves the Recording instance
2. Opens the file
3. Calls OpenAI Whisper API
4. Saves transcription to `recording.transcription`

**Note:** This function runs asynchronously in a background thread. In production, use Celery for better task management.

## Environment Variables

Required environment variables:

- `SECRET_KEY`: Django secret key
- `DEBUG`: Boolean (True/False)
- `DATABASE_URL`: PostgreSQL connection string (for production)
- `OPENAI_API_KEY`: OpenAI API key
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `REDIS_URL`: Redis connection URL (for WebSocket support)

Optional:
- `ANTHROPIC_API_KEY`: Anthropic API key (for alternative models)
- `ASSEMBLYAI_API_KEY`: AssemblyAI key (alternative transcription)
- `PINECONE_API_KEY`: Pinecone API key (for vector database)
- `PINECONE_ENVIRONMENT`: Pinecone environment
- `PINECONE_INDEX_NAME`: Pinecone index name

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200`: Success
- `302`: Redirect
- `400`: Bad Request
- `401`: Unauthorized
- `404`: Not Found
- `500`: Internal Server Error

Error responses include JSON with error details:
```json
{
    "error": "Error message description"
}
```

## Rate Limiting

API rate limiting is recommended for production:
- Case generation: 10 requests/hour per user
- Interview evaluation: 5 requests/hour per user
- Recording upload: 20 requests/hour per user

## Security

- All endpoints require CSRF protection
- File uploads are validated for type and size
- User data is isolated by authentication
- API keys are stored in environment variables
- Input sanitization prevents prompt injection attacks

