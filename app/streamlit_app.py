import json
import streamlit as st
import streamlit.components.v1 as components
from src.grader import Grader
from src.interviewer import Interviewer
from src.context_builder import build_context


def copy_markdown_button(text: str) -> None:
    escaped = json.dumps(text)
    components.html(
        f"""
        <textarea id="copyArea" style="position:absolute;left:-9999px;"></textarea>
        <script>document.getElementById('copyArea').value = {escaped};</script>
        <button id="copyBtn" onclick="
            var el = document.getElementById('copyArea');
            el.select();
            el.setSelectionRange(0, 99999);
            document.execCommand('copy');
            this.textContent = '✅ Copiado!';
            this.style.background = '#28a745';
            setTimeout(function() {{
                document.getElementById('copyBtn').textContent = '📋 Copiar Markdown';
                document.getElementById('copyBtn').style.background = '#6c757d';
            }}, 2000);
        " style="background:#6c757d;color:white;border:none;padding:6px 14px;
                 border-radius:4px;cursor:pointer;font-size:14px;">
            📋 Copiar Markdown
        </button>
        """,
        height=45,
    )

st.title("🎯 Prompt Grader")

# --- INPUTS ---

provider = st.selectbox(
    "Provider",
    options=["anthropic", "bedrock"],
    format_func=lambda x: "Anthropic" if x == "anthropic" else "AWS Bedrock"
)

if provider == "anthropic":
    api_key = st.text_input(
        "🔑 Anthropic API Key",
        type="password",
        placeholder="sk-ant-...",
        help="Usada apenas nesta sessão. Nunca é salva ou compartilhada."
    )
    bedrock_api_key = aws_region = None
else:
    api_key = None
    col_b1, col_b2 = st.columns([3, 1])
    with col_b1:
        bedrock_api_key = st.text_input("🔑 Bedrock API Key", type="password")
    with col_b2:
        aws_region = st.text_input("Região", value="us-east-1")

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
    if provider == "anthropic" and not api_key:
        st.error("Insira sua Anthropic API Key para continuar.")
        st.stop()
    if provider == "bedrock" and not bedrock_api_key:
        st.error("Insira sua Bedrock API Key para continuar.")
        st.stop()
    if not user_message.strip():
        st.error("Digite um prompt antes de gerar perguntas.")
        st.stop()

    with st.spinner("Gerando perguntas..."):
        interviewer = Interviewer(api_key=api_key, provider=provider, bedrock_api_key=bedrock_api_key, aws_region=aws_region)
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
        if provider == "anthropic" and not api_key:
            st.error("Insira sua Anthropic API Key para continuar.")
            st.stop()
        if provider == "bedrock" and not bedrock_api_key:
            st.error("Insira sua Bedrock API Key para continuar.")
            st.stop()

        criterios = [c.strip() for c in criterios_text.split("\n") if c.strip()]
        enriched_prompt = build_context(user_message, answers)

        use_json = {
            "user_prompt": enriched_prompt,
            "criteria": criterios
        }

        grader = Grader(api_key=api_key, provider=provider, bedrock_api_key=bedrock_api_key, aws_region=aws_region)
        historico = []
        status = st.empty()
        status.info("⏳ Rodando iteração 1...")

        for entry in grader.run_grader(use_json, max_iterations=max_iterations):
            status.info(f"⏳ Rodando iteração {entry['iteracao'] + 1} de {max_iterations}...")
            historico.append(entry)
            score = entry["score"]
            emoji = "✅" if score >= 8 else "⚠️"

            with st.expander(f"{emoji} Iteração {entry['iteracao']} — Score: {score}/10", expanded=True):
                tab1, tab2, tab3 = st.tabs(["System Prompt", "Resposta", "Avaliação"])

                with tab1:
                    st.code(entry["system_prompt"], language="markdown")

                with tab2:
                    copy_markdown_button(entry["resposta"])
                    st.markdown(entry["resposta"])

                with tab3:
                    st.json(entry.get("evaluation", {}))

        status.empty()
        st.success(f"Concluído em {len(historico)} iteração(ões)")
