import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import time
import requests
from datetime import datetime
from utils.data import (
    available_symptoms,
    mock_diagnosis_results,
    doctors_data,
    medical_history,
    appointments_data
)
from utils.helpers import (
    display_symptom_selector,
    display_diagnosis_results,
    display_appointments,
    display_medical_history,
    display_profile
)

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

# Funções para API de Dados Abertos
def get_health_units(uf=None, city=None):
    """Busca unidades de saúde na API do Ministério da Saúde"""
    try:
        url = "https://apidadosabertos.saude.gov.br/cnes/estabelecimentos"
        params = {}
        if uf and uf != 'Todos':
            params['uf'] = uf
        if city:
            params['municipio'] = city
            
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json().get('estabelecimentos', [])
    except Exception as e:
        st.error(f"Erro ao buscar unidades de saúde: {str(e)}")
        return []

def get_epidemiological_data(disease='covid'):
    """Busca dados epidemiológicos"""
    try:
        url = f"https://apidadosabertos.saude.gov.br/{disease}/casos"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erro ao buscar dados epidemiológicos: {str(e)}")
        return None

def generate_diagnosis(symptoms, uf=None):
    """Gera diagnóstico baseado em sintomas e dados epidemiológicos da região"""
    try:
        # Busca dados epidemiológicos regionais
        epi_data = get_epidemiological_data()
        regional_cases = 0
        
        if epi_data and 'casos' in epi_data:
            if uf:
                regional_cases = sum([c['casos'] for c in epi_data['casos'] if c.get('uf') == uf])
            else:
                regional_cases = sum([c['casos'] for c in epi_data['casos']])
        
        # Lógica de diagnóstico adaptada
        conditions = []
        
        # COVID-19 (prioriza se houver muitos casos na região)
        if regional_cases > 1000 and any(sym in symptoms for sym in ['febre', 'tosse', 'dificuldade respiratória']):
            prob = min(0.3 + (regional_cases / 10000), 0.9)
            conditions.append({
                'name': 'COVID-19',
                'probability': round(prob, 2),
                'description': f"Infecção respiratória viral ({regional_cases} casos recentes na região)"
            })
        
        # Outras condições baseadas em sintomas
        if 'febre' in symptoms and 'dor de garganta' in symptoms:
            conditions.append({
                'name': 'Amigdalite',
                'probability': 0.65,
                'description': 'Inflamação das amígdalas'
            })
            
        if 'dor abdominal' in symptoms and 'náusea' in symptoms:
            conditions.append({
                'name': 'Gastrite',
                'probability': 0.7,
                'description': 'Inflamação do revestimento do estômago'
            })
        
        if not conditions:
            conditions.append({
                'name': 'Resfriado Comum',
                'probability': 0.5,
                'description': 'Infecção viral leve do trato respiratório'
            })
        
        # Ordena por probabilidade
        conditions.sort(key=lambda x: x['probability'], reverse=True)
        
        # Recomendações baseadas na gravidade
        recommendations = [
            'Hidrate-se adequadamente',
            'Descanse o suficiente'
        ]
        
        if any(c['probability'] > 0.7 for c in conditions):
            recommendations.append('Consulte uma unidade de saúde para avaliação')
        if 'dificuldade respiratória' in symptoms:
            recommendations.append('Procure atendimento urgente se piorar')
        
        return {
            'possible_conditions': conditions,
            'recommendations': recommendations,
            'analyzed_symptoms': symptoms,
            'regional_data': f"Dados regionais: {regional_cases} casos recentes" if regional_cases else ""
        }
        
    except Exception as e:
        st.error(f"Erro ao gerar diagnóstico: {str(e)}")
        return None

# Navegação principal
def main_navigation():
    with st.sidebar:
        selected = option_menu(
            menu_title="Menu Principal",
            options=["Início", "Diagnóstico", "Unidades de Saúde", "Dados Epidemiológicos", "Consultas", "Histórico", "Perfil"],
            icons=["house", "search-heart", "hospital", "activity", "calendar-check", "clock-history", "person"],
            menu_icon="menu-button-wide",
            default_index=0,
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
        elif selected == "Unidades de Saúde":
            st.session_state.current_page = 'health_units'
        elif selected == "Dados Epidemiológicos":
            st.session_state.current_page = 'epi_data'
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
    
    cols = st.columns(2)
    with cols[0]:
        with st.container(border=True, height=200):
            st.markdown("🔍 **Diagnóstico de Sintomas**")
            st.markdown("Identifique possíveis condições médicas")
            if st.button("Acessar Diagnóstico", key="diagnosis_btn"):
                st.session_state.current_page = 'diagnosis'
    
    with cols[1]:
        with st.container(border=True, height=200):
            st.markdown("🏥 **Unidades de Saúde**")
            st.markdown("Encontre hospitais e UBS próximos")
            if st.button("Buscar Unidades", key="units_btn"):
                st.session_state.current_page = 'health_units'
    
    cols = st.columns(2)
    with cols[0]:
        with st.container(border=True, height=200):
            st.markdown("📊 **Dados Epidemiológicos**")
            st.markdown("Casos de doenças na sua região")
            if st.button("Ver Dados", key="epi_btn"):
                st.session_state.current_page = 'epi_data'
    
    with cols[1]:
        with st.container(border=True, height=200):
            st.markdown("📅 **Agendar Consultas**")
            st.markdown("Marque consultas com especialistas")
            if st.button("Ver Consultas", key="appointments_btn"):
                st.session_state.current_page = 'appointments'

def diagnosis_page():
    st.title("🔍 Diagnóstico de Sintomas")
    
    display_symptom_selector()
    
    with st.expander("Informações adicionais para diagnóstico preciso"):
        age = st.number_input("Idade", min_value=0, max_value=120, value=30)
        uf = st.selectbox("UF (opcional)", ['Não informar'] + sorted([
            'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO',
            'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI',
            'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
        ]))
    
    if st.button("Analisar Sintomas", 
                disabled=len(st.session_state.user_symptoms) == 0,
                type="primary"):
        st.session_state.is_loading = True
        st.rerun()
    
    if st.session_state.is_loading:
        with st.status("Analisando sintomas...", expanded=True) as status:
            st.write("Consultando dados de saúde pública...")
            
            # Usa a função com a API do governo
            st.session_state.diagnosis_results = generate_diagnosis(
                st.session_state.user_symptoms,
                uf if uf != 'Não informar' else None
            )
            
            if not st.session_state.diagnosis_results:
                st.session_state.diagnosis_results = mock_diagnosis_results(st.session_state.user_symptoms)
                st.warning("Usando dados simulados devido a problema na API")
            
            st.session_state.is_loading = False
            status.update(label="Análise concluída!", state="complete", expanded=False)
        st.rerun()
    
    if st.session_state.diagnosis_results:
        display_diagnosis_results()

def health_units_page():
    st.title("🏥 Unidades de Saúde Próximas")
    
    col1, col2 = st.columns(2)
    with col1:
        uf = st.selectbox("Selecione seu estado:", 
                         ['Todos'] + sorted([
                             'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO',
                             'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI',
                             'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
                         ]))
    with col2:
        city = st.text_input("Ou digite seu município:")
    
    if st.button("Buscar Unidades de Saúde"):
        with st.spinner("Buscando unidades..."):
            units = get_health_units(uf if uf != 'Todos' else None, city if city else None)
            
            if units:
                st.subheader(f"Unidades encontradas: {len(units)}")
                
                for unit in units[:10]:  # Limita a 10 resultados
                    with st.expander(f"🏥 {unit.get('no_fantasia', 'Unidade de Saúde')}"):
                        cols = st.columns(2)
                        with cols[0]:
                            st.write(f"**Endereço:** {unit.get('no_logradouro', 'N/A')}, {unit.get('nu_numero', 'N/A')}")
                            st.write(f"**Bairro:** {unit.get('no_bairro', 'N/A')}")
                            st.write(f"**Município:** {unit.get('no_municipio', 'N/A')} - {unit.get('uf', 'N/A')}")
                        with cols[1]:
                            st.write(f"**Tipo:** {unit.get('ds_tipo_unidade', 'N/A')}")
                            st.write(f"**Telefone:** {unit.get('nu_telefone', 'N/A')}")
                            st.write(f"**Atendimento SUS:** {'Sim' if unit.get('co_atu_sus', 0) == 1 else 'Não'}")
            else:
                st.warning("Nenhuma unidade encontrada com os critérios informados")

def epidemiological_data_page():
    st.title("📊 Dados Epidemiológicos")
    
    disease = st.selectbox("Selecione a doença:", 
                          ['COVID-19', 'Dengue', 'Influenza', 'Zika'])
    uf = st.selectbox("Filtrar por UF:", 
                      ['Todas'] + sorted([
                          'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO',
                          'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI',
                          'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
                      ]))
    
    if st.button("Buscar Dados Atualizados"):
        with st.spinner("Obtendo dados oficiais..."):
            data = get_epidemiological_data(disease.lower())
            
            if data and 'casos' in data:
                df = pd.DataFrame(data['casos'])
                
                if uf != 'Todas':
                    df = df[df['uf'] == uf]
                
                if not df.empty:
                    st.subheader(f"Casos de {disease} em {uf if uf != 'Todas' else 'todo Brasil'}")
                    
                    cols = st.columns(2)
                    with cols[0]:
                        st.dataframe(df.head(10))
                    with cols[1]:
                        if 'data' in df.columns:
                            df['data'] = pd.to_datetime(df['data'])
                            df = df.sort_values('data')
                            st.line_chart(df.set_index('data')['casos'])
                    
                    st.download_button(
                        "Baixar dados completos",
                        df.to_csv(index=False).encode('utf-8'),
                        f"dados_{disease.lower()}_{uf if uf != 'Todas' else 'brasil'}.csv",
                        "text/csv"
                    )
                else:
                    st.info("Nenhum caso registrado para os filtros selecionados")
            else:
                st.error("Não foi possível obter os dados. Tente novamente mais tarde.")

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
                
                date = st.date_input("Data da consulta", min_value=datetime.now())
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

def main():
    main_navigation()
    
    if st.session_state.current_page == 'home':
        home_page()
    elif st.session_state.current_page == 'diagnosis':
        diagnosis_page()
    elif st.session_state.current_page == 'health_units':
        health_units_page()
    elif st.session_state.current_page == 'epi_data':
        epidemiological_data_page()
    elif st.session_state.current_page == 'appointments':
        appointments_page()
    elif st.session_state.current_page == 'history':
        history_page()
    elif st.session_state.current_page == 'profile':
        profile_page()

if __name__ == "__main__":
    main()
