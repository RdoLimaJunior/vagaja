import streamlit as st
import instructor
from google import genai
from pydantic import BaseModel, Field
from typing import List, Optional
from pypdf import PdfReader
import json

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
            {"role": "system", "content": "Você é o Motor de Inteligência VagaJá. Extraia dados de currículos para triagem técnica. Considere hoje como Abril de 2026."},
            {"role": "user", "content": texto}
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
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.subheader(f"Candidato: {candidato.nome}")
                    st.metric("Senioridade", candidato.senioridade)
                    st.write(f"**Tempo de carreira:** {candidato.tempo_total_carreira_meses} meses")
                    st.info(candidato.pitch_do_recrutador)
                
                with col2:
                    st.subheader("Análise SWOT")
                    st.write(candidato.swot_do_candidato.model_dump())
                
                with st.expander("Ver JSON Completo"):
                    st.json(candidato.model_dump_json())
                    
            except Exception as e:
                st.error(f"Erro ao processar: {e}")