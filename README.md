# LLM Collab Study

Decoding Human-LLM Collaboration in Coding - A Transparency-Focused Analysis.

## Live Demo

Try it now: https://llm-collab-study-api.onrender.com

## Key Metrics

| Metric | Value |
|--------|-------|
| Sessions Analyzed | 15+ interaction sessions |
| Collaboration Patterns Found | 4 distinct patterns |
| Avg Fluency Score | 4.28 / 5 |
| Avg Correctness Score | 3.56 / 5 |
| Fluency-Correctness Correlation | -0.14 (NEGATIVE) |
| Over-Trust Cases | 6.7% |
| Debugging Turns | 5.8 avg (2x more than generation) |
| Refactoring Constraint Violations | 34% |

## Key Finding

Negative correlation between fluency and correctness means higher fluency does NOT mean higher correctness. Fluent AI outputs actively mislead user trust.

## 4 Collaboration Patterns

| Pattern | Percentage | Risk Level |
|---------|------------|------------|
| Linear Flow | 40.0% | Low |
| Iterative Refinement | 40.0% | Medium |
| Instruction Failure | 13.3% | High |
| Over-Trust | 6.7% | Critical |

## Research Questions

| ID | Question | Focus |
|----|----------|-------|
| RQ1 | What interaction patterns emerge in multi-turn coding tasks? | Pattern taxonomy |
| RQ2 | How do task types affect collaboration? | Task variation |
| RQ3 | What factors lead to instruction failure? | Failure analysis |
| RQ4 | How does output fluency influence user trust? | Trust calibration |

## Task Metrics

| Task Type | Avg Turns | Success Rate | Retry Rate |
|-----------|-----------|--------------|------------|
| Generation | 2.7 | 100% | 8.3% |
| Debugging | 5.8 | 40% | 25.0% |
| Refactoring | 3.8 | 75% | 20.0% |

## Architecture

React Frontend --> Flask API --> Groq LLM (Llama 3.3 70B) --> Pattern Classifier --> Research Analyzer --> JSON Storage

## Features

- Glass-Box Assistant: Shows model confidence and uncertainty
- Pattern Classification: 4-pattern detection algorithm
- Research Dashboard: Visual analytics and charts
- Trust Calibration: Fluency vs correctness analysis
- Session Explorer: Browse all interaction sessions
- CLI Tools: Log and analyze sessions from terminal

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, TailwindCSS 3.4 |
| Backend | Python 3.11, Flask 3.0 |
| LLM API | Groq (LLaMA 3.3-70B) |
| Analysis | Custom Python classifier |
| Deployment | Render.com |

## Glass-Box Transparency

Unlike black-box LLMs, our system reveals:
- Confidence score per response
- Uncertainty areas identified
- Constraints followed or violated

## Pattern Classification Algorithm

Priority 1: Instruction Failure (constraint violations detected)
Priority 2: Over-Trust (high fluency + low correctness)
Priority 3: Iterative Refinement (corrections made)
Priority 4: Linear Flow (ideal case, no issues)

## Quick Start

1. Clone: git clone https://github.com/santhosh123-vs/llm-collab-study
2. Install Python deps: pip install -r requirements.txt
3. Install Node deps: cd frontend && npm install
4. Add .env with GROQ_API_KEY
5. Run backend: python3 server.py
6. Run frontend: cd frontend && npm start
7. Open: http://localhost:3000



## Author

Kethavath Santhosh - github.com/santhosh123-vs
