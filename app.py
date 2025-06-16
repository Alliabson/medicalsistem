import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import time
import requests
from datetime import datetime

# --- DADOS E LÓGICA (Anteriormente em utils/data.py) ---

disease_database = {
    'COVID-19': {
        'symptoms': {'febre', 'tosse', 'cansaço', 'perda de paladar ou olfato', 'dificuldade respiratória', 'dor de cabeça', 'dor muscular'},
        'description': 'Infecção respiratória viral causada pelo SARS-CoV-2.',
        'base_probability': 0.4
    },
    'Amigdalite': {
        'symptoms': {'dor de garganta', 'febre', 'dificuldade para engolir', 'gânglios inchados', 'dor de cabeça'},
        'description': 'Inflamação das amígdalas, geralmente por infecção viral ou bacteriana.',
        'base_probability': 0.6
    },
    'Gastrite': {
        'symptoms': {'dor abdominal', 'náusea', 'vômito', 'sensação de inchaço', 'azia'},
        'description': 'Inflamação do revestimento do estômago.',
        'base_probability': 0.7
    },
    'Dengue': {
        'symptoms': {'febre', 'dor de cabeça', 'dor muscular', 'dores nas articulações', 'manchas vermelhas na pele', 'náusea'},
        'description': 'Doença viral transmitida pelo mosquito Aedes aegypti.',
        'base_probability': 0.5
    },
    'Resfriado Comum': {
        'symptoms': {'coriza', 'espirros', 'tosse', 'dor de garganta'},
        'description': 'Infecção viral leve do nariz e da garganta.',
        'base_probability': 0.8
    },
    'Sinusite': {
        'symptoms': {'dor de cabeça', 'congestão nasal', 'pressão facial', 'coriza', 'tosse'},
        'description': 'Inflamação dos seios nasais, que pode ser causada por infecção ou alergia.',
        'base_probability': 0.6
    }
}
all_symptoms = sorted(list(set(symptom for disease in disease_database.values() for symptom in disease['symptoms'])))
doctors_data = pd.DataFrame([
    {'id': 1, 'name': 'Ana Silva', 'specialty': 'Clínico Geral', 'appointment_type': 'online'},
    {'id': 2, 'name': 'Carlos Mendes', 'specialty': 'Cardiologia', 'appointment_type': 'presencial'},
    {'id': 3, 'name': 'Mariana Costa', 'specialty': 'Ortopedia', 'appointment_type': 'online'}
])

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
if 'appointments' not in st.session_state:
    st.session_state.appointments = []

# --- LÓGICA DE DIAGNÓSTICO ---
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

# --- PÁGINAS DO APP ---
def diagnosis_page():
    st.title("🔍 Diagnóstico de Sintomas")
    st.markdown("Selecione os sintomas que você está sentindo para receber uma análise preliminar.")
    st.session_state.user_symptoms = st.multiselect("Selecione seus sintomas:", options=all_symptoms, default=st.session_state.user_symptoms)
    if st.button("Analisar Sintomas", disabled=not st.session_state.user_symptoms, type="primary"):
        st.session_state.is_loading = True
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
        for condition in results.get('possible_conditions', []):
            with st.container(border=True):
                st.subheader(f"{condition['name']} - Probabilidade: {int(condition['probability'] * 100)}%")
                st.progress(condition['probability'])
                st.write(f"*{condition['description']}*")
                if 'matching_symptoms' in condition and condition['matching_symptoms']:
                    st.write(f"**Sintomas correspondentes:** {', '.join(condition['matching_symptoms'])}")
        st.subheader("Recomendações")
        for rec in results.get('recommendations', []):
            st.warning(rec) if "ATENÇÃO" in rec else st.success(rec)
        st.divider()
        st.caption("Aviso: Este diagnóstico não substitui a avaliação de um profissional de saúde.")

def appointments_page():
    st.title("📅 Agendamento de Consultas")
    tab1, tab2 = st.tabs(["**Minhas Consultas**", "**Agendar Nova**"])
    with tab1:
        st.subheader("Consultas Agendadas")
        if not st.session_state.appointments:
            st.info("Nenhuma consulta agendada.")
        for app in st.session_state.appointments:
            with st.container(border=True):
                st.markdown(f"**Médico(a):** Dr(a). {app['doctor']} ({app['specialty']})")
                st.markdown(f"**Data:** {app['date']} às {app['time']} | **Tipo:** {app['type'].capitalize()}")
    with tab2:
        st.subheader("Encontre um Médico")
        for _, doctor in doctors_data.iterrows():
            with st.container(border=True):
                st.subheader(f"Dr(a). {doctor['name']} - {doctor['specialty']}")
                if st.button("Agendar Agora", key=f"schedule_{doctor['id']}"):
                    new_appointment = {
                        'doctor': doctor['name'], 'specialty': doctor['specialty'],
                        'date': (datetime.now() + pd.Timedelta(days=1)).strftime('%d/%m/%Y'), 'time': '10:00',
                        'type': doctor['appointment_type']
                    }
                    st.session_state.appointments.append(new_appointment)
                    st.success(f"Consulta com Dr(a). {doctor['name']} agendada!")
                    time.sleep(1)
                    st.rerun()

# --- NAVEGAÇÃO E EXECUÇÃO ---
def main():
    with st.sidebar:
        st.session_state.current_page = option_menu(
            "MediAssist Menu", ["Diagnóstico", "Agendamentos"],
            icons=['search-heart', 'calendar-check'], menu_icon="menu-button-wide",
            default_index=0, styles={"nav-link-selected": {"background-color": "#0d6efd"}}
        )
    if st.session_state.current_page == "Diagnóstico":
        diagnosis_page()
    elif st.session_state.current_page == "Agendamentos":
        appointments_page()

if __name__ == "__main__":
    main()
