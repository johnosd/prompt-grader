import json
from src.evaluator import Evaluator
from src.executor import Executor
from src.improver import Improver
import pytest

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
    
    evaluator = Evaluator()
    return evaluator.evaluate_response(use_cases[0])


def test_get_feedback(setup_evaluation):
    use_json = setup_evaluation

    improver = Improver()
    user_prompt, feedbacks, problems, justification, score = improver.get_feedback(use_json)
    print("\n\n Feedbacks:------------------------------------------")
    for feedback in feedbacks:
        print(feedback) 
    
    print("\n\n Problems:-------------------------------------------")
    for problem in problems:
        print(problem)

def test_build_improvement_prompt(setup_evaluation):
    use_json = setup_evaluation
    improver = Improver()
    user_prompt, feedbacks, problems, justification, score = improver.get_feedback(use_json)
    prompt_improvement = improver.build_improvement_prompt(feedbacks, problems, justification, score, user_prompt)
    print("\n\n Prompt de melhoria:-------------------------------------------")
    print(prompt_improvement)

def test_improve_prompt(setup_evaluation):
    use_json = setup_evaluation
    improver = Improver()
    user_prompt, feedbacks, problems, justification, score = improver.get_feedback(use_json)
    prompt_improvement = improver.build_improvement_prompt(feedbacks, problems, justification, score, user_prompt)
    system_prompt = f"""Você é um especialista em prompt engineering.
    Seu trabalho é melhorar o prompt original com base nos seguintes critérios de avaliação
    """
    messages = []
    executor = Executor()
    executor.add_user_message(messages, prompt_improvement)
    improved_prompt = executor.execute_prompt(messages, system_prompt=system_prompt, model="claude-sonnet-4-6")
    print("\n\n Prompt melhorado:-------------------------------------------")
    print(improved_prompt.content[0].text.strip())

def test_executor_evaluator_improver(setup_evaluation):
    """
    Teste complento
    deve reusar o use_cases com o mesmo usar_message e criteria
    chamar o executor para gerar a resposta do modelo
    chamar o evaluator para gerar o feedback e os problemas
    chamar o improver para melhorar o prompt
    """
    use_json = setup_evaluation

    # imprimo o prompt do usuario e a resposta do modelo
    print("\n\n # PROMPT DO USUÁRIO:-------------------------------------------")
    print(json.dumps(use_json["user_prompt"], indent=2, ensure_ascii=False))

    print("\n\n # RESPOSTA DO MODELO:-------------------------------------------")
    print(json.dumps(use_json["response"], indent=2, ensure_ascii=False))

    # imprime avaliação, os feedbacks e os problemas
    print("\n\n # AVALIAÇÃO:-------------------------------------------")
    print(json.dumps(use_json["evaluation"], indent=2, ensure_ascii=False))

    # Chamar o improver para melhorar o prompt
    improver = Improver()
    user_prompt, feedbacks, problems, justification, score = improver.get_feedback(use_json)
    prompt_improvement = improver.build_improvement_prompt(feedbacks, problems, justification, score, user_prompt)
    system_prompt_improver = f"""Você é um especialista em prompt engineering.
    Seu trabalho é melhorar o prompt original com base nos seguintes critérios de avaliação
    """
    messages_improver = []
    executor = Executor()
    executor.add_user_message(messages_improver, prompt_improvement)
    improved_prompt = executor.execute_prompt(messages_improver, system_prompt=system_prompt_improver, model="claude-sonnet-4-6")
    
    print("\n\n # PROMPT MELHORADO:-------------------------------------------")
    print(improved_prompt.content[0].text.strip())

