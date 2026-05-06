# Prompt Grader

An agentic pipeline that automatically improves a user prompt through iterative evaluation cycles, until the model's response meets a defined quality threshold.

## What is prompt evaluation?

Prompt evaluation (or **grading**) is the practice of automatically measuring how well a model response satisfies a set of criteria — and using that signal to improve the prompt that generated it.

Claude is well-suited for this because the same model that generates responses can also act as a judge: given a response and a rubric, it returns a structured score and diagnosis. Anthropic's documentation refers to this pattern as [using Claude to evaluate Claude outputs](https://docs.anthropic.com/en/docs/build-with-claude/evaluate-prompts), and it is a core building block for prompt engineering workflows, regression testing, and autonomous agents that self-improve.

This project applies that pattern in a loop: evaluate → diagnose → rewrite → repeat.

## How it works

### Context Interview

Before the grading loop starts, an optional **Interviewer** step enriches the user prompt by asking clarifying questions. The user answers them in the UI, and a **Context Builder** merges the original prompt with the answers into a single, richer input for the grader.

```
user_prompt + depth level
      │
      ▼
  Interviewer ── generates clarifying questions (minimal / medium / maximum)
      │
      ▼
  User answers questions
      │
      ▼
  Context Builder ── enriched_prompt
      │
      ▼
  Grading loop (below)
```

### Grading loop

The key design decision is that the **system prompt stays fixed** across iterations. What changes is the **user prompt** — the Improver rewrites it to be more explicit, structured, and constraint-rich so that the same agent produces better responses without modifying its core instructions.

```
enriched_prompt (evolves each iteration)
      │
      ▼
  Executor ── system_prompt (fixed)
      │
      ▼
  Evaluator ── score + diagnosis JSON
      │           { score, criteria: { atende, motivo }, justification }
      ▼
  Improver ── generates improved user_prompt
      │
      └──► repeat until score >= threshold or max_iterations reached
```

Each iteration:

1. **Execute** — sends the current `user_prompt` to a Claude agent with a fixed `system_prompt`; captures the text response
2. **Evaluate** — a second Claude call scores the response (0–10) against each user-defined criterion and returns a JSON diagnosis
3. **Improve** — a third Claude call reads the diagnosis and rewrites the `user_prompt` to directly address every failing criterion; the improved prompt becomes the input for the next iteration

## Live demo

[https://prompt-grader.streamlit.app/](https://prompt-grader.streamlit.app/)

Enter your Anthropic API key directly in the UI — no setup required.

## Setup (local)

**Requirements:** Python 3.10+, an Anthropic API key.

```bash
# Install dependencies
pip install -r requirements.txt

# Set your API key
echo "ANTHROPIC_API_KEY=your-key-here" > .env
```

## Usage

### Streamlit UI

```bash
streamlit run app/streamlit_app.py
```

1. Enter your prompt and evaluation criteria (one per line)
2. Choose the interview depth (`minimal` / `medium` / `maximum`) and click **Gerar Perguntas**
3. Answer the clarifying questions that appear
4. Click **Rodar Grader** — the grader runs with the enriched context

### Deploy on Streamlit Community Cloud

1. Fork or push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) and click **New app**.
3. Select the repository and set the main file path to `app/streamlit_app.py`.
4. Click **Deploy** — no secrets configuration needed, the app asks for the API key at runtime.

### Python API

```python
from src.grader import Grader

use_json = {
    "user_prompt": "Gere meu treino semanal de musculação",
    "criteria": [
        "Respondeu com um plano de treino semanal de musculação?",
        "Cada treino tem nome, séries, repetições e tempo de descanso?",
        "Cada exercício tem o kg recomendado?"
    ]
}

grader = Grader()
historico = grader.run_grader(use_json, threshold_score=8, max_iterations=3)

for h in historico:
    print(f"Iteration {h['iteracao']} — Score: {h['score']}/10")
    print(h["system_prompt_melhorado"])
```

`run_grader` returns a list of dicts, one per iteration, with:

| Key | Description |
|-----|-------------|
| `iteracao` | Iteration number |
| `system_prompt` | Prompt used in this iteration |
| `resposta` | Agent response |
| `score` | Evaluation score (0–10) |
| `evaluation` | Full evaluation JSON |
| `system_prompt_melhorado` | Improved prompt for the next iteration |

## Running tests

```bash
pytest
```

Tests run with `-v -s` by default (configured in `pytest.ini`), so `print()` output is visible.

## Project structure

```
app/
├── src/
│   ├── executor.py         # Claude API wrapper
│   ├── evaluator.py        # Scores a response against criteria
│   ├── improver.py         # Rewrites the prompt from evaluation feedback
│   ├── grader.py           # Orchestrates the grading loop
│   ├── interviewer.py      # Generates clarifying questions by depth level
│   └── context_builder.py  # Merges user prompt + interview answers
├── tests/
│   ├── data/
│   │   ├── use_cases.json          # Example inputs
│   │   └── evaluation_output.json  # Sample evaluator output for unit tests
│   ├── test_executor.py
│   ├── test_evaluator.py
│   ├── test_improver.py
│   ├── test_grader.py
│   └── test_interviewer.py
└── streamlit_app.py
```
