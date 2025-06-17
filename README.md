📋 MediAssist - Sistema de Triagem Médica Inteligente
📌 Visão Geral
O MediAssist é uma aplicação web desenvolvida em Python com Streamlit que oferece triagem médica preliminar baseada em sintomas. O sistema analisa os sintomas relatados pelo usuário, sugere possíveis condições médicas com suas probabilidades, recomenda especialistas adequados e auxilia na localização de unidades de saúde próximas.

✨ Funcionalidades Principais
✅ Diagnóstico Preliminar

Analisa sintomas e calcula a probabilidade de condições médicas associadas

Exibe descrições detalhadas das possíveis doenças

✅ Recomendações Personalizadas

Sugere ações imediatas (hidratação, repouso, emergência)

Indica quando procurar um médico

✅ Busca Integrada de Profissionais

Encontra especialistas (médicos, clínicas, hospitais) no Google Maps

Oferece opções de telemedicina baseadas na localização do usuário

✅ Interface Amigável

Design intuitivo e responsivo

Navegação simplificada

🛠️ Tecnologias Utilizadas
Python (Linguagem principal)

Streamlit (Framework para interface web)

Requests (Para consumo de APIs)

Google Maps/Google Search (Integração para busca de profissionais)


🚀 Como Executar o Projeto
Pré-requisitos
Python 3.8+ instalado

Gerenciador de pacotes pip

Passo a Passo
Clone o repositório

bash
git clone https://github.com/seu-usuario/mediassist.git
cd mediassist
Crie um ambiente virtual (opcional, mas recomendado)

bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows
Instale as dependências

bash
pip install -r requirements.txt
Execute o aplicativo

bash
streamlit run app.py
Acesse no navegador
Abra http://localhost:8501 no seu navegador.
