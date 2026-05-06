
import json

from src.executor import Executor

SYSTEM_PROMPT = """
        Você é um avaliador de qualidade de uma resposta gerada por um agente de IA.
        Sua tarefa é avaliar a resposta do agente com base em critérios específicos fornecidos
        pelo usuário.
        Retorne APENAS JSON válido. Não use markdown, não use blocos de código, não adicione texto antes ou depois do JSON.
    """
class Evaluator:
    def __init__(self, api_key: str = None, provider: str = "anthropic", bedrock_api_key: str = None, aws_region: str = None):
        self.system_prompt = SYSTEM_PROMPT
        self.model = "claude-sonnet-4-6"
        self.api_key = api_key
        self.provider = provider
        self.bedrock_api_key = bedrock_api_key
        self.aws_region = aws_region
        

    def build_evaluation_prompt(
            self,
            user_prompt: str, 
            agent_response: str, 
            criteria: list[str]
            ) -> str:
        
        criteria_text = "\n".join(f"- {c}" for c in criteria)
        
        return f"""
        Mensagem do cliente:
        {user_prompt}

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


    def evaluate_response(self, use_json) -> dict:

        user_prompt = use_json["user_prompt"]
        criteria = use_json["criteria"]
        agent_response = use_json["response"]
       
        prompt_evaluation = self.build_evaluation_prompt(
            user_prompt, 
            agent_response, 
            criteria
            )
        
        executor = Executor(self.api_key, provider=self.provider, bedrock_api_key=self.bedrock_api_key, aws_region=self.aws_region)
        messages = []
        executor.add_user_message(messages, prompt_evaluation)
        evaluation = executor.execute_prompt(
            messages,
            system_prompt=self.system_prompt,
            model=self.model
            )

        evaluation_text = evaluation.content[0].text.strip()

        use_json["evaluation_prompt"] = prompt_evaluation
        use_json["evaluation"] = json.loads(evaluation_text)
        
        return use_json