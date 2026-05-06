import json
import re

from src.executor import Executor

SYSTEM_PROMPT = """Você é um especialista em elicitação de requisitos e entendimento de contexto.

Dado um prompt do usuário, analise o domínio ao qual ele pertence e gere perguntas de esclarecimento
relevantes para enriquecer a resposta final.

Regras por nível de profundidade:
- minimal: 2 a 3 perguntas, apenas o essencial para evitar ambiguidade crítica
- medium: < 10 perguntas, cobrindo contexto relevante e restrições importantes
- maximum: > 10 perguntas, entreviste o usuário e pergunte tudo que pode enriquecer e personalizar a resposta

Retorne APENAS JSON válido com uma lista de strings. Sem markdown, sem texto adicional.
Formato esperado:
["pergunta 1", "pergunta 2", "pergunta 3"]"""


class Interviewer:
    def __init__(self, api_key: str = None):
        self.system_prompt = SYSTEM_PROMPT
        self.model = "claude-haiku-4-5-20251001"
        self.api_key = api_key

    def generate_questions(self, user_prompt: str, depth: str = "medium") -> list[str]:
        if depth not in ("minimal", "medium", "maximum"):
            raise ValueError("depth deve ser 'minimal', 'medium' ou 'maximum'.")

        user_message = f"Nível de profundidade: {depth}\n\nPrompt do usuário:\n{user_prompt}"

        executor = Executor(self.api_key)
        messages = []
        executor.add_user_message(messages, user_message)

        response = executor.execute_prompt(
            messages,
            system_prompt=self.system_prompt,
            model=self.model,
        )

        response_text = response.content[0].text.strip()
        # strip markdown code block if model wraps the JSON (e.g. ```json ... ```)
        match = re.search(r"```(?:json)?\s*([\s\S]*?)```", response_text)
        if match:
            response_text = match.group(1).strip()
        return json.loads(response_text)
