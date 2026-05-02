import json
import copy
from src.grader import Grader

data_path = "app/tests/data/"

with open(data_path + "use_cases.json", "r", encoding="utf-8") as f:
    use_cases = json.load(f)

def test_run_grader():
    use_json = copy.deepcopy(use_cases[0])

    grader = Grader()
    historico = grader.run_grader(use_json, threshold_score=8, max_iterations=3)

    resultado = {
        "user_prompt": use_json["user_prompt"],
        "criteria": use_json["criteria"],
        "primeira_resposta": historico[0]["resposta"],
        "prompt_melhorado": historico[0]["system_prompt_melhorado"],
    }

    print(json.dumps(resultado, indent=2, ensure_ascii=False))

    assert isinstance(historico, list)
    assert 1 <= len(historico) <= 3

    for h in historico:
        assert "iteracao" in h
        assert "system_prompt" in h
        assert "resposta" in h
        assert "score" in h
        assert isinstance(h["score"], (int, float))
        assert 0 <= h["score"] <= 10
