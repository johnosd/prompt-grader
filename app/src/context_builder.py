def build_context(user_prompt: str, qa_pairs: list[tuple[str, str]]) -> str:
    if not qa_pairs:
        return user_prompt

    lines = [user_prompt, "", "Informações adicionais:"]
    for question, answer in qa_pairs:
        if answer.strip():
            lines.append(f"- {question} → {answer}")

    return "\n".join(lines)
