import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import time
from dotenv import load_dotenv
import os
from utils.data import get_real_diagnosis
from utils.data import (
    available_symptoms,
    mock_diagnosis_results,
    doctors_data,
    medical_history,
    appointments_data
)
from utils.helpers import (
    display_symptom_selector,  # Nome corrigido
    display_diagnosis_results,
    display_appointments,
    display_medical_history,
    display_profile
)

# Carrega variáveis de ambiente
load_dotenv()

# Configurações da API Infermedica
INFERMEDICA_APP_ID = os.getenv('INFERMEDICA_APP_ID', 'sua_app_id')
INFERMEDICA_APP_KEY = os.getenv('INFERMEDICA_APP_KEY', 'sua_app_key')

# Configuração da página
st.set_page_config(
    page_title="MediAssist - Telemedicina",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="auto"
)

# CSS personalizado
def load_css():
    with open("assets/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Estado da sessão
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'
if 'user_symptoms' not in st.session_state:
    st.session_state.user_symptoms = []
if 'diagnosis_results' not in st.session_state:
    st.session_state.diagnosis_results = None
if 'is_loading' not in st.session_state:
    st.session_state.is_loading = False

# Navegação principal
def main_navigation():
    with st.sidebar:
        selected = option_menu(
            menu_title="Menu Principal",
            options=["Início", "Diagnóstico", "Consultas", "Histórico", "Perfil"],
            icons=["house", "search-heart", "calendar-check", "clock-history", "person"],
            menu_icon="menu-button-wide",
            default_index=["Início", "Diagnóstico", "Consultas", "Histórico", "Perfil"].index(
                "Início" if st.session_state.current_page == 'home' 
                else 'Diagnóstico' if st.session_state.current_page == 'diagnosis'
                else 'Consultas' if st.session_state.current_page == 'appointments'
                else 'Histórico' if st.session_state.current_page == 'history'
                else 'Perfil'
            ),
            styles={
                "container": {"padding": "0!important", "background-color": "#f8f9fa"},
                "icon": {"color": "orange", "font-size": "18px"}, 
                "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
                "nav-link-selected": {"background-color": "#0d6efd"},
            }
        )
        
        if selected == "Início":
            st.session_state.current_page = 'home'
        elif selected == "Diagnóstico":
            st.session_state.current_page = 'diagnosis'
        elif selected == "Consultas":
            st.session_state.current_page = 'appointments'
        elif selected == "Histórico":
            st.session_state.current_page = 'history'
        elif selected == "Perfil":
            st.session_state.current_page = 'profile'

# Páginas do aplicativo
def home_page():
    st.title("🏥 MediAssist")
    st.markdown("Bem-vindo ao seu assistente de telemedicina pessoal")
    
    # Cartões de funcionalidades
    cols = st.columns(2)
    with cols[0]:
        with st.container(border=True, height=200):
            st.markdown("🔍 **Diagnóstico de Sintomas**")
            st.markdown("Identifique possíveis condições médicas com base nos seus sintomas")
            if st.button("Acessar Diagnóstico", key="diagnosis_btn"):
                st.session_state.current_page = 'diagnosis'
    
    with cols[1]:
        with st.container(border=True, height=200):
            st.markdown("📅 **Agendar Consultas**")
            st.markdown("Marque consultas com nossos especialistas")
            if st.button("Ver Consultas", key="appointments_btn"):
                st.session_state.current_page = 'appointments'
    
    cols = st.columns(2)
    with cols[0]:
        with st.container(border=True, height=200):
            st.markdown("⏳ **Histórico Médico**")
            st.markdown("Acesse seu histórico de diagnósticos e consultas")
            if st.button("Ver Histórico", key="history_btn"):
                st.session_state.current_page = 'history'
    
    with cols[1]:
        with st.container(border=True, height=200):
            st.markdown("👤 **Perfil do Paciente**")
            st.markdown("Gerencie suas informações pessoais e médicas")
            if st.button("Acessar Perfil", key="profile_btn"):
                st.session_state.current_page = 'profile'
    
    # Acesso rápido
    st.subheader("Acesso Rápido")
    with st.expander("Verificar sintomas"):
        st.write("Selecione seus sintomas para uma avaliação preliminar")
    
    with st.expander("Consultar resultados de exames"):
        st.write("Acesse seus exames laboratoriais e de imagem")
    
    with st.expander("Monitorar sinais vitais"):
        st.write("Registre e acompanhe seus sinais vitais ao longo do tempo")

def diagnosis_page():
    st.title("🔍 Diagnóstico de Sintomas")
    
    # Seletor de sintomas
    display_symptom_selector()
    
    # Informações adicionais para diagnóstico preciso
    with st.expander("Informações adicionais para diagnóstico preciso"):
        age = st.number_input("Idade", min_value=0, max_value=120, value=30)
        sex = st.radio("Sexo biológico", ["male", "female"], format_func=lambda x: "Masculino" if x == "male" else "Feminino")
    
    # Botão de análise
    if st.button("Analisar Sintomas", 
                disabled=len(st.session_state.user_symptoms) == 0,
                type="primary",
                use_container_width=True):
        st.session_state.is_loading = True
        
        # Usar API real se disponível, senão usar mock
        if INFERMEDICA_APP_ID != 'sua_app_id':
            diagnosis_data = get_real_diagnosis(st.session_state.user_symptoms, age, sex)
            if diagnosis_data:
                st.session_state.diagnosis_results = process_infermedica_response(diagnosis_data)
            else:
                st.session_state.diagnosis_results = mock_diagnosis_results(st.session_state.user_symptoms)
                st.warning("Usando dados simulados devido a erro na API")
        else:
            st.session_state.diagnosis_results = mock_diagnosis_results(st.session_state.user_symptoms)
            st.info("Usando dados simulados. Configure as credenciais da API para diagnóstico real.")
        
        st.session_state.is_loading = False
        st.rerun()
    
    # Simulação de carregamento
    if st.session_state.is_loading:
        with st.status("Analisando sintomas...", expanded=True) as status:
            st.write("Consultando base de dados médicos...")
            time.sleep(2)
            st.write("Comparando com casos similares...")
            time.sleep(1)
            st.write("Gerando possíveis diagnósticos...")
            time.sleep(1)
            st.session_state.diagnosis_results = mock_diagnosis_results(st.session_state.user_symptoms)
            st.session_state.is_loading = False
            status.update(label="Análise concluída!", state="complete", expanded=False)
        st.rerun()
    
    # Exibir resultados
    if st.session_state.diagnosis_results:
        display_diagnosis_results()

def appointments_page():
    st.title("📅 Consultas Médicas")
    
    # Abas para diferentes visualizações
    tab1, tab2 = st.tabs(["Próximas Consultas", "Agendar Nova Consulta"])
    
    with tab1:
        display_appointments()
    
    with tab2:
        st.subheader("Médicos Disponíveis")
        
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            specialty = st.selectbox("Especialidade", 
                                   ["Todos", "Clínico Geral", "Cardiologia", "Ortopedia", "Pediatria"])
        with col2:
            appointment_type = st.selectbox("Tipo de Consulta", 
                                          ["Todos", "Presencial", "Online"])
        
        # Lista de médicos
        filtered_doctors = doctors_data.copy()
        if specialty != "Todos":
            filtered_doctors = filtered_doctors[filtered_doctors['specialty'] == specialty]
        if appointment_type != "Todos":
            filtered_doctors = filtered_doctors[filtered_doctors['appointment_type'] == appointment_type.lower()]
        
        for _, doctor in filtered_doctors.iterrows():
            with st.container(border=True):
                cols = st.columns([1, 4, 2])
                with cols[0]:
                    st.image("assets/icons/user.svg", width=60)
                with cols[1]:
                    st.subheader(f"Dr. {doctor['name']}")
                    st.caption(f"**Especialidade:** {doctor['specialty']}")
                    st.caption(f"**Tipo:** {doctor['appointment_type'].capitalize()}")
                    st.caption(f"**Próxima disponibilidade:** {doctor['next_availability']}")
                with cols[2]:
                    if st.button("Agendar", key=f"schedule_{doctor['id']}"):
                        st.session_state['selected_doctor'] = doctor['id']
                        st.session_state['schedule_step'] = 1
                        st.rerun()
        
        # Formulário de agendamento
        if 'schedule_step' in st.session_state:
            if st.session_state.schedule_step == 1:
                st.subheader("Agendar Consulta")
                selected_doctor = doctors_data[doctors_data['id'] == st.session_state.selected_doctor].iloc[0]
                
                st.write(f"**Médico:** Dr. {selected_doctor['name']}")
                st.write(f"**Especialidade:** {selected_doctor['specialty']}")
                st.write(f"**Tipo:** {selected_doctor['appointment_type'].capitalize()}")
                
                date = st.date_input("Data da consulta", min_value=pd.to_datetime('today'))
                time_options = ["09:00", "10:30", "14:00", "15:30", "17:00"]
                time = st.selectbox("Horário", time_options)
                reason = st.text_area("Motivo da consulta")
                
                if st.button("Confirmar Agendamento"):
                    # Simular confirmação
                    new_appointment = {
                        'id': len(appointments_data) + 1,
                        'doctor': selected_doctor['name'],
                        'specialty': selected_doctor['specialty'],
                        'date': date.strftime('%d/%m/%Y'),
                        'time': time,
                        'type': selected_doctor['appointment_type'],
                        'status': 'Agendada'
                    }
                    appointments_data.append(new_appointment)
                    st.success("Consulta agendada com sucesso!")
                    del st.session_state['schedule_step']
                    del st.session_state['selected_doctor']
                    time.sleep(2)
                    st.rerun()
                
                if st.button("Cancelar", type="secondary"):
                    del st.session_state['schedule_step']
                    del st.session_state['selected_doctor']
                    st.rerun()

def history_page():
    st.title("⏳ Histórico Médico")
    
    tab1, tab2, tab3 = st.tabs(["Diagnósticos", "Consultas", "Exames"])
    
    with tab1:
        display_medical_history('diagnoses')
    
    with tab2:
        display_medical_history('appointments')
    
    with tab3:
        display_medical_history('exams')

def profile_page():
    st.title("👤 Perfil do Paciente")
    display_profile()
def process_infermedica_response(response):
    """Processa a resposta da API Infermedica para o formato do nosso app"""
    conditions = []
    for condition in response.get('conditions', []):
        conditions.append({
            'name': condition['common_name'],
            'probability': condition['probability'],
            'description': condition.get('hint', 'Descrição não disponível')
        })
    
    recommendations = []
    if response.get('should_stop'):
        recommendations.append("Pare de adicionar sintomas e veja as recomendações")
    
    triage_level = response.get('triage_level', 'unknown')
    if triage_level == 'emergency':
        recommendations.append("Procure atendimento de emergência imediatamente")
    elif triage_level == 'acute':
        recommendations.append("Marque uma consulta médica o mais rápido possível")
    
    return {
        'possible_conditions': conditions,
        'recommendations': recommendations,
        'analyzed_symptoms': st.session_state.user_symptoms
    }
# Roteamento de páginas
def main():
    main_navigation()
    
    if st.session_state.current_page == 'home':
        home_page()
    elif st.session_state.current_page == 'diagnosis':
        diagnosis_page()
    elif st.session_state.current_page == 'appointments':
        appointments_page()
    elif st.session_state.current_page == 'history':
        history_page()
    elif st.session_state.current_page == 'profile':
        profile_page()

if __name__ == "__main__":
    main()
