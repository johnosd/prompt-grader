from src.executor import execute_prompt, add_user_message, add_assistant_message

def test_executor():
    messages = []
    add_user_message(messages, "Gere um treino semanal de musculação")

    result = execute_prompt(messages)
    add_assistant_message(messages, result)
    print(result)
