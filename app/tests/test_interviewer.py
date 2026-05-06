import pytest
from src.interviewer import Interviewer

USER_PROMPT = "Gere meu treino semanal de musculação"

DEPTH_RANGES = {
    "minimal": (2, 3),
    "medium":  (1, 9),
    "maximum": (11, float("inf")),
}


@pytest.mark.parametrize("depth", ["minimal", "medium", "maximum"])
def test_interviewer(depth):
    interviewer = Interviewer()
    questions = interviewer.generate_questions(USER_PROMPT, depth=depth)

    print(f"\n--- {depth} ({len(questions)} perguntas) ---")
    for i, q in enumerate(questions, 1):
        print(f"  {i}. {q}")

    min_q, max_q = DEPTH_RANGES[depth]

    assert isinstance(questions, list), "Retorno deve ser uma lista"
    assert all(isinstance(q, str) for q in questions), "Cada pergunta deve ser uma string"
    assert min_q <= len(questions) <= max_q, (
        f"depth='{depth}': esperado entre {min_q} e {max_q} perguntas, "
        f"mas retornou {len(questions)}"
    )
