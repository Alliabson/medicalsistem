import streamlit as st
import pandas as pd
from utils.data import medical_history, patient_profile

def display_symptom_selector():
    """Exibe o seletor de sintomas e gerencia os sintomas selecionados"""
    st.subheader("Selecione seus sintomas")
    
    # Sintomas selecionados
    if st.session_state.user_symptoms:
        st.write("**Sintomas selecionados:**")
        cols = st.columns(4)
        for i, symptom in enumerate(st.session_state.user_symptoms):
            with cols[i % 4]:
                st.markdown(
                    f"<div style='border: 1px solid #0d6efd; border-radius: 5px; padding: 5px; margin: 2px; "
                    f"text-align: center; background-color: #e7f1ff;'>"
                    f"{symptom} <span style='color: #0d6efd; cursor: pointer;' "
                    f"onclick='window.streamlitAPI.setComponentValue({{type: \"remove_symptom\", symptom: \"{symptom}\"}})'>×</span>"
                    f"</div>", 
                    unsafe_allow_html=True
                )
    else:
        st.info("Nenhum sintoma selecionado")
    
    # Todos os sintomas disponíveis
    st.write("**Adicionar sintomas:**")
    cols = st.columns(4)
    for i, symptom in enumerate(available_symptoms):
        if symptom not in st.session_state.user_symptoms:
            with cols[i % 4]:
                if st.button(symptom, key=f"symptom_{i}"):
                    if symptom not in st.session_state.user_symptoms:
                        st.session_state.user_symptoms.append(symptom)
                        st.rerun()

def display_diagnosis_results():
    """Exibe os resultados do diagnóstico"""
    results = st.session_state.diagnosis_results
    
    st.subheader("Resultados da Análise")
    st.write(f"**Sintomas analisados:** {', '.join(results['analyzed_symptoms'])}")
    
    st.markdown("---")
    st.subheader("Possíveis Condições")
    
    for condition in results['possible_conditions']:
        with st.expander(f"{condition['name']} ({int(condition['probability']*100)}% de probabilidade)"):
            st.write(condition['description'])
            st.progress(condition['probability'], text=f"Probabilidade: {int(condition['probability']*100)}%")
    
    st.markdown("---")
    st.subheader("Recomendações")
    for rec in results['recommendations']:
        st.markdown(f"- {rec}")
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.button("Agendar Consulta", type="primary", use_container_width=True)
    with col2:
        st.button("Salvar Resultados", type="secondary", use_container_width=True)

def display_appointments():
    """Exibe as consultas agendadas"""
    if not appointments_data:
        st.info("Nenhuma consulta agendada")
        return
    
    for appointment in appointments_data:
        with st.container(border=True):
            cols = st.columns([4, 1])
            with cols[0]:
                st.markdown(f"**Dr. {appointment['doctor']}** ({appointment['specialty']})")
                st.markdown(f"📅 **Data:** {appointment['date']} às {appointment['time']}")
                st.markdown(f"📌 **Tipo:** {appointment['type'].capitalize()}")
                st.markdown(f"🔄 **Status:** {appointment['status']}")
            with cols[1]:
                if st.button("Detalhes", key=f"appt_{appointment['id']}"):
                    st.session_state['view_appointment'] = appointment['id']
                    st.rerun()
    
    if 'view_appointment' in st.session_state:
        appointment = next(a for a in appointments_data if a['id'] == st.session_state.view_appointment)
        with st.expander(f"Detalhes da Consulta com Dr. {appointment['doctor']}", expanded=True):
            st.markdown(f"**Especialidade:** {appointment['specialty']}")
            st.markdown(f"**Data e Hora:** {appointment['date']} às {appointment['time']}")
            st.markdown(f"**Tipo de Consulta:** {appointment['type'].capitalize()}")
            st.markdown(f"**Status:** {appointment['status']}")
            
            if st.button("Cancelar Consulta", type="secondary"):
                # Simular cancelamento
                appointments_data.remove(appointment)
                del st.session_state['view_appointment']
                st.success("Consulta cancelada com sucesso!")
                time.sleep(2)
                st.rerun()
            
            if st.button("Voltar", key="back_appointments"):
                del st.session_state['view_appointment']
                st.rerun()

def display_medical_history(history_type):
    """Exibe o histórico médico baseado no tipo (diagnoses, appointments, exams)"""
    if history_type == 'diagnoses':
        data = medical_history['diagnoses']
        if not data:
            st.info("Nenhum diagnóstico registrado")
            return
        
        for item in data:
            with st.expander(f"{item['condition']} - {item['date']} ({item['probability']}% de probabilidade)"):
                st.markdown(f"**Sintomas:** {item['symptoms']}")
                st.progress(item['probability']/100, text=f"Probabilidade: {item['probability']}%")
    
    elif history_type == 'appointments':
        data = medical_history['past_appointments']
        if not data:
            st.info("Nenhuma consulta passada registrada")
            return
        
        for item in data:
            with st.expander(f"Consulta com Dr. {item['doctor']} - {item['date']}"):
                st.markdown(f"**Especialidade:** {item['specialty']}")
                st.markdown(f"**Tipo:** {item['type']}")
                st.markdown("**Relatório:**")
                st.write(item['report'])
    
    elif history_type == 'exams':
        data = medical_history['exams']
        if not data:
            st.info("Nenhum exame registrado")
            return
        
        for item in data:
            with st.expander(f"{item['type']} - {item['date']}"):
                st.markdown("**Resultados:**")
                st.write(item['results'])

def display_profile():
    """Exibe o perfil do paciente"""
    profile = patient_profile
    
    # Informações básicas
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("assets/icons/user.svg", width=100)
    with col2:
        st.subheader(profile['name'])
        st.markdown(f"**ID:** {profile['id']}")
        st.markdown(f"**Data de Nascimento:** {profile['birth_date']}")
        st.markdown(f"**Gênero:** {profile['gender']}")
    
    st.markdown("---")
    
    # Informações de saúde
    cols = st.columns(2)
    with cols[0]:
        st.subheader("Dados Físicos")
        st.markdown(f"**Tipo Sanguíneo:** {profile['blood_type']}")
        st.markdown(f"**Altura:** {profile['height']}")
        st.markdown(f"**Peso:** {profile['weight']}")
    
    with cols[1]:
        st.subheader("Condições Médicas")
        if profile['conditions']:
            for condition in profile['conditions']:
                st.markdown(f"- **{condition['name']}** (desde {condition['diagnosed']}, {condition['severity']})")
        else:
            st.info("Nenhuma condição médica registrada")
    
    st.markdown("---")
    
    # Alergias
    st.subheader("Alergias")
    if profile['allergies']:
        for allergy in profile['allergies']:
            st.markdown(f"- **{allergy['name']}**: {allergy['reaction']}")
    else:
        st.info("Nenhuma alergia registrada")
    
    # Botão para editar perfil
    st.button("Editar Perfil", type="secondary")
