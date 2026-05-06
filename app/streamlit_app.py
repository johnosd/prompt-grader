import streamlit as st
from src.grader import Grader
from src.interviewer import Interviewer
from src.context_builder import build_context

st.title("🎯 Prompt Grader")

# --- INPUTS ---

api_key = st.text_input(
    "🔑 Sua Anthropic API Key",
    type="password",
    placeholder="sk-ant-...",
    help="Sua chave é usada apenas nesta sessão para chamar a API do Claude. Ela nunca é salva, logada ou compartilhada."
)

user_message = st.text_area(
    "User Message",
    placeholder="Ex: Gere meu treino semanal de musculação"
)

criterios_text = st.text_area(
    "Critérios de avaliação (um por linha)",
    placeholder="Respondeu com um plano semanal?\nCada exercício tem séries e repetições?"
)

col1, col2 = st.columns(2)
with col1:
    depth = st.selectbox(
        "Nível de entrevista",
        options=["minimal", "medium", "maximum"],
        index=1
    )
with col2:
    max_iterations = st.slider("Máximo de iterações", min_value=1, max_value=5, value=3)

# --- STEP 1: GERAR PERGUNTAS ---

if st.button("💬 Gerar Perguntas"):
    if not api_key:
        st.error("Insira sua Anthropic API Key para continuar.")
        st.stop()
    if not user_message.strip():
        st.error("Digite um prompt antes de gerar perguntas.")
        st.stop()

    with st.spinner("Gerando perguntas..."):
        interviewer = Interviewer(api_key=api_key)
        st.session_state.questions = interviewer.generate_questions(user_message, depth=depth)

# --- STEP 2: RESPONDER PERGUNTAS ---

if st.session_state.get("questions"):
    st.subheader("Responda as perguntas abaixo")

    answers = []
    for i, question in enumerate(st.session_state.questions):
        answer = st.text_input(question, key=f"answer_{i}")
        answers.append((question, answer))

    # --- STEP 3: RODAR GRADER ---

    if st.button("▶ Rodar Grader"):
        if not api_key:
            st.error("Insira sua Anthropic API Key para continuar.")
            st.stop()

        criterios = [c.strip() for c in criterios_text.split("\n") if c.strip()]
        enriched_prompt = build_context(user_message, answers)

        use_json = {
            "user_prompt": enriched_prompt,
            "criteria": criterios
        }

        with st.spinner("Rodando Grader..."):
            grader = Grader(api_key=api_key)
            historico = grader.run_grader(use_json, max_iterations=max_iterations)

        st.success(f"Concluído em {len(historico)} iteração(ões)")

        for h in historico:
            score = h["score"]
            emoji = "✅" if score >= 8 else "⚠️"

            with st.expander(f"{emoji} Iteração {h['iteracao']} — Score: {score}/10"):
                tab1, tab2, tab3 = st.tabs(["System Prompt", "Resposta", "Avaliação"])

                with tab1:
                    st.code(h["system_prompt"], language="text")

                with tab2:
                    st.markdown(h["resposta"])

                with tab3:
                    st.json(h.get("evaluation", {}))
