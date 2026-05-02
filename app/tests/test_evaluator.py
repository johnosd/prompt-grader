import pytest
from src.evaluator import Evaluator
from src.executor import Executor
import json

#import use_cases from app/tests/use_cases.json
data_path = "app/tests/data/"

with open(data_path + "/use_cases.json", "r", encoding="utf-8") as f:
    use_cases = json.load(f)

@pytest.fixture(scope="module")
def setup_evaluation():

    executor = Executor()
    messages = []
    executor.add_user_message(messages, use_cases[0]["user_prompt"])
    response = executor.execute_prompt(
        messages,
        system_prompt="Você é um assistente que responde perguntas de forma clara e objetiva."
    )
    
    use_cases[0]["response"] = response.content[0].text.strip()

    return use_cases[0]


def test_evaluator(setup_evaluation):

    use_json = setup_evaluation

    evaluator = Evaluator()
    evaluation = evaluator.evaluate_response(use_json)

    print(json.dumps(evaluation, indent=2, ensure_ascii=False))

    return evaluation

def test_evaluator_write_output():

    evaluation = test_evaluator()
    
    with open(data_path + "/evaluation_output.json", "w", encoding="utf-8") as f:
        json.dump(evaluation, f, indent=2, ensure_ascii=False)