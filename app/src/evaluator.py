
import json

from src.executor import execute_prompt, add_user_message

def build_grader_prompt(user_message: str, agent_response: str, criteria: list[str]) -> str:
    criteria_text = "\n".join(f"- {c}" for c in criteria)
    return f"""
    Mensagem do cliente:
    {user_message}

    Resposta do agente:
    {agent_response}

    Critérios de avaliação:
    {criteria_text}

    Avalie cada critério individualmente e responda APENAS com JSON válido, sem texto adicional:
        {{
        "score": <número de 0 a 10>,
        "criteria": {{
            "criterio_1": {{"atende": true, "motivo": "..."}},
            "criterio_2": {{"atende": false, "motivo": "..."}},
            "criterio_3": {{"atende": true, "motivo": "..."}}
        }},
        "justification": "1-2 frases sobre o principal problema"
        }}
    """


def evaluate_response(user_prompt: str, response: str, criteria: list[str]) -> dict:
    messages = []
    prompt_grader = build_grader_prompt(user_prompt, response, criteria)
    add_user_message(messages, prompt_grader)

  
    system_prompt = """
        Você é um avaliador de qualidade de uma resposta gerada por um agente de IA.
        Sua tarefa é avaliar a resposta do agente com base em critérios específicos fornecidos
        pelo usuário.
        Retorne APENAS JSON válido. Não use markdown, não use blocos de código, não adicione texto antes ou depois do JSON.
    """


    evaluation = execute_prompt(messages, model="claude-sonnet-4-6", system_prompt=system_prompt)

    parse_evaluation = json.loads(evaluation)
    
    return {
        "prompt": user_prompt,
        "response": response,
        "evaluation": parse_evaluation
    }