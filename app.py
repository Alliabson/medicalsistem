import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import time
import requests
from datetime import datetime

# --- CONFIGURAÇÃO INICIAL E DADOS (Integrado de utils/data.py) ---

# Base de conhecimento de doenças
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

# Gera a lista de sintomas disponíveis a partir da base de dados
all_symptoms = set()
for disease in disease_database.values():
    all_symptoms.update(disease['symptoms'])
available_symptoms = sorted(list(all_symptoms))

# Dados Mock para outras partes do app
doctors_data = pd.DataFrame([
    {'id': 1, 'name': 'Ana Silva', 'specialty': 'Clínico Geral', 'appointment_type': 'online', 'next_availability': 'Hoje, 14:30'},
    {'id': 2, 'name': 'Carlos Mendes', 'specialty': 'Cardiologia', 'appointment_type': 'presencial', 'next_availability': 'Amanhã, 10:00'},
    {'id': 3, 'name': 'Mariana Costa', 'specialty': 'Ortopedia', 'appointment_type': 'online', 'next_availability': 'Quarta-feira, 09:00'}
])

# --- CONFIGURAÇÃO DA PÁGINA E ESTILO ---

st.set_page_config(
    page_title="MediAssist - Telemedicina",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="auto"
)

# CSS personalizado (Integrado de assets/styles.css)
def load_css():
    css_styles = """
    /* Melhora a aparência dos botões */
    .stButton>button {
        border-radius: 10px;
        border: 2px solid #0d6efd;
        color: #0d6efd;
        background-color: transparent;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        border-color: #0b5ed7;
        color: white;
        background-color: #0b5ed7;
    }
    .stButton>button[kind="primary"] {
        background-color: #0d6efd;
        color: white;
    }
    /* Estilo para containers */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] > div > [data-testid="stVerticalBlock"] > [data-testid="stExpander"] {
        border: 1px solid #e6e6e6;
        border-radius: 10px;
    }
    """
    st.markdown(f"<style>{css_styles}</style>", unsafe_allow_html=True)

load_css()

# --- ESTADO DA SESSÃO ---

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'diagnosis' # Inicia no diagnóstico
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
                'name': disease,
                'probability': round(min(probability, 0.95), 2),
                'description': data['description'],
                'matching_symptoms': list(matching_symptoms)
            })
    
    if not possible_conditions and symptoms:
        possible_conditions.append({
            'name': 'Condição Não Especificada',
            'probability': 0.2,
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

    return {
        'possible_conditions': possible_conditions,
        'recommendations': list(recommendations),
        'analyzed_symptoms': symptoms
    }

# --- PÁGINAS DO APLICATIVO ---

def diagnosis_page():
    st.title("🔍 Diagnóstico de Sintomas")
    st.markdown("Selecione os sintomas que você está sentindo para receber uma análise preliminar.")

    st.session_state.user_symptoms = st.multiselect(
        "Selecione seus sintomas:",
        options=available_symptoms,
        default=st.session_state.user_symptoms,
        help="Você pode selecionar múltiplos sintomas."
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

def appointments_page():
    st.title("📅 Agendamento de Consultas")
    
    tab1, tab2 = st.tabs(["**Próximas Consultas**", "**Agendar Nova Consulta**"])
    
    with tab1:
        st.subheader("Suas Consultas Agendadas")
        if not st.session_state.appointments_data:
            st.info("Você ainda não possui nenhuma consulta agendada.")
        else:
            for app in st.session_state.appointments_data:
                with st.container(border=True):
                    st.markdown(f"**Médico(a):** Dr(a). {app['doctor']} ({app['specialty']})")
                    st.markdown(f"**Data:** {app['date']} às {app['time']}")
                    st.markdown(f"**Tipo:** {app['type'].capitalize()}")

    with tab2:
        st.subheader("Encontre um Médico")
        for _, doctor in doctors_data.iterrows():
            with st.container(border=True):
                cols = st.columns([4, 2])
                with cols[0]:
                    st.subheader(f"Dr(a). {doctor['name']}")
                    st.caption(f"**Especialidade:** {doctor['specialty']} | **Tipo:** {doctor['appointment_type'].capitalize()}")
                    st.write(f"**Próxima disponibilidade:** {doctor['next_availability']}")
                with cols[1]:
                    st.write("") # Espaçamento
                    st.write("") # Espaçamento
                    if st.button("Agendar", key=f"schedule_{doctor['id']}"):
                        new_appointment = {
                            'doctor': doctor['name'],
                            'specialty': doctor['specialty'],
                            'date': '20/06/2025', # Data de exemplo
                            'time': '10:00', # Hora de exemplo
                            'type': doctor['appointment_type']
                        }
                        st.session_state.appointments_data.append(new_appointment)
                        st.success(f"Consulta com Dr(a). {doctor['name']} agendada com sucesso!")
                        time.sleep(2)
                        st.rerun()

# --- NAVEGAÇÃO PRINCIPAL E EXECUÇÃO ---

def main():
    with st.sidebar:
        st.markdown("## 🏥 MediAssist")
        selected = option_menu(
            menu_title="Menu Principal",
            options=["Diagnóstico", "Agendamentos"],
            icons=["search-heart", "calendar-check"],
            menu_icon="cast",
            default_index=0,
        )
        st.session_state.current_page = selected

    page = st.session_state.current_page
    if page == "Diagnóstico":
        diagnosis_page()
    elif page == "Agendamentos":
        appointments_page()

if __name__ == "__main__":
    main()
