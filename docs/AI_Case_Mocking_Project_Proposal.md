# AI Case Interview Simulator - Project Proposal

## Team Members
David Schmidt, Francis Krauch, Yichen Max Li, Yiyi Shen

## Overview

A web-based AI Case Interview Simulator for MBA/Master's students to practice consulting and product management interviews. The tool supports both interviewer-led (McKinsey-style) and candidate-led (BCG/Bain/PM-style) formats. It can generate realistic cases, conduct a live, interactive mock interview, record and analyze the candidate's performance (content + communication style), and provide structured scores and coaching feedback.

## Key Features/Workflow

### 1. Mode Selection

- User chooses interview type: interviewer-led, candidate-led, or PM product case.

### 2. Live AI Interview

- AI presents prompt, clarifying details, exhibits.
- Adaptive follow-up questions based on chosen format.

### 3. Recording

- User records video and audio in-browser during the interview.
- Video is uploaded for analysis.

### 4. Answer and Behavior Analysis

- System transcribes and evaluates content quality (structure, hypothesis, math, insights).
- Vision/voice model analyzes communication style (movement, pacing, presence, delivery).

### 5. Feedback and Scoring

- Scorecards with multiple dimensions.
- Written coaching guidance and recommended drills.

## Technical Accomplishment

- Hosted Web App (React/Next.js + FastAPI)
- Conversational Chat Engine
- Multi-Agent Workflow (Case Generator, Interviewer, Evaluator, Coach)
- Search-Augmented Retrieval (RAG)
- Multiple Models + Multiple API Calls
- Prompt-Injection Safety (input filtering + controlled exhibit release)

## Code Quality

Modular structure, docstrings, type hints, unit tests, version control (GitHub).

## Timeline

- **Week 1**: Architecture + backend/frontend setup
- **Week 2**: Case generation + RAG
- **Week 3**: Evaluator + Coach agents, integration, UI polish, documentation, final demo

