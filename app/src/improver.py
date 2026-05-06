from src.executor import Executor

SYSTEM_PROMPT = """Você é um especialista em prompt engineering.
    Seu trabalho é melhorar o prompt original com base nos seguintes critérios de avaliação.
    """
class Improver:

    def __init__(self, api_key: str = None, provider: str = "anthropic"):
        self.system_prompt = SYSTEM_PROMPT
        self.model = "claude-sonnet-4-6"
        self.api_key = api_key
        self.provider = provider

    def get_feedback(
            self, 
            use_json: dict
            ) -> tuple[list[str], list[str], str, int]:
        """
        recebe o json de avaliacao e retorna lista de feedbacks e lista de problemas identificados
        """
        feedbacks = []
        problems = []
        
        user_prompt = use_json["user_prompt"]
        justification = use_json["evaluation"]["justification"]
        score = use_json["evaluation"]["score"]
        
        for criterio, resultado in use_json["evaluation"]["criteria"].items():
            atende = resultado["atende"]
            motivo = resultado["motivo"]
            if atende:
                feedbacks.append(f"- {criterio}: Atende - {motivo}")
            else:
                problems.append(f"- {criterio}: Não atende - {motivo}")

        return user_prompt, feedbacks, problems, justification, score


    def build_improvement_prompt(
            self,
            feedbacks,
            problems,
            justification,        
            score,
            original_prompt,
            system_prompt = SYSTEM_PROMPT
            ) -> str:

            return f"""
            {system_prompt} \n\n 

            Um agente foi avaliado e teve BAIXA qualidade nas respostas.\n\n

            System prompt atual: {original_prompt} \n\n
            
            Justificativa da avaliação: {justification} \n\n
            
            Nota da avaliação: {score} \n\n

            Problemas identificados nas avaliações:\n
            {"\n".join(feedbacks)}

            Critérios específicos que o agente NÃO atendeu:\n
            {"\n".join(problems)}

            Com base nesses problemas, escreva um NOVO system prompt melhorado para o agente.\n
            O prompt deve corrigir diretamente cada problema identificado.\n\n

            Escreva APENAS o novo system prompt, sem comentários adicionais.\n
            """

    def improve_prompt(
            self,
            use_json: dict,
            system_prompt = SYSTEM_PROMPT
    ):
        
        """"
        recebe o prompt original, os critérios de avaliação e a avaliação do prompt original, e retorna um prompt melhorado com base nessas informações.
        - user_prompt: o prompt do usuário a ser melhorado.
        - criteria: uma lista de critérios de avaliação que foram usados para avaliar o prompt original.
        - evaluation: um dicionário contendo a avaliação do prompt original, onde as chaves são os critérios de avaliação e os valores são as avaliações correspondentes.
        """

        # 1. Identificar todos os problemas a partir da avaliação
        user_prompt, feedbacks, problems, justification, score = self.get_feedback(use_json)

        # 2. Construir um prompt de melhoria com base nos problemas identificados
        instruction_prompt  = self.build_improvement_prompt(
             feedbacks, 
             problems, 
             justification, 
             score, 
             user_prompt, 
             system_prompt
             )

        # 3. Chamar o LLM para gerar o novo system prompt
        executor = Executor(self.api_key, provider=self.provider)
        messages = []
        executor.add_user_message(messages, instruction_prompt)

        response = executor.execute_prompt(
            messages,
            system_prompt=self.system_prompt,
            model=self.model
        )

        improved_system_prompt = response.content[0].text.strip()
        use_json["improved_prompt"] = improved_system_prompt
        
        return use_json




