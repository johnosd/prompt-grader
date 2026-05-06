import json
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

SYSTEM_PROMPT = """Você é um agente reponsavel por executar prompts de acordo com as instruções do usuário."""

class Executor:

    def __init__(self, api_key: str = None):
        self.client = anthropic.Anthropic(api_key=api_key)


    def add_user_message(self, messages, text):
        user_message = {"role": "user", "content": text}
        messages.append(user_message)

    def add_assistant_message(self, messages, text):
        assistant_message = {"role": "assistant", "content": text}
        messages.append(assistant_message)

    def execute_prompt(
            self,
            messages,
            system_prompt: str=None,
            model: str = "claude-haiku-4-5-20251001"
            ) -> str:
        
        
        params = {
            "model": model,
            "max_tokens": 8096,
            "messages": messages,
        }

        if system_prompt:
            params["system"] = system_prompt

        # chamar a API do Claude e retorna apenas texto'
        response = self.client.messages.create(**params)
        return response
