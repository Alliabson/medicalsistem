import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import time
import requests
from datetime import datetime

# Importando os dados e a base de conhecimento do nosso arquivo utils/data.py
from utils.data import (
    available_symptoms,
    doctors_data,
    disease_database
)

# --- CONFIGURAÇÃO DA PÁGINA E ESTADO DA SESSÃO ---
st.set_page_config(
    page_title="MediAssist - Telemedicina",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="auto"
)

# Carrega o CSS do arquivo
def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"Arquivo CSS '{file_name}' não encontrado. A aparência pode ser afetada.")

load_css("assets/styles.css")

# Estado da sessão para navegação e dados
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Diagnóstico'
if 'user_symptoms' not in st.session_state:
    st.session_state.user_symptoms = []
if 'diagnosis_results' not in st.session_state:
    st.session_state.diagnosis_results = None
if 'is_loading' not in st.session_state:
    st.session_state.is_loading = False
if 'appointments_data' not in st.session_state:
    st.session_state.appointments_data = []

# --- FUNÇÃO DE DIAGNÓSTICO INTELIGENTE ---
def generate_diagnosis(symptoms):
    user_symptoms_set = set(symptoms)
    possible_conditions = []

    for disease, data in disease_database.items():
        disease_symptoms = data['symptoms']
        matching_symptoms = user_symptoms_set.intersection(disease_symptoms)
        score = len(matching_symptoms)

        if score > 0:
            match_percentage = score / len(disease_symptoms)
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
            'description': 'Os sintomas não correspondem a uma condição em nossa base. Recomenda-se a consulta com um clínico geral.',
            'matching_symptoms': symptoms
        })

    possible_conditions.sort(key=lambda x: x['probability'], reverse=True)

    recommendations = {'Hidrate-se adequadamente', 'Descanse o suficiente'}
    if any(c['probability'] > 0.7 for c in possible_conditions):
        recommendations.add('É altamente recomendável consultar um médico.')
    if 'dificuldade respiratória' in user_symptoms_set:
        recommendations.add('ATENÇÃO: Dificuldade para respirar é um sintoma grave. Procure atendimento de emergência.')
    if 'febre' in user_symptoms_set:
        recommendations.add('Monitore sua temperatura. Se a febre persistir, procure um médico.')

    return {'possible_conditions': possible_conditions, 'recommendations': list(recommendations), 'analyzed_symptoms': symptoms}


# --- PÁGINAS DO APLICATIVO ---

def home_page():
    st.title("🏥 Bem-vindo ao MediAssist")
    st.markdown("Seu assistente de telemedicina pessoal. Use o menu à esquerda para começar.")
    # Adicione mais conteúdo à sua página inicial se desejar

def diagnosis_page():
    st.title("🔍 Diagnóstico de Sintomas")
    st.markdown("Selecione os sintomas que você está sentindo para receber uma análise preliminar e inteligente.")
    st.session_state.user_symptoms = st.multiselect(
        "Selecione seus sintomas:", options=available_symptoms,
        default=st.session_state.user_symptoms, help="Você pode selecionar múltiplos sintomas."
    )
    if st.button("Analisar Sintomas", disabled=not st.session_state.user_symptoms, type="primary"):
        st.session_state.is_loading = True
        st.rerun()
    if st.session_state.is_loading:
        with st.spinner("Analisando seus sintomas..."):
            time.sleep(1)
            st.session_state.diagnosis_results = generate_diagnosis(st.session_state.user_symptoms)
            st.session_state.is_loading = False
        st.rerun()
    if st.session_state.diagnosis_results:
        display_diagnosis_results()

def appointments_page():
    st.title("📅 Agendamento de Consultas")
    tab1, tab2 = st.tabs(["**Próximas Consultas**", "**Agendar Nova Consulta**"])
    with tab1:
        display_appointments()
    with tab2:
        st.subheader("Encontre um Médico")
        for _, doctor in doctors_data.iterrows():
            with st.container(border=True):
                cols = st.columns([1, 4, 2])
                with cols[0]:
                    try:
                        st.image("assets/icons/user.svg", width=60)
                    except Exception:
                        st.markdown("🧑‍⚕️")
                with cols[1]:
                    st.subheader(f"Dr(a). {doctor['name']}")
                    st.caption(f"**Especialidade:** {doctor['specialty']} | **Tipo:** {doctor['appointment_type'].capitalize()}")
                with cols[2]:
                    if st.button("Agendar Agora", key=f"schedule_{doctor['id']}"):
                        new_appointment = {'doctor': doctor['name'], 'specialty': doctor['specialty'], 'date': f"{datetime.now().day+1}/{datetime.now().month}/{datetime.now().year}", 'time': '10:00', 'type': doctor['appointment_type']}
                        st.session_state.appointments_data.append(new_appointment)
                        st.success(f"Consulta com Dr(a). {doctor['name']} agendada!")
                        time.sleep(2)
                        st.rerun()

# --- FUNÇÕES DE EXIBIÇÃO (do antigo helpers.py) ---
def display_diagnosis_results():
    results = st.session_state.diagnosis_results
    st.subheader("Resultados da Análise")
    st.info(f"**Sintomas Analisados:** {', '.join(results['analyzed_symptoms'])}")
    st.markdown("---")
    for condition in results.get('possible_conditions', []):
        with st.container(border=True):
            st.subheader(f"{condition['name']} - Probabilidade: {int(condition['probability'] * 100)}%")
            st.progress(condition['probability'])
            st.write(f"*{condition['description']}*")
            if 'matching_symptoms' in condition and condition['matching_symptoms']:
                st.write(f"**Sintomas correspondentes:** {', '.join(condition['matching_symptoms'])}")
    st.subheader("Recomendações")
    for rec in results.get('recommendations', []):
        if "ATENÇÃO" in rec:
            st.warning(f"⚠️ {rec}")
        else:
            st.success(f"✅ {rec}")
    st.markdown("---")
    st.warning("**Aviso:** Este é um diagnóstico preliminar e não substitui a consulta com um profissional de saúde qualificado.")

def display_appointments():
    st.subheader("Suas Consultas Agendadas")
    if not st.session_state.appointments_data:
        st.info("Você ainda não possui nenhuma consulta agendada.")
    else:
        for app in st.session_state.appointments_data:
            with st.container(border=True):
                st.markdown(f"**Médico(a):** Dr(a). {app['doctor']} ({app['specialty']})")
                st.markdown(f"**Data:** {app['date']} às {app['time']}")
                st.markdown(f"**Tipo:** {app['type'].capitalize()}")


# --- NAVEGAÇÃO PRINCIPAL E EXECUÇÃO ---
def main():
    with st.sidebar:
        st.session_state.current_page = option_menu(
            "MediAssist Menu", ["Início", "Diagnóstico", "Agendamentos"],
            icons=['house', 'search-heart', 'calendar-check'],
            menu_icon="menu-button-wide", default_index=1,
            styles={"nav-link-selected": {"background-color": "#0d6efd"}}
        )
    
    if st.session_state.current_page == "Início":
        home_page()
    elif st.session_state.current_page == "Diagnóstico":
        diagnosis_page()
    elif st.session_state.current_page == "Agendamentos":
        appointments_page()

if __name__ == "__main__":
    main()
