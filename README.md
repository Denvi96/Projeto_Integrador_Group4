# 🤖 NPC Chatbot — Projeto Integrador | Jovem Programador

O **NPC Chatbot (Núcleo de Processamento Conversacional)** é um assistente virtual criado como parte do Projeto Integrador do curso **Jovem Programador**, com o objetivo de tirar dúvidas sobre o programa utilizando inteligência artificial e dados obtidos diretamente do [site oficial](https://www.jovemprogramador.com.br).

---

## 🎯 Objetivo

Fornecer uma experiência de conversa amigável e informativa, ajudando usuários a entenderem melhor o Programa Jovem Programador — com linguagem acessível, foco no conteúdo real do site e respostas rápidas, inteligentes e personalizadas.

---

## 🧠 Tecnologias Utilizadas

- **Python 3.11+**
- **FastAPI** (backend e API)
- **SQLite** (armazenamento em cache local)
- **BeautifulSoup** (web scraping)
- **Google Generative AI (Gemini API)** para respostas com linguagem natural
- **Sentence Transformers** (para similaridade semântica)
- **LangChain / Logging avançado**
- **Interface CLI em terminal (colorida e interativa)**

---

## ⚙️ Como Rodar o Projeto

### Pré-requisitos

- Python 3.11 ou superior
- Git

### Passo a passo

```bash
# Clone o repositório
git clone https://github.com/Denvi96/Projeto_Integrador_Group4.git
cd Projeto_Integrador_Group4

# Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate     # Linux/macOS
venv\Scripts\activate        # Windows

# Instale as dependências
pip install -r requirements.txt

# Configure a chave da API Gemini
# Crie um arquivo .env com sua chave:
echo "GOOGLE_API_KEY=your-api-key" > .env

# Execute o chatbot
python main.py
