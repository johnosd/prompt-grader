from src.evaluator import evaluate_response
from src.executor import execute_prompt, add_assistant_message, add_user_message
import json

use_cases = [
{
        "id": 1,
        "user_message": "Gere meu treino semanal de musculação",
        "criteria": [
            "Respondeu com um plano de treino semanal de musculação?",
            "Cada treino tem um nome do execicio, número de séries, número de repetições e tempo de descanso?",
            "cada execicio tem o kg recomendado para cada série?"
        ],
    }
]

def test_evaluator():
    messages = []
    criteria = use_cases[0]["criteria"]
    # 1 - Gerar resposta do agente 
    add_user_message(messages, use_cases[0]["user_message"])
    response = execute_prompt(messages, model="claude-haiku-4-5-20251001")

    # 2 - Avaliar resposta do agente
    evaluation = evaluate_response(use_cases[0]["user_message"], response, criteria)
    print(json.dumps(evaluation, indent=2, ensure_ascii=False))

