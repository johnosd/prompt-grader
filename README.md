# Prompt Grader

An agentic pipeline that automatically improves an AI agent's system prompt through iterative evaluation cycles, until the responses meet a defined quality threshold.

## How it works

Each iteration runs three steps:

1. **Execute** — sends the user message to a Claude agent using the current system prompt
2. **Evaluate** — scores the response (0–10) against user-defined criteria
3. **Improve** — rewrites the system prompt based on the evaluation feedback

The loop repeats until the score reaches the threshold or the maximum number of iterations is hit.

```
user_message + system_prompt
        │
        ▼
  executor.py ──► model response
        │
        ▼
  evaluator.py ──► { score, criteria, justification }
        │
        ▼
  improver.py ──► improved_system_prompt
        │
        └──► repeat until score >= threshold or max_iterations reached
```

## Setup

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

Fill in the user message, one evaluation criterion per line, and the number of iterations. Click **Rodar Grader** to start.

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
│   ├── executor.py    # Claude API wrapper
│   ├── evaluator.py   # Scores a response against criteria
│   ├── improver.py    # Rewrites the system prompt from evaluation feedback
│   └── grader.py      # Orchestrates the loop
├── tests/
│   ├── data/
│   │   ├── use_cases.json          # Example inputs
│   │   └── evaluation_output.json  # Sample evaluator output for unit tests
│   ├── test_executor.py
│   ├── test_evaluator.py
│   ├── test_improver.py
│   └── test_grader.py
└── streamlit_app.py
```
