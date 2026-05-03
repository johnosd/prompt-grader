from src.executor import Executor
from src.evaluator import Evaluator
from src.improver import Improver

SYSTEM_PROMPT = "Você é um assistente que responde perguntas de forma clara e objetiva sem perguntar"

class Grader:
    def __init__(self, api_key: str = None):
        self.system_prompt = SYSTEM_PROMPT
        self.model = "claude-sonnet-4-6"
        self.api_key = api_key

    def grader(
            self,
            use_json: dict,
            system_prompt: str = SYSTEM_PROMPT
    ) -> tuple:
        messages = []
        executor = Executor(api_key=self.api_key)
        executor.add_user_message(messages, use_json["user_prompt"])

        # 1. Executar o prompt
        response = executor.execute_prompt(
            messages,
            system_prompt=system_prompt,
            model=self.model
        )
        use_json["response"] = response.content[0].text.strip()

        # 2. Avaliar a resposta
        evaluator = Evaluator(api_key=self.api_key)
        use_json = evaluator.evaluate_response(use_json)

        # 3. Melhorar o system prompt
        improver = Improver(api_key=self.api_key)
        use_json = improver.improve_prompt(use_json)

        return use_json

    def run_grader(
            self,
            use_json: dict,
            threshold_score: int = 8,
            max_iterations: int = 2
    ) -> list:

        system_prompt = SYSTEM_PROMPT
        historico = []

        for iteration in range(1, max_iterations + 1):
            use_json = self.grader(use_json, system_prompt)

            score = use_json["evaluation"]["score"]

            historico.append({
                "iteracao": iteration,
                "system_prompt": system_prompt,
                "resposta": use_json["response"],
                "score": score,
                "system_prompt_melhorado": use_json.get("improved_prompt"),
                "evaluation": use_json.get("evaluation"),
                "resposta_melhorada": use_json.get("improved_response"),
            })

            if score >= threshold_score:
                break

            # system_prompt = use_json["improved_prompt"]
            use_json["user_prompt"] = use_json["improved_prompt"]

        return historico
