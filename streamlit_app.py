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

# --- CSS PERSONALIZADO PARA GLASSMORPHISM ---
st.markdown("""
<style>
    /* Reset e variáveis de cor */
    :root {
        --primary-bg: #f8fafc;
        --secondary-bg: #ffffff;
        --accent-color: #3b82f6;
        --accent-light: #dbeafe;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --glass-bg: rgba(255, 255, 255, 0.25);
        --glass-border: rgba(255, 255, 255, 0.18);
        --shadow-light: 0 8px 32px rgba(0, 0, 0, 0.1);
        --shadow-medium: 0 12px 40px rgba(0, 0, 0, 0.15);
        --border-radius: 16px;
        --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* Body e background */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
        min-height: 100vh;
    }

    /* Container principal */
    .block-container {
        background: transparent !important;
        padding: 2rem 1rem;
        max-width: 1200px;
        margin: 0 auto;
    }

    /* Header */
    .stApp header {
        background: transparent !important;
    }

    /* Títulos */
    h1, h2, h3 {
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    /* Cards com glassmorphism */
    .glass-card {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: var(--border-radius);
        box-shadow: var(--shadow-light);
        padding: 2rem;
        margin: 1rem 0;
        transition: var(--transition);
    }

    .glass-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-medium);
    }

    /* Card CBO especial */
    .cbo-card {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(147, 197, 253, 0.1));
        backdrop-filter: blur(25px);
        -webkit-backdrop-filter: blur(25px);
        border: 2px solid rgba(59, 130, 246, 0.3);
        border-radius: var(--border-radius);
        box-shadow: 0 20px 60px rgba(59, 130, 246, 0.2);
        padding: 2rem;
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
        height: 4px;
        background: linear-gradient(90deg, #3b82f6, #1d4ed8, #1e40af);
    }

    /* Métricas */
    .metric-card {
        background: var(--glass-bg);
        backdrop-filter: blur(15px);
        border: 1px solid var(--glass-border);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: var(--shadow-light);
        transition: var(--transition);
    }

    .metric-card:hover {
        transform: scale(1.02);
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: var(--accent-color);
        margin: 0.5rem 0;
    }

    .metric-label {
        font-size: 0.9rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }

    /* Botões */
    .stButton button {
        background: linear-gradient(135deg, var(--accent-color), #1d4ed8);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
        transition: var(--transition);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
    }

    /* File uploader */
    .uploadedFile {
        background: var(--glass-bg);
        backdrop-filter: blur(15px);
        border: 2px dashed var(--glass-border);
        border-radius: var(--border-radius);
        padding: 2rem;
        text-align: center;
        transition: var(--transition);
    }

    .uploadedFile:hover {
        border-color: var(--accent-color);
        background: rgba(59, 130, 246, 0.05);
    }

    /* Progress bars */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--accent-color), #1d4ed8);
        border-radius: 10px;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: var(--glass-bg);
        backdrop-filter: blur(15px);
        border: 1px solid var(--glass-border);
        border-radius: 12px;
        padding: 1rem;
        font-weight: 600;
        color: var(--text-primary);
    }

    /* Dataframe */
    .stDataFrame {
        background: var(--glass-bg);
        backdrop-filter: blur(15px);
        border: 1px solid var(--glass-border);
        border-radius: var(--border-radius);
        box-shadow: var(--shadow-light);
    }

    /* Success messages */
    .stSuccess {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.1), rgba(22, 163, 74, 0.1));
        backdrop-filter: blur(15px);
        border: 1px solid rgba(34, 197, 94, 0.3);
        border-radius: var(--border-radius);
        color: #16a34a;
        font-weight: 600;
    }

    /* Error messages */
    .stError {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(220, 38, 38, 0.1));
        backdrop-filter: blur(15px);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: var(--border-radius);
        color: #dc2626;
        font-weight: 600;
    }

    /* Info messages */
    .stInfo {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(37, 99, 235, 0.1));
        backdrop-filter: blur(15px);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: var(--border-radius);
        color: var(--accent-color);
        font-weight: 600;
    }

    /* Skills chart container */
    .skills-container {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: var(--border-radius);
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: var(--shadow-light);
    }

    /* SWOT sections */
    .swot-section {
        background: var(--glass-bg);
        backdrop-filter: blur(15px);
        border: 1px solid var(--glass-border);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        transition: var(--transition);
    }

    .swot-section:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-medium);
    }

    .swot-strengths { border-left: 4px solid #22c55e; }
    .swot-weaknesses { border-left: 4px solid #f59e0b; }
    .swot-opportunities { border-left: 4px solid #3b82f6; }
    .swot-threats { border-left: 4px solid #ef4444; }

    /* Formação cards */
    .formacao-card {
        background: var(--glass-bg);
        backdrop-filter: blur(15px);
        border: 1px solid var(--glass-border);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        transition: var(--transition);
    }

    .formacao-card:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-light);
    }

    /* Status badges */
    .status-completed { color: #22c55e; font-weight: 600; }
    .status-cursando { color: #3b82f6; font-weight: 600; }
    .status-trancado { color: #f59e0b; font-weight: 600; }
    .status-incompleto { color: #ef4444; font-weight: 600; }

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
            padding: 1rem;
        }
    }

    /* Scrollbar customizado */
    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.3);
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.5);
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

# Header com glassmorphism
st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <h1 style="font-size: 3rem; margin-bottom: 0.5rem; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: none;">
        🚀 VagaJá
    </h1>
    <p style="font-size: 1.2rem; color: rgba(255, 255, 255, 0.9); margin: 0; font-weight: 300;">
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
                    st.markdown(f"""
                    <div style="background-color: #f0f8ff; padding: 20px; border-radius: 10px; border-left: 5px solid #1f77b4;">
                        <h3 style="color: #1f77b4; margin: 0;">{candidato.cbo_principal.titulo}</h3>
                        <p style="font-size: 18px; font-weight: bold; margin: 5px 0;">Código: {candidato.cbo_principal.codigo}</p>
                        <p style="margin: 0; color: #666;">{candidato.cbo_principal.justificativa}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_seniority:
                    st.subheader("📊 Senioridade")
                    st.metric("Nível", candidato.senioridade, delta=f"{candidato.tempo_total_carreira_meses} meses de carreira")
                
                # Informações básicas
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.subheader("👤 Dados Pessoais")
                    st.write(f"**Nome:** {candidato.nome}")
                    if candidato.idade:
                        st.write(f"**Idade:** {candidato.idade} anos")
                    st.write(f"**PCD:** {'Sim' if candidato.pcd else 'Não'}")
                
                with col2:
                    st.subheader("📍 Localização")
                    st.write(f"**Cidade:** {candidato.localizacao.cidade}")
                    st.write(f"**UF:** {candidato.localizacao.uf}")
                    if candidato.localizacao.bairro:
                        st.write(f"**Bairro:** {candidato.localizacao.bairro}")
                
                with col3:
                    st.subheader("💼 Carreira")
                    st.write(f"**Tempo total:** {candidato.tempo_total_carreira_meses} meses")
                    st.write(f"**Senioridade:** {candidato.senioridade}")
                
                # Matriz de Skills - Gráfico interativo
                st.markdown("---")
                st.subheader("🚀 Matriz de Skills")
                
                if candidato.matriz_skills:
                    # Preparar dados para o gráfico
                    skills_df = pd.DataFrame([
                        {"Skill": skill.skill, "Tipo": skill.tipo, "Nível": skill.nivel}
                        for skill in candidato.matriz_skills
                    ])
                    
                    # Gráfico de barras por tipo de skill
                    fig_skills = px.bar(
                        skills_df,
                        x="Skill",
                        y="Nível",
                        color="Tipo",
                        title="Níveis de Competência por Skill",
                        color_discrete_sequence=px.colors.qualitative.Set3,
                        height=400
                    )
                    fig_skills.update_layout(
                        xaxis_title="Skills",
                        yaxis_title="Nível de Competência",
                        showlegend=True
                    )
                    st.plotly_chart(fig_skills, use_container_width=True)
                    
                    # Tabela detalhada das skills
                    st.subheader("📋 Detalhamento das Skills")
                    st.dataframe(
                        skills_df,
                        column_config={
                            "Skill": st.column_config.TextColumn("Skill", width="medium"),
                            "Tipo": st.column_config.TextColumn("Tipo", width="small"),
                            "Nível": st.column_config.NumberColumn("Nível", format="%d")
                        },
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("Nenhuma skill identificada no currículo.")
                
                # Formação Acadêmica
                st.markdown("---")
                st.subheader("🎓 Formação Acadêmica")
                
                if candidato.formacao:
                    for formacao in candidato.formacao:
                        with st.container():
                            col_inst, col_curso, col_status = st.columns([2, 2, 1])
                            with col_inst:
                                st.write(f"**Instituição:** {formacao.instituicao}")
                            with col_curso:
                                st.write(f"**Curso:** {formacao.curso}")
                            with col_status:
                                status_color = {
                                    "Concluído": "green",
                                    "Cursando": "blue",
                                    "Trancado": "orange",
                                    "Incompleto": "red"
                                }.get(formacao.status, "gray")
                                st.markdown(f'<span style="color: {status_color}; font-weight: bold;">{formacao.status}</span>', unsafe_allow_html=True)
                        st.markdown("---")
                else:
                    st.info("Nenhuma formação acadêmica identificada.")
                
                # Idiomas e Comunicação
                st.markdown("---")
                st.subheader("🌍 Idiomas e Comunicação")
                
                if candidato.idiomas_e_comunicacao:
                    idiomas_df = pd.DataFrame([
                        {"Idioma": idioma.idioma, "Proficiência": idioma.proficiencia}
                        for idioma in candidato.idiomas_e_comunicacao
                    ])
                    
                    # Gráfico de idiomas
                    fig_idiomas = px.bar(
                        idiomas_df,
                        x="Idioma",
                        y="Proficiência",
                        title="Proficiência em Idiomas",
                        color="Proficiência",
                        color_discrete_map={
                            "Nativo": "#2E8B57",
                            "Fluente": "#32CD32",
                            "Avançado": "#FFD700",
                            "Intermediário": "#FFA500",
                            "Básico": "#FF6347"
                        },
                        height=300
                    )
                    st.plotly_chart(fig_idiomas, use_container_width=True)
                else:
                    st.info("Nenhum idioma identificado.")
                
                # Pitch do Recrutador
                st.markdown("---")
                st.subheader("💬 Pitch do Recrutador")
                st.info(candidato.pitch_do_recrutador)
                
                # Análise SWOT
                st.markdown("---")
                st.subheader("📊 Análise SWOT")
                
                swot = candidato.swot_do_candidato
                col_strengths, col_weaknesses = st.columns(2)
                col_opportunities, col_threats = st.columns(2)
                
                with col_strengths:
                    st.markdown("### ✅ Strengths (Pontos Fortes)")
                    for strength in swot.strengths:
                        st.markdown(f"• {strength}")
                
                with col_weaknesses:
                    st.markdown("### ❌ Weaknesses (Pontos Fracos)")
                    for weakness in swot.weaknesses:
                        st.markdown(f"• {weakness}")
                
                with col_opportunities:
                    st.markdown("### 🚀 Opportunities (Oportunidades)")
                    for opportunity in swot.opportunities:
                        st.markdown(f"• {opportunity}")
                
                with col_threats:
                    st.markdown("### ⚠️ Threats (Ameaças)")
                    for threat in swot.threats:
                        st.markdown(f"• {threat}")
                
                # JSON Completo (expandido)
                with st.expander("🔍 Ver Dados Completos (JSON)"):
                    st.json(candidato.model_dump_json())
                    
            except Exception as e:
                st.error(f"Erro ao processar: {e}")