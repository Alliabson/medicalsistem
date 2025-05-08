def display_diagnosis_results():
    """Exibe os resultados do diagnóstico usando a API Infermedica"""
    results = st.session_state.diagnosis_results
    
    st.subheader("Resultados da Análise")
    st.write(f"**Sintomas analisados:** {', '.join(results['analyzed_symptoms'])}")
    
    st.markdown("---")
    st.subheader("Possíveis Condições")
    
    for condition in results['possible_conditions']:
        with st.expander(f"{condition['name']} ({int(condition['probability']*100)}% de probabilidade)"):
            st.write(condition['description'])
            st.progress(condition['probability'], text=f"Probabilidade: {int(condition['probability']*100)}%")
            
            # Buscar informações de medicamentos relacionados
            if st.button(f"Ver tratamentos para {condition['name']}", key=f"treatment_{condition['name']}"):
                common_drugs = {
                    'Gripe': 'Paracetamol',
                    'COVID-19': 'Ivermectina',
                    'Resfriado Comum': 'Dipirona',
                    'Gastrite': 'Omeprazol',
                    'Asma': 'Salbutamol'
                }
                
                drug_name = common_drugs.get(condition['name'], 'Paracetamol')
                drug_info = get_drug_info(drug_name)
                
                if drug_info:
                    with st.popover(f"Informações sobre {drug_info['name']}"):
                        st.subheader(drug_info['name'])
                        st.markdown("**Indicações:**")
                        st.write(drug_info['indications'][0] if isinstance(drug_info['indications'], list) else drug_info['indications'])
                        
                        st.markdown("**Avisos:**")
                        st.write(drug_info['warnings'][0] if isinstance(drug_info['warnings'], list) else drug_info['warnings'])
                        
                        st.markdown("**Efeitos Colaterais:**")
                        st.write(drug_info['side_effects'][0] if isinstance(drug_info['side_effects'], list) else drug_info['side_effects'])
                else:
                    st.warning(f"Não foi possível encontrar informações sobre {drug_name}")
    
    st.markdown("---")
    st.subheader("Recomendações")
    for rec in results['recommendations']:
        st.markdown(f"- {rec}")
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Agendar Consulta", type="primary", use_container_width=True):
            st.session_state['schedule_after_diagnosis'] = True
            st.session_state.current_page = 'appointments'
            st.rerun()
    with col2:
        if st.button("Salvar no Histórico", type="secondary", use_container_width=True):
            # Salvar no FHIR
            patient_id = "example"  # Substituir por ID real do paciente
            condition_data = {
                'code': {'text': results['possible_conditions'][0]['name']},
                'subject': {'reference': f'Patient/{patient_id}'},
                'evidence': [{'code': {'text': sym}} for sym in results['analyzed_symptoms']],
                'recordedDate': datetime.now().isoformat()
            }
            
            condition_id = save_to_fhir('Condition', condition_data)
            if condition_id:
                st.success("Diagnóstico salvo no seu histórico médico!")
            else:
                st.error("Erro ao salvar no histórico médico")
