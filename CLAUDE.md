# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run a single test function
pytest app/tests/test_evaluator.py::test_evaluator
```

Tests run with `-v -s` by default (configured in `pytest.ini`), so `print()` output is visible.

## Architecture

This project is an **agentic prompt grader** that iteratively improves an AI agent's system prompt until its responses meet a quality threshold.

### Pipeline (orchestrated by `grader.py`)

```
user_message + system_prompt
        │
        ▼
  executor.py ──► model response
        │
        ▼
  evaluator.py ──► evaluation JSON { score, criteria, justification }
        │
        ▼
  improver.py ──► improved_system_prompt
        │
        └──► repeat until score >= threshold_score or max_iterations reached
```

### Modules

- **`executor.py`** — wraps the Claude API. `execute_prompt(messages, system_prompt, model)` sends a conversation and returns the text response. `add_user_message` / `add_assistant_message` build the messages list.
- **`evaluator.py`** — evaluates a model response against user-defined criteria. Returns a JSON dict with `evaluation.score` (0–10), per-criterion `atende`/`motivo`, and `justification`.
- **`improver.py`** — takes an evaluation JSON and the current system prompt, then returns an improved system prompt. `get_feedback()` extracts feedbacks (passing criteria) and problems (failing criteria) from the evaluation JSON. `improve_prompt(original_prompt, criteria, evaluation)` orchestrates the full improvement call.
- **`grader.py`** — orchestrates the loop. `run_grader(user_message, criteria, threshold_score, max_iterations)` runs iterations and returns a `historico` list with each iteration's system prompt, response, and score.

### Each module has its own fixed `SYSTEM_PROMPT` constant

- `executor.py` / `grader.py`: the agent's system prompt — **this is what gets improved** across iterations.
- `evaluator.py`: fixed evaluator instructions — never changes.
- `improver.py`: fixed prompt-engineering instructions — never changes.

### Test data

`app/tests/data/use_cases.json` — example user messages and criteria.  
`app/tests/data/evaluation_output.json` — sample evaluator output used in unit tests.

### Environment

Requires `ANTHROPIC_API_KEY` in a `.env` file at the project root.
