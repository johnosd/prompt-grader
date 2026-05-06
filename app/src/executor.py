import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """Você é um agente responsável por executar prompts de acordo com as instruções do usuário."""

BEDROCK_MODEL_MAP = {
    "claude-haiku-4-5-20251001": "anthropic.claude-haiku-4-5-20251001-v1:0",
    "claude-sonnet-4-6": "anthropic.claude-sonnet-4-6-20250919-v1:0",
    "claude-opus-4-7": "anthropic.claude-opus-4-7-20250514-v1:0",
}

class Executor:

    def __init__(
            self,
            api_key: str = None,
            provider: str = "anthropic",
            bedrock_api_key: str = None,
            aws_region: str = None,
    ):
        self.provider = provider
        if provider == "bedrock":
            if bedrock_api_key:
                os.environ["AWS_BEARER_TOKEN_BEDROCK"] = bedrock_api_key
            self.client = anthropic.AnthropicBedrock(aws_region=aws_region)
        else:
            self.client = anthropic.Anthropic(api_key=api_key)

    def add_user_message(self, messages, text):
        messages.append({"role": "user", "content": text})

    def add_assistant_message(self, messages, text):
        messages.append({"role": "assistant", "content": text})

    def execute_prompt(
            self,
            messages,
            system_prompt: str = None,
            model: str = "claude-haiku-4-5-20251001"
            ):

        if self.provider == "bedrock":
            model = BEDROCK_MODEL_MAP.get(model, model)

        params = {
            "model": model,
            "max_tokens": 8096,
            "messages": messages,
        }

        if system_prompt:
            params["system"] = system_prompt

        return self.client.messages.create(**params)
