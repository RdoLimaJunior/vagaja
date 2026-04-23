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
st.set_page_config(page_title="VagaJá - Triagem Inteligente", layout="wide")
st.title("🚀 VagaJá - Motor de Inteligência de Candidatos")
st.markdown("Suba o currículo em PDF para extração estruturada e análise SWOT.")

uploaded_file = st.file_uploader("Upload do Currículo", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    texto = "".join([page.extract_text() for page in reader.pages])
    
    if st.button("Processar Candidato"):
        with st.spinner("O motor VagaJá está analisando..."):
            try:
                candidato = extrair_dados(texto)
                
                # Exibição dos resultados
                st.success(f"✅ Candidato {candidato.nome} processado com sucesso!")
                
                # CBO Principal - Destaque especial
                st.markdown("---")
                col_cbo, col_seniority = st.columns([2, 1])
                
                with col_cbo:
                    st.subheader("🎯 CBO Principal")
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