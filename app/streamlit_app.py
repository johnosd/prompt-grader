import streamlit as st
from src.grader import Grader

st.title("🎯 Prompt Grader")

# --- INPUTS ---

api_key = st.text_input(
    "🔑 Sua Anthropic API Key",
    type="password",
    placeholder="sk-ant-...",
    help="Sua chave é usada apenas nesta sessão para chamar a API do Claude. Ela nunca é salva, logada ou compartilhada. O código é open source — você pode auditar em github.com/johncosta/prompt-grader. Prefere rodar localmente? Veja o README."
)

user_message = st.text_area(
    "User Message",
    placeholder="Ex: Gere meu treino semanal de musculação"
)

criterios_text = st.text_area(
    "Critérios de avaliação (um por linha)",
    placeholder="Respondeu com um plano semanal?\nCada exercício tem séries e repetições?"
)

max_iterations = st.slider("Máximo de iterações", min_value=1, max_value=5, value=3)

rodar = st.button("▶ Rodar Grader")

if rodar:
    if not api_key:
        st.error("Insira sua Anthropic API Key para continuar.")
        st.stop()
    criterios = [c.strip() for c in criterios_text.split("\n") if c.strip()]
    
    use_json = {
        "user_prompt": user_message,
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