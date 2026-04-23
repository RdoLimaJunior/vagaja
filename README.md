# 🚀 VagaJá - Motor de Inteligência de Candidatos

Uma aplicação Streamlit inteligente para triagem automática de currículos usando IA Gemini e Pydantic.

## ✨ Funcionalidades

- 📄 **Upload de PDF**: Faça upload de currículos em formato PDF
- 🤖 **Extração Inteligente**: Usa Gemini 2.0 Flash para extrair dados estruturados
- 📊 **Análise SWOT**: Gera análise automática de pontos fortes, fracos, oportunidades e ameaças
- 🎯 **Triagem Técnica**: Classifica senioridade, habilidades e experiência
- 📈 **Dashboard Interativo**: Interface moderna com métricas e visualizações

## 🛠️ Tecnologias Utilizadas

- **Streamlit**: Framework web para aplicações de dados
- **Google Gemini 2.0 Flash**: IA para processamento de linguagem natural
- **Instructor**: Biblioteca para estruturar respostas de IA com Pydantic
- **PyPDF**: Extração de texto de arquivos PDF
- **Pydantic**: Validação e serialização de dados

## 🚀 Deploy

### Streamlit Cloud

1. Acesse [share.streamlit.io](https://share.streamlit.io)
2. Clique em "New app"
3. Configure:
   - Repository: `RdoLimaJunior/vagaja`
   - Branch: `main`
   - Main file path: `streamlit_app.py`
4. Deploy e aguarde a build
5. Configure a secret no App Settings:
   ```
   GEMINI_API_KEY = "sua-chave-gemini-aqui"
   ```

### Desenvolvimento Local

1. Clone o repositório:
   ```bash
   git clone https://github.com/RdoLimaJunior/vagaja.git
   cd vagaja
   ```

2. Crie um ambiente virtual:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # ou
   .venv\Scripts\activate     # Windows
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure a API key do Gemini:
   - Crie o arquivo `.streamlit/secrets.toml`
   - Adicione: `GEMINI_API_KEY = "sua-chave-aqui"`

5. Execute a aplicação:
   ```bash
   streamlit run streamlit_app.py
   ```

## 📋 Estrutura dos Dados Extraídos

A aplicação extrai automaticamente:

- **Dados Pessoais**: Nome, idade, PCD
- **Localização**: Cidade, UF, bairro, CEP
- **Profissional**: Senioridade, tempo de carreira
- **CBO**: Código e título da ocupação principal
- **Formação**: Instituições, cursos e status
- **Idiomas**: Idiomas e níveis de proficiência
- **Habilidades**: Matriz de skills com tipos e níveis
- **Análise SWOT**: Pontos fortes, fracos, oportunidades e ameaças

## 🔧 Configuração

### Secrets

Para desenvolvimento local, crie `.streamlit/secrets.toml`:
```toml
GEMINI_API_KEY = "sua-chave-gemini-aqui"
```

Para produção no Streamlit Cloud, configure no App Settings.

### API Key do Gemini

1. Acesse [Google AI Studio](https://aistudio.google.com/)
2. Clique em "Create API Key"
3. Copie a chave gerada
4. Configure nos secrets conforme acima

## 📊 Como Usar

1. **Upload**: Selecione um arquivo PDF de currículo
2. **Processamento**: Clique em "Processar Candidato"
3. **Análise**: Aguarde a extração e análise automática
4. **Resultado**: Visualize os dados estruturados e análise SWOT
5. **JSON**: Expanda para ver o JSON completo dos dados

## 🤝 Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para:

- Reportar bugs
- Sugerir melhorias
- Enviar pull requests

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👨‍💻 Autor

**RdoLimaJunior** - [GitHub](https://github.com/RdoLimaJunior)

---

⭐ **Dê uma estrela se este projeto te ajudou!**
