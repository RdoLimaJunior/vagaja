import streamlit as st
import instructor
from google import genai
from pydantic import BaseModel, Field
from typing import List, Optional
from pypdf import PdfReader
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURAÇÃO DA IA ---
# Certifique-se de configurar a variável de ambiente GEMINI_API_KEY no Streamlit Cloud
api_key = st.secrets.get("GEMINI_API_KEY")
client = instructor.from_genai(genai.Client(api_key=api_key))

# --- CSS PERSONALIZADO PARA DESIGN CLARO E LEVE ---
st.markdown("""
<style>
    /* Reset e variáveis de cor - Tema Claro */
    :root {
        --primary-bg: #ffffff;
        --secondary-bg: #f8fafc;
        --accent-color: #2563eb;
        --accent-light: #dbeafe;
        --accent-hover: #1d4ed8;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --text-light: #94a3b8;
        --border-color: #e2e8f0;
        --shadow-light: 0 1px 3px rgba(0, 0, 0, 0.1);
        --shadow-medium: 0 4px 6px rgba(0, 0, 0, 0.07);
        --border-radius: 12px;
        --transition: all 0.2s ease;
    }

    /* Body e background - Fundo claro */
    .main {
        background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
        background-attachment: fixed;
        min-height: 100vh;
    }

    /* Container principal - Mais clean */
    .block-container {
        background: transparent !important;
        padding: 2rem 1rem;
        max-width: 1200px;
        margin: 0 auto;
    }

    /* Header - Design clean */
    .stApp header {
        background: transparent !important;
    }

    /* Títulos - Cores claras */
    h1, h2, h3 {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        margin-bottom: 1rem !important;
    }

    /* Cards limpos - Sem glassmorphism pesado */
    .glass-card {
        background: var(--primary-bg);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        box-shadow: var(--shadow-light);
        padding: 1.5rem;
        margin: 1rem 0;
        transition: var(--transition);
    }

    .glass-card:hover {
        box-shadow: var(--shadow-medium);
        transform: translateY(-1px);
    }

    /* Card CBO especial - Mais sutil */
    .cbo-card {
        background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
        border: 2px solid #0ea5e9;
        border-radius: var(--border-radius);
        box-shadow: 0 4px 12px rgba(14, 165, 233, 0.15);
        padding: 1.5rem;
        margin: 1rem 0;
        position: relative;
        overflow: hidden;
    }

    .cbo-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #0ea5e9, #0284c7);
    }

    /* Métricas - Design clean */
    .metric-card {
        background: var(--primary-bg);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        box-shadow: var(--shadow-light);
        transition: var(--transition);
    }

    .metric-card:hover {
        box-shadow: var(--shadow-medium);
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--accent-color);
        margin: 0.5rem 0;
    }

    .metric-label {
        font-size: 0.85rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 500;
    }

    /* Botões - Design moderno */
    .stButton button {
        background: var(--accent-color);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2);
        transition: var(--transition);
        text-transform: none;
        letter-spacing: 0.025em;
    }

    .stButton button:hover {
        background: var(--accent-hover);
        box-shadow: 0 4px 8px rgba(37, 99, 235, 0.3);
        transform: translateY(-1px);
    }

    /* File uploader - Clean */
    .uploadedFile {
        background: var(--secondary-bg);
        border: 2px dashed var(--border-color);
        border-radius: var(--border-radius);
        padding: 2rem;
        text-align: center;
        transition: var(--transition);
    }

    .uploadedFile:hover {
        border-color: var(--accent-color);
        background: #f1f5f9;
    }

    /* Progress bars */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--accent-color), var(--accent-hover));
        border-radius: 6px;
    }

    /* Expander - Clean */
    .streamlit-expanderHeader {
        background: var(--secondary-bg);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 1rem;
        font-weight: 500;
        color: var(--text-primary);
        transition: var(--transition);
    }

    .streamlit-expanderHeader:hover {
        background: var(--primary-bg);
    }

    /* Dataframe - Clean */
    .stDataFrame {
        background: var(--primary-bg);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        box-shadow: var(--shadow-light);
    }

    /* Success messages - Clean */
    .stSuccess {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: var(--border-radius);
        color: #166534;
        font-weight: 500;
    }

    /* Error messages - Clean */
    .stError {
        background: #fef2f2;
        border: 1px solid #fecaca;
        border-radius: var(--border-radius);
        color: #dc2626;
        font-weight: 500;
    }

    /* Info messages - Clean */
    .stInfo {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: var(--border-radius);
        color: var(--accent-color);
        font-weight: 500;
    }

    /* Skills chart container - Clean */
    .skills-container {
        background: var(--primary-bg);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: var(--shadow-light);
    }

    /* SWOT sections - Clean */
    .swot-section {
        background: var(--primary-bg);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: var(--transition);
    }

    .swot-section:hover {
        box-shadow: var(--shadow-light);
    }

    .swot-strengths { border-left: 3px solid #22c55e; }
    .swot-weaknesses { border-left: 3px solid #f59e0b; }
    .swot-opportunities { border-left: 3px solid #3b82f6; }
    .swot-threats { border-left: 3px solid #ef4444; }

    /* Formação cards - Clean */
    .formacao-card {
        background: var(--secondary-bg);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: var(--transition);
    }

    .formacao-card:hover {
        background: var(--primary-bg);
        box-shadow: var(--shadow-light);
    }

    /* Status badges - Clean */
    .status-completed { color: #22c55e; font-weight: 600; }
    .status-cursando { color: #3b82f6; font-weight: 600; }
    .status-trancado { color: #f59e0b; font-weight: 600; }
    .status-incompleto { color: #ef4444; font-weight: 600; }

    /* Header principal - Simples */
    .header-container {
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem 0;
    }

    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }

    .header-subtitle {
        font-size: 1.1rem;
        color: var(--text-secondary);
        font-weight: 400;
    }

    /* Footer - Clean */
    .footer-container {
        text-align: center;
        margin-top: 3rem;
        padding: 2rem;
        background: var(--secondary-bg);
        border-radius: var(--border-radius);
        border: 1px solid var(--border-color);
    }

    .footer-text {
        color: var(--text-secondary);
        margin: 0;
        font-size: 0.9rem;
        font-weight: 500;
    }

    /* Responsive design */
    @media (max-width: 768px) {
        .block-container {
            padding: 1rem 0.5rem;
        }

        .glass-card, .cbo-card {
            padding: 1rem;
            margin: 0.5rem 0;
        }

        .metric-card {
            padding: 0.75rem;
        }

        .header-title {
            font-size: 2rem;
        }
    }
</style>
""", unsafe_allow_html=True)

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

# --- FUNÇÃO DE EXTRAÇÃO ---
def extrair_dados(texto):
    return client.chat.completions.create(
        model="gemini-2.5-flash-lite",
        response_model=Curriculo,
        messages=[
            {"role": "user", "content": f"VagaJá: Extraia os dados seguindo o schema. Data de referência: Abril/2026. Currículo: {texto}"}
        ],
    )

# --- INTERFACE STREAMLIT ---
st.set_page_config(
    page_title="VagaJá - Motor de Inteligência",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="🚀"
)

# Header simples e limpo
st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <h1 style="font-size: 2.5rem; margin-bottom: 0.5rem; color: #1e293b; font-weight: 700;">
        🚀 VagaJá
    </h1>
    <p style="font-size: 1.1rem; color: #64748b; margin: 0; font-weight: 400;">
        Motor de Inteligência para Triagem de Candidatos
    </p>
</div>
""", unsafe_allow_html=True)

# Upload section com glassmorphism
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown("### 📄 Upload do Currículo")
st.markdown("Faça upload de um arquivo PDF para análise inteligente dos dados do candidato.")
uploaded_file = st.file_uploader(
    "Selecione o arquivo PDF",
    type="pdf",
    help="Apenas arquivos PDF são aceitos. Tamanho máximo: 200MB",
    label_visibility="collapsed"
)

if uploaded_file:
    st.markdown("### 📊 Processamento")
    if st.button("🚀 **Processar Candidato**", type="primary", use_container_width=True):
        with st.spinner("🤖 O motor VagaJá está analisando o currículo..."):
            reader = PdfReader(uploaded_file)
            texto = "".join([page.extract_text() for page in reader.pages])

            try:
                candidato = extrair_dados(texto)

                # Success message
                st.success(f"✅ **{candidato.nome}** processado com sucesso!")

                # CBO Principal - Destaque especial
                st.markdown('<div class="cbo-card">', unsafe_allow_html=True)
                st.markdown("## 🎯 CBO Principal")

                col_cbo_title, col_cbo_code = st.columns([3, 1])
                with col_cbo_title:
                    st.markdown(f"### {candidato.cbo_principal.titulo}")
                with col_cbo_code:
                    st.metric("Código CBO", candidato.cbo_principal.codigo)

                st.markdown("**Justificativa:**")
                st.info(candidato.cbo_principal.justificativa)
                st.markdown('</div>', unsafe_allow_html=True)

                # Métricas principais
                st.markdown("## 📊 Métricas do Candidato")
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.markdown('<div class="metric-label">Senioridade</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="metric-value">{candidato.senioridade}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                with col2:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.markdown('<div class="metric-label">Tempo de Carreira</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="metric-value">{candidato.tempo_total_carreira_meses}</div>', unsafe_allow_html=True)
                    st.markdown('<div style="font-size: 0.8rem; color: var(--text-secondary);">meses</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                with col3:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.markdown('<div class="metric-label">PCD</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="metric-value">{"Sim" if candidato.pcd else "Não"}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                with col4:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.markdown('<div class="metric-label">Idade</div>', unsafe_allow_html=True)
                    idade_display = candidato.idade if candidato.idade else "N/A"
                    st.markdown(f'<div class="metric-value">{idade_display}</div>', unsafe_allow_html=True)
                    if candidato.idade:
                        st.markdown('<div style="font-size: 0.8rem; color: var(--text-secondary);">anos</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                # Informações detalhadas
                col_left, col_right = st.columns([1, 1])

                with col_left:
                    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                    st.markdown("## 👤 Dados Pessoais")
                    st.write(f"**Nome:** {candidato.nome}")
                    if candidato.idade:
                        st.write(f"**Idade:** {candidato.idade} anos")
                    st.write(f"**PCD:** {'Sim' if candidato.pcd else 'Não'}")

                    st.markdown("## 📍 Localização")
                    st.write(f"**Cidade:** {candidato.localizacao.cidade}")
                    st.write(f"**UF:** {candidato.localizacao.uf}")
                    if candidato.localizacao.bairro:
                        st.write(f"**Bairro:** {candidato.localizacao.bairro}")
                    if candidato.localizacao.cep:
                        st.write(f"**CEP:** {candidato.localizacao.cep}")
                    st.markdown('</div>', unsafe_allow_html=True)

                with col_right:
                    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                    st.markdown("## 💬 Pitch do Recrutador")
                    st.info(candidato.pitch_do_recrutador)
                    st.markdown('</div>', unsafe_allow_html=True)

                # Matriz de Skills
                st.markdown('<div class="skills-container">', unsafe_allow_html=True)
                st.markdown("## 🚀 Matriz de Skills")

                if candidato.matriz_skills:
                    skills_df = pd.DataFrame([
                        {"Skill": skill.skill, "Tipo": skill.tipo, "Nível": skill.nivel}
                        for skill in candidato.matriz_skills
                    ])

                    # Gráfico de skills
                    fig_skills = px.bar(
                        skills_df,
                        x="Skill",
                        y="Nível",
                        color="Tipo",
                        title="",
                        color_discrete_sequence=px.colors.qualitative.Pastel,
                        height=350
                    )
                    fig_skills.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='white',
                        xaxis_title="",
                        yaxis_title="Nível",
                        showlegend=True,
                        legend=dict(
                            bgcolor='rgba(255,255,255,0.1)',
                            bordercolor='rgba(255,255,255,0.2)',
                            borderwidth=1
                        )
                    )
                    fig_skills.update_xaxes(gridcolor='rgba(255,255,255,0.1)')
                    fig_skills.update_yaxes(gridcolor='rgba(255,255,255,0.1)')

                    st.plotly_chart(fig_skills, use_container_width=True, config={'displayModeBar': False})

                    # Tabela de skills
                    st.markdown("### 📋 Detalhamento")
                    st.dataframe(
                        skills_df,
                        column_config={
                            "Skill": st.column_config.TextColumn("Skill", width="large"),
                            "Tipo": st.column_config.TextColumn("Tipo", width="medium"),
                            "Nível": st.column_config.NumberColumn("Nível", format="%d ⭐")
                        },
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("Nenhuma skill identificada no currículo.")
                st.markdown('</div>', unsafe_allow_html=True)

                # Formação Acadêmica
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown("## 🎓 Formação Acadêmica")

                if candidato.formacao:
                    for i, formacao in enumerate(candidato.formacao):
                        st.markdown('<div class="formacao-card">', unsafe_allow_html=True)

                        col_inst, col_curso, col_status = st.columns([2, 2, 1])
                        with col_inst:
                            st.markdown(f"**🏫 {formacao.instituicao}**")
                        with col_curso:
                            st.markdown(f"**📚 {formacao.curso}**")
                        with col_status:
                            status_class = f"status-{formacao.status.lower()}"
                            st.markdown(f'<span class="{status_class}">● {formacao.status}</span>', unsafe_allow_html=True)

                        st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.info("Nenhuma formação acadêmica identificada.")
                st.markdown('</div>', unsafe_allow_html=True)

                # Idiomas
                if candidato.idiomas_e_comunicacao:
                    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                    st.markdown("## 🌍 Idiomas e Comunicação")

                    idiomas_df = pd.DataFrame([
                        {"Idioma": idioma.idioma, "Proficiência": idioma.proficiencia}
                        for idioma in candidato.idiomas_e_comunicacao
                    ])

                    fig_idiomas = px.bar(
                        idiomas_df,
                        x="Idioma",
                        y="Proficiência",
                        title="",
                        color="Proficiência",
                        color_discrete_map={
                            "Nativo": "#22c55e",
                            "Fluente": "#3b82f6",
                            "Avançado": "#f59e0b",
                            "Intermediário": "#8b5cf6",
                            "Básico": "#ef4444"
                        },
                        height=250
                    )
                    fig_idiomas.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='white',
                        xaxis_title="",
                        yaxis_title="",
                        showlegend=False
                    )
                    fig_idiomas.update_xaxes(gridcolor='rgba(255,255,255,0.1)')
                    fig_idiomas.update_yaxes(gridcolor='rgba(255,255,255,0.1)')

                    st.plotly_chart(fig_idiomas, use_container_width=True, config={'displayModeBar': False})
                    st.markdown('</div>', unsafe_allow_html=True)

                # Análise SWOT
                st.markdown("## 📊 Análise SWOT")

                swot = candidato.swot_do_candidato
                col1, col2 = st.columns(2)
                col3, col4 = st.columns(2)

                with col1:
                    st.markdown('<div class="swot-section swot-strengths">', unsafe_allow_html=True)
                    st.markdown("### ✅ Strengths")
                    for strength in swot.strengths:
                        st.markdown(f"• {strength}")
                    st.markdown('</div>', unsafe_allow_html=True)

                with col2:
                    st.markdown('<div class="swot-section swot-weaknesses">', unsafe_allow_html=True)
                    st.markdown("### ⚠️ Weaknesses")
                    for weakness in swot.weaknesses:
                        st.markdown(f"• {weakness}")
                    st.markdown('</div>', unsafe_allow_html=True)

                with col3:
                    st.markdown('<div class="swot-section swot-opportunities">', unsafe_allow_html=True)
                    st.markdown("### 🚀 Opportunities")
                    for opportunity in swot.opportunities:
                        st.markdown(f"• {opportunity}")
                    st.markdown('</div>', unsafe_allow_html=True)

                with col4:
                    st.markdown('<div class="swot-section swot-threats">', unsafe_allow_html=True)
                    st.markdown("### ❌ Threats")
                    for threat in swot.threats:
                        st.markdown(f"• {threat}")
                    st.markdown('</div>', unsafe_allow_html=True)

                # JSON Completo
                with st.expander("🔍 **Ver Dados Completos (JSON)**"):
                    st.json(candidato.model_dump_json())

            except Exception as e:
                st.error(f"❌ **Erro ao processar:** {str(e)}")

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 3rem; padding: 2rem; background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px); border-radius: 16px;">
    <p style="color: rgba(255, 255, 255, 0.8); margin: 0; font-size: 0.9rem;">
        🚀 <strong>VagaJá</strong> - Motor de Inteligência para Recrutamento | Powered by Gemini AI
    </p>
</div>
""", unsafe_allow_html=True)
