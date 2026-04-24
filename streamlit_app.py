import hashlib
from io import BytesIO

import streamlit as st
import instructor
from google import genai
from pydantic import BaseModel, Field
from typing import List, Optional
from pypdf import PdfReader
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO DA IA ---
# Certifique-se de configurar a variável de ambiente GEMINI_API_KEY no Streamlit Cloud
api_key = st.secrets.get("GEMINI_API_KEY")
client = instructor.from_genai(genai.Client(api_key=api_key))

# --- CLASSES DO SCHEMA (O Coração do Motor) ---
class Localidade(BaseModel):
    cidade: str
    uf: str
    bairro: Optional[str] = None
    cep: Optional[str] = None
    aderencia_geografica_estimada: str

class CBO(BaseModel):
    titulo: str
    codigo: str
    justificativa: str

class Formacao(BaseModel):
    instituicao: str
    curso: str
    status: str

class Skill(BaseModel):
    skill: str
    tipo: str
    nivel: str

class Idioma(BaseModel):
    idioma: str
    proficiencia: str

class SWOT(BaseModel):
    strengths: List[str]
    weaknesses: List[str]
    opportunities: List[str]
    threats: List[str]

class Curriculo(BaseModel):
    nome: str
    idade: Optional[int] = None
    pcd: bool
    senioridade: str
    tempo_total_carreira_meses: int
    localizacao: Localidade
    cbo_principal: CBO
    formacao: List[Formacao]
    idiomas_e_comunicacao: List[Idioma]
    matriz_skills: List[Skill]
    pitch_do_recrutador: str
    swot_do_candidato: SWOT
    linkedin: Optional[str] = None
    portfolio: List[str] = Field(default_factory=list)
    outros_links: List[str] = Field(default_factory=list)
    necessita_verificacao: List[str] = Field(default_factory=list)

# --- FUNÇÃO DE EXTRAÇÃO ---
def extrair_dados(texto):
    return client.chat.completions.create(
        model="gemini-2.5-flash-lite",
        response_model=Curriculo,
        messages=[
            {
                "role": "system",
                "content": "Você é um assistente especialista em recrutamento e análise de currículos. Extraia o currículo para o schema e aponte possíveis indícios de inconsistência."
            },
            {
                "role": "user",
                "content": (
                    f"Texto do currículo:\n{texto}\n\n"
                    "Extraia os dados conforme o schema vigente. "
                    "Inclua um campo 'necessita_verificacao' com trechos que merecem revisão humana. "
                    "Apontar experiências sem evidência, senioridade desproporcional, informações contraditórias ou vagas demais com pouco contexto."
                )
            }
        ],
    )

# --- UTILITÁRIOS DE LINK ---
MAX_CV_CHARACTERS = 20000
MAX_PDF_BYTES = 2 * 1024 * 1024  # 2MB, limite realista para CVs apenas de texto


def sanitize_url(url: str) -> str:
    if not url:
        return ""
    url = url.strip().strip('"').strip("'").strip(".,;:")
    if url.startswith("www."):
        url = "https://" + url
    if not url.lower().startswith("http://") and not url.lower().startswith("https://"):
        url = "https://" + url
    return url


def normalize_text(text: str) -> str:
    normalized = "\n".join(
        line.strip() for line in text.splitlines() if line.strip()
    )
    return normalized[:MAX_CV_CHARACTERS]


def compute_pdf_hash(raw_bytes: bytes) -> str:
    return hashlib.sha256(raw_bytes).hexdigest()


@st.cache_data(show_spinner=False)
def extrair_dados_cache(pdf_hash: str, texto: str) -> dict:
    response = client.chat.completions.create(
        model="gemini-2.5-flash-lite",
        response_model=Curriculo,
        messages=[
            {
                "role": "system",
                "content": "Você é um assistente especialista em recrutamento e análise de currículos. Extraia o currículo para o schema e aponte possíveis indícios de inconsistência."
            },
            {
                "role": "user",
                "content": (
                    f"Texto do currículo:\n{texto}\n\n"
                    "Extraia os dados conforme o schema vigente. "
                    "Inclua um campo 'necessita_verificacao' com trechos que merecem revisão humana. "
                    "Apontar experiências sem evidência, senioridade desproporcional, informações contraditórias ou vagas demais com pouco contexto."
                )
            }
        ],
    )
    return response.model_dump()


def extrair_dados(pdf_hash: str, texto: str) -> Curriculo:
    data = extrair_dados_cache(pdf_hash, texto)
    return Curriculo.model_validate(data)


def render_embedded_link(title: str, url: str):
    safe_url = sanitize_url(url)
    if not safe_url:
        return
    st.markdown(f"**{title}:** [{safe_url}]({safe_url})")
    st.markdown(
        f'<div style="margin: 1rem 0; border: 1px solid var(--border-color); border-radius: 12px; overflow:hidden;"><iframe src="{safe_url}" width="100%" height="450" frameborder="0"></iframe></div>',
        unsafe_allow_html=True,
    )
    if "linkedin.com" in safe_url.lower():
        st.markdown("<small>Se o LinkedIn não carregar no iframe, abra o link acima em uma nova aba.</small>", unsafe_allow_html=True)

# --- INTERFACE STREAMLIT ---
st.set_page_config(
    page_title="VagaJa - Motor de Inteligencia",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.title("VagaJa - Motor de Inteligencia")
st.markdown("Sistema de analise inteligente de curriculos")

# Upload section
st.header("Upload do Curriculo")
st.markdown("Selecione um arquivo PDF para analise.")
uploaded_file = st.file_uploader(
    "Arquivo PDF",
    type="pdf",
    help="Apenas arquivos PDF sao aceitos. Limite recomendado: 2MB.",
    label_visibility="collapsed"
)

if uploaded_file:
    if uploaded_file.size > MAX_PDF_BYTES:
        st.error(
            "Arquivo muito grande. Curriculos com mais de 2MB normalmente nao sao documentos de texto puros."
        )
    else:
        st.header("Processamento")
        if st.button("Processar Candidato"):
            with st.spinner("Analisando curriculo..."):
                raw_bytes = uploaded_file.read()
                pdf_hash = compute_pdf_hash(raw_bytes)
                reader = PdfReader(BytesIO(raw_bytes))
                raw_text = " ".join(
                    page.extract_text() or "" for page in reader.pages
                )
                texto = normalize_text(raw_text)

                if not texto:
                    st.error("Nao foi possivel extrair texto do PDF.")
                else:
                    candidato = extrair_dados(pdf_hash, texto)

                    st.success(f"Candidato {candidato.nome} processado com sucesso!")

                    # Informacoes principais
                    with st.expander("Informacoes Principais"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Nome:** {candidato.nome}")
                            if candidato.idade:
                                st.write(f"**Idade:** {candidato.idade} anos")
                            st.write(f"**PCD:** {'Sim' if candidato.pcd else 'Nao'}")
                        with col2:
                            st.write(f"**Senioridade:** {candidato.senioridade}")
                            st.write(f"**Tempo de Carreira:** {candidato.tempo_total_carreira_meses} meses")

                    # Localizacao
                    with st.expander("Localizacao"):
                        st.write(f"**Cidade:** {candidato.localizacao.cidade}")
                        st.write(f"**UF:** {candidato.localizacao.uf}")
                        if candidato.localizacao.bairro:
                            st.write(f"**Bairro:** {candidato.localizacao.bairro}")
                        if candidato.localizacao.cep:
                            st.write(f"**CEP:** {candidato.localizacao.cep}")
                        st.write(f"**Aderencia Geografica:** {candidato.localizacao.aderencia_geografica_estimada}")

                    # CBO
                    with st.expander("CBO Principal"):
                        st.write(f"**Titulo:** {candidato.cbo_principal.titulo}")
                        st.write(f"**Codigo:** {candidato.cbo_principal.codigo}")
                        st.write(f"**Justificativa:** {candidato.cbo_principal.justificativa}")

                    # Pitch do Recrutador
                    with st.expander("Pitch do Recrutador"):
                        st.write(candidato.pitch_do_recrutador)

                    # Matriz de Skills
                    with st.expander("Matriz de Skills"):
                        if candidato.matriz_skills:
                            skills_df = pd.DataFrame([
                                {"Skill": skill.skill, "Tipo": skill.tipo, "Nivel": skill.nivel}
                                for skill in candidato.matriz_skills
                            ])
                            st.dataframe(skills_df, use_container_width=True)

                            # Grafico de skills
                            fig_skills = px.bar(
                                skills_df,
                                x="Skill",
                                y="Nivel",
                                color="Tipo",
                                title="",
                                height=350
                            )
                            st.plotly_chart(fig_skills, use_container_width=True)
                        else:
                            st.write("Nenhuma skill identificada.")

                    # Formacao Academica
                    with st.expander("Formacao Academica"):
                        if candidato.formacao:
                            for formacao in candidato.formacao:
                                st.write(f"**Instituicao:** {formacao.instituicao}")
                                st.write(f"**Curso:** {formacao.curso}")
                                st.write(f"**Status:** {formacao.status}")
                                st.divider()
                        else:
                            st.write("Nenhuma formacao identificada.")

                    # Idiomas
                    with st.expander("Idiomas e Comunicacao"):
                        if candidato.idiomas_e_comunicacao:
                            idiomas_df = pd.DataFrame([
                                {"Idioma": idioma.idioma, "Proficiencia": idioma.proficiencia}
                                for idioma in candidato.idiomas_e_comunicacao
                            ])
                            st.dataframe(idiomas_df, use_container_width=True)

                            fig_idiomas = px.bar(
                                idiomas_df,
                                x="Idioma",
                                y="Proficiencia",
                                title="",
                                height=250
                            )
                            st.plotly_chart(fig_idiomas, use_container_width=True)
                        else:
                            st.write("Nenhum idioma identificado.")

                    # Links e Portfolio
                    if candidato.linkedin or candidato.portfolio or candidato.outros_links:
                        with st.expander("Links e Portfolio"):
                            if candidato.linkedin:
                                st.write(f"**LinkedIn:** {candidato.linkedin}")
                                st.components.v1.html(
                                    f'<iframe src="{sanitize_url(candidato.linkedin)}" width="100%" height="400" frameborder="0"></iframe>',
                                    height=400
                                )

                            if candidato.portfolio:
                                for i, link in enumerate(candidato.portfolio):
                                    st.write(f"**Portfolio {i+1}:** {link}")
                                    st.components.v1.html(
                                        f'<iframe src="{sanitize_url(link)}" width="100%" height="400" frameborder="0"></iframe>',
                                        height=400
                                    )

                            if candidato.outros_links:
                                for i, link in enumerate(candidato.outros_links):
                                    st.write(f"**Link {i+1}:** {link}")
                                    st.components.v1.html(
                                        f'<iframe src="{sanitize_url(link)}" width="100%" height="400" frameborder="0"></iframe>',
                                        height=400
                                    )

                    # Necessita verificacao
                    if candidato.necessita_verificacao:
                        with st.expander("Necessita Verificacao"):
                            st.write(f"Foram identificados {len(candidato.necessita_verificacao)} pontos que merecem revisao humana:")
                            for item in candidato.necessita_verificacao:
                                st.write(f"- {item}")
                    else:
                        with st.expander("Necessita Verificacao"):
                            st.write("Nenhum indicio claro de inconsistencia detectado automaticamente.")

                    # Analise SWOT
                    with st.expander("Analise SWOT"):
                        swot = candidato.swot_do_candidato
                        col1, col2 = st.columns(2)
                        with col1:
                            st.subheader("Strengths")
                            for strength in swot.strengths:
                                st.write(f"- {strength}")

                            st.subheader("Opportunities")
                            for opportunity in swot.opportunities:
                                st.write(f"- {opportunity}")

                        with col2:
                            st.subheader("Weaknesses")
                            for weakness in swot.weaknesses:
                                st.write(f"- {weakness}")

                            st.subheader("Threats")
                            for threat in swot.threats:
                                st.write(f"- {threat}")

                    # JSON Completo
                    with st.expander("Dados Completos (JSON)"):
                        st.json(candidato.model_dump_json())

st.markdown("---")
st.markdown("VagaJa - Motor de Inteligencia para Recrutamento | Powered by Gemini AI")
