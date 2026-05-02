import json

from src.executor import Executor

#import use_cases from app/tests/use_cases.json
data_path = "app/tests/data/"

messages = []

with open(data_path + "/use_cases.json", "r", encoding="utf-8") as f:
    use_cases = json.load(f)
    
def test_executor():
    user_prompt = use_cases[0]["user_prompt"]
    executor = Executor()
    executor.add_user_message(messages, user_prompt)

    result = executor.execute_prompt(messages)

    use_cases[0]["result"] = result.content[0].text.strip()
    # format json
    print(json.dumps(use_cases, indent=2, ensure_ascii=False))

