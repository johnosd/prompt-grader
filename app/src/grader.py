from src.executor import Executor
from src.evaluator import Evaluator
from src.improver import Improver

SYSTEM_PROMPT = "Você é um assistente que responde perguntas de forma clara e objetiva sem perguntar"

class Grader:
    def __init__(self, api_key: str = None, provider: str = "anthropic", aws_access_key: str = None, aws_secret_key: str = None, aws_region: str = None):
        self.system_prompt = SYSTEM_PROMPT
        self.model = "claude-sonnet-4-6"
        self.api_key = api_key
        self.provider = provider
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key
        self.aws_region = aws_region

    def grader(
            self,
            use_json: dict,
            system_prompt: str = SYSTEM_PROMPT
    ) -> tuple:
        messages = []
        executor = Executor(api_key=self.api_key, provider=self.provider, aws_access_key=self.aws_access_key, aws_secret_key=self.aws_secret_key, aws_region=self.aws_region)
        executor.add_user_message(messages, use_json["user_prompt"])

        # 1. Executar o prompt
        response = executor.execute_prompt(
            messages,
            system_prompt=system_prompt,
            model=self.model
        )
        use_json["response"] = response.content[0].text.strip()

        # 2. Avaliar a resposta
        evaluator = Evaluator(api_key=self.api_key, provider=self.provider, aws_access_key=self.aws_access_key, aws_secret_key=self.aws_secret_key, aws_region=self.aws_region)
        use_json = evaluator.evaluate_response(use_json)

        # 3. Melhorar o system prompt
        improver = Improver(api_key=self.api_key, provider=self.provider, aws_access_key=self.aws_access_key, aws_secret_key=self.aws_secret_key, aws_region=self.aws_region)
        use_json = improver.improve_prompt(use_json)

        return use_json

    def run_grader(
            self,
            use_json: dict,
            threshold_score: int = 8,
            max_iterations: int = 2
    ):
        system_prompt = SYSTEM_PROMPT

        for iteration in range(1, max_iterations + 1):
            use_json = self.grader(use_json, system_prompt)

            score = use_json["evaluation"]["score"]

            entry = {
                "iteracao": iteration,
                "system_prompt": system_prompt,
                "resposta": use_json["response"],
                "score": score,
                "system_prompt_melhorado": use_json.get("improved_prompt"),
                "evaluation": use_json.get("evaluation"),
                "resposta_melhorada": use_json.get("improved_response"),
            }

            yield entry

            if score >= threshold_score:
                break

            system_prompt = use_json["improved_prompt"]
