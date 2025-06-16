import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import time
import requests
from datetime import datetime
import re # Usado para criar URLs amigáveis

# --- DADOS E LÓGICA (Anteriormente em utils/data.py) ---

disease_database = {
    'COVID-19': {'symptoms': {'febre', 'tosse', 'cansaço', 'perda de paladar ou olfato', 'dificuldade respiratória', 'dor de cabeça', 'dor muscular'}, 'description': 'Infecção respiratória viral causada pelo SARS-CoV-2.', 'base_probability': 0.4},
    'Amigdalite': {'symptoms': {'dor de garganta', 'febre', 'dificuldade para engolir', 'gânglios inchados', 'dor de cabeça'}, 'description': 'Inflamação das amígdalas, geralmente por infecção viral ou bacteriana.', 'base_probability': 0.6},
    'Gastrite': {'symptoms': {'dor abdominal', 'náusea', 'vômito', 'sensação de inchaço', 'azia'}, 'description': 'Inflamação do revestimento do estômago.', 'base_probability': 0.7},
    'Dengue': {'symptoms': {'febre', 'dor de cabeça', 'dor muscular', 'dores nas articulações', 'manchas vermelhas na pele', 'náusea'}, 'description': 'Doença viral transmitida pelo mosquito Aedes aegypti.', 'base_probability': 0.5},
    'Resfriado Comum': {'symptoms': {'coriza', 'espirros', 'tosse', 'dor de garganta'}, 'description': 'Infecção viral leve do nariz e da garganta.', 'base_probability': 0.8},
    'Sinusite': {'symptoms': {'dor de cabeça', 'congestão nasal', 'pressão facial', 'coriza', 'tosse'}, 'description': 'Inflamação dos seios nasais, que pode ser causada por infecção ou alergia.', 'base_probability': 0.6}
}

# NOVO MAPEAMENTO: De Condição para Especialidade Médica
condition_to_specialty = {
    'COVID-19': 'Clínico Geral',
    'Amigdalite': 'Otorrinolaringologista',
    'Gastrite': 'Gastroenterologista',
    'Dengue': 'Clínico Geral',
    'Resfriado Comum': 'Clínico Geral',
    'Sinusite': 'Otorrinolaringologista',
    'Condição Não Especificada': 'Clínico Geral'
}

all_symptoms = sorted(list(set(symptom for disease in disease_database.values() for symptom in disease['symptoms'])))


# --- CONFIGURAÇÃO DA PÁGINA E ESTADO ---
st.set_page_config(page_title="MediAssist", page_icon="🏥", layout="wide")

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Diagnóstico'
if 'user_symptoms' not in st.session_state:
    st.session_state.user_symptoms = []
if 'diagnosis_results' not in st.session_state:
    st.session_state.diagnosis_results = None
if 'is_loading' not in st.session_state:
    st.session_state.is_loading = False

# --- LÓGICA DE DIAGNÓSTICO (sem alterações) ---
def generate_diagnosis(symptoms):
    user_symptoms_set = set(symptoms)
    possible_conditions = []
    for disease, data in disease_database.items():
        matching_symptoms = user_symptoms_set.intersection(data['symptoms'])
        if matching_symptoms:
            match_percentage = len(matching_symptoms) / len(data['symptoms'])
            probability = data['base_probability'] * match_percentage
            if 'dificuldade respiratória' in matching_symptoms and disease == 'COVID-19':
                probability *= 1.5
            possible_conditions.append({
                'name': disease, 'probability': round(min(probability, 0.95), 2),
                'description': data['description'], 'matching_symptoms': list(matching_symptoms)
            })
    if not possible_conditions and symptoms:
        possible_conditions.append({
            'name': 'Condição Não Especificada', 'probability': 0.2,
            'description': 'Os sintomas não correspondem a uma condição na base. Consulte um clínico geral.',
            'matching_symptoms': symptoms
        })
    possible_conditions.sort(key=lambda x: x['probability'], reverse=True)
    recommendations = {'Hidrate-se', 'Descanse'}
    if any(c['probability'] > 0.7 for c in possible_conditions):
        recommendations.add('Consulte um médico nos próximos dias.')
    if 'dificuldade respiratória' in user_symptoms_set:
        recommendations.add('ATENÇÃO: Dificuldade para respirar é grave. Procure emergência.')
    if 'febre' in user_symptoms_set:
        recommendations.add('Monitore a temperatura. Se persistir, procure um médico.')
    return {'possible_conditions': possible_conditions, 'recommendations': list(recommendations), 'analyzed_symptoms': symptoms}

# --- FUNÇÃO AUXILIAR PARA CRIAR URL ---
def slugify(text):
    text = text.lower()
    text = re.sub(r'[\s\(\)]+', '-', text)  # Substitui espaços e parênteses por hífen
    text = re.sub(r'[^a-z0-9-]', '', text) # Remove caracteres não alfanuméricos exceto hífen
    return text

# --- PÁGINAS DO APP ---
def diagnosis_page():
    st.title("🔍 Diagnóstico de Sintomas")
    st.markdown("Selecione os sintomas que você está sentindo para receber uma análise preliminar.")
    st.session_state.user_symptoms = st.multiselect("Selecione seus sintomas:", options=all_symptoms, default=st.session_state.user_symptoms)
    if st.button("Analisar Sintomas", disabled=not st.session_state.user_symptoms, type="primary"):
        st.session_state.is_loading = True
        st.session_state.diagnosis_results = None # Limpa resultados antigos
        st.rerun()
    if st.session_state.is_loading:
        with st.spinner("Analisando..."):
            time.sleep(1)
            st.session_state.diagnosis_results = generate_diagnosis(st.session_state.user_symptoms)
            st.session_state.is_loading = False
        st.rerun()
        
    if st.session_state.diagnosis_results:
        results = st.session_state.diagnosis_results
        st.subheader("Resultados da Análise")
        st.info(f"**Sintomas Analisados:** {', '.join(results['analyzed_symptoms'])}")
        st.divider()

        # Exibe as condições
        for condition in results.get('possible_conditions', []):
            with st.container(border=True):
                st.subheader(f"{condition['name']} - Probabilidade: {int(condition['probability'] * 100)}%")
                st.progress(condition['probability'])
                st.write(f"*{condition['description']}*")
        
        st.divider()

        # NOVA SEÇÃO: AÇÃO RECOMENDADA COM BASE NO DIAGNÓSTICO
        st.subheader("🚀 Próximo Passo: Encontre um Especialista")
        top_condition = results['possible_conditions'][0]['name']
        recommended_specialty = condition_to_specialty.get(top_condition, 'Clínico Geral')
        
        st.success(f"Com base na sua análise, a especialidade recomendada é **{recommended_specialty}**.")
        
        # Cria a URL para a Doctoralia (exemplo)
        specialty_slug = slugify(recommended_specialty)
        doctoralia_url = f"https://www.doctoralia.com.br/especialistas/telemedicina/{specialty_slug}"
        
        st.markdown(f"""
        Clique no botão abaixo para ver uma lista de especialistas disponíveis para teleconsulta.
        
        <a href="{doctoralia_url}" target="_blank">
            <button style="
                width: 100%; 
                padding: 10px; 
                font-size: 18px; 
                font-weight: bold; 
                color: white; 
                background-color: #0d6efd; 
                border: none; 
                border-radius: 5px; 
                cursor: pointer;">
                Buscar {recommended_specialty}s Online
            </button>
        </a>
        """, unsafe_allow_html=True)

        st.divider()
        st.subheader("Recomendações Gerais")
        for rec in results.get('recommendations', []):
            st.warning(rec) if "ATENÇÃO" in rec else st.success(f"✅ {rec}")
        st.caption("Aviso: Este diagnóstico não substitui a avaliação de um profissional de saúde.")

def info_page():
    st.title("ℹ️ Sobre o MediAssist")
    st.markdown("""
    O **MediAssist** é uma ferramenta de triagem inicial projetada para ajudar os usuários a entenderem melhor seus sintomas. 
    
    ### Funcionalidades
    - **Diagnóstico Inteligente:** Utiliza uma base de conhecimento para analisar os sintomas e sugerir possíveis condições médicas.
    - **Recomendações de Especialistas:** Com base no diagnóstico, o MediAssist sugere a especialidade médica mais adequada e facilita a busca por profissionais de telemedicina em plataformas externas.
    
    ### Aviso Legal
    Este aplicativo é uma ferramenta de suporte e **não substitui um diagnóstico médico profissional**. As probabilidades e recomendações são baseadas em um modelo simplificado. Sempre consulte um médico para questões de saúde.
    """)

# --- NAVEGAÇÃO E EXECUÇÃO ---
def main():
    with st.sidebar:
        st.session_state.current_page = option_menu(
            "MediAssist Menu", ["Diagnóstico", "Sobre"],
            icons=['search-heart', 'info-circle-fill'], menu_icon="menu-button-wide",
            default_index=0, styles={"nav-link-selected": {"background-color": "#0d6efd"}}
        )
    if st.session_state.current_page == "Diagnóstico":
        diagnosis_page()
    elif st.session_state.current_page == "Sobre":
        info_page()

if __name__ == "__main__":
    main()
