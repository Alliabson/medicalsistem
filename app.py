import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import time
import requests
from datetime import datetime
import urllib.parse

# --- DADOS E LÓGICA ---
disease_database = {
    'COVID-19': {'symptoms': {'febre', 'tosse', 'cansaço', 'perda de paladar ou olfato', 'dificuldade respiratória', 'dor de cabeça', 'dor muscular'}, 'description': 'Infecção respiratória viral causada pelo SARS-CoV-2.', 'base_probability': 0.4},
    'Amigdalite': {'symptoms': {'dor de garganta', 'febre', 'dificuldade para engolir', 'gânglios inchados', 'dor de cabeça'}, 'description': 'Inflamação das amígdalas, geralmente por infecção viral ou bacteriana.', 'base_probability': 0.6},
    'Gastrite': {'symptoms': {'dor abdominal', 'náusea', 'vômito', 'sensação de inchaço', 'azia'}, 'description': 'Inflamação do revestimento do estômago.', 'base_probability': 0.7},
    'Dengue': {'symptoms': {'febre', 'dor de cabeça', 'dor muscular', 'dores nas articulações', 'manchas vermelhas na pele', 'náusea'}, 'description': 'Doença viral transmitida pelo mosquito Aedes aegypti.', 'base_probability': 0.5},
    'Resfriado Comum': {'symptoms': {'coriza', 'espirros', 'tosse', 'dor de garganta'}, 'description': 'Infecção viral leve do nariz e da garganta.', 'base_probability': 0.8},
    'Sinusite': {'symptoms': {'dor de cabeça', 'congestão nasal', 'pressão facial', 'coriza', 'tosse'}, 'description': 'Inflamação dos seios nasais, que pode ser causada por infecção ou alergia.', 'base_probability': 0.6}
}

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
ufs_brasil = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']

# --- CONFIGURAÇÃO DA PÁGINA E ESTADO ---
st.set_page_config(page_title="MediAssist", page_icon="🏥", layout="wide")

if 'diagnosis_results' not in st.session_state:
    st.session_state.diagnosis_results = None
if 'health_units' not in st.session_state:
    st.session_state.health_units = None

# --- FUNÇÕES DE API E LÓGICA ---
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
                'name': disease,
                'probability': round(min(probability, 0.95), 2),
                'description': data['description'],
                'matching_symptoms': list(matching_symptoms)
            })
    
    if not possible_conditions and symptoms:
        possible_conditions.append({
            'name': 'Condição Não Especificada',
            'probability': 0.2,
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
    
    return {
        'possible_conditions': possible_conditions,
        'recommendations': list(recommendations),
        'analyzed_symptoms': symptoms
    }

def get_health_units(uf, city, specialty=None):
    if not uf or not city:
        return None
    try:
        url = f"https://apidadosabertos.saude.gov.br/cnes/estabelecimentos?municipio={urllib.parse.quote(city)}&uf={uf}"
        if specialty:
            url += f"&descricao_tipo_unidade={urllib.parse.quote(specialty)}"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        units = response.json().get('estabelecimentos', [])
        
        return [unit for unit in units if unit.get('noFantasia') and unit.get('noLogradouro')]
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao buscar unidades de saúde: {str(e)}")
        return []

# --- PÁGINAS DO APP ---
def diagnosis_page():
    st.title("🔍 Diagnóstico de Sintomas")
    st.markdown("Selecione os sintomas que você está sentindo para receber uma análise preliminar.")
    
    user_symptoms = st.multiselect("Selecione seus sintomas:", options=all_symptoms)
    
    if st.button("Analisar Sintomas", disabled=not user_symptoms, type="primary"):
        with st.spinner("Analisando..."):
            time.sleep(1)
            st.session_state.diagnosis_results = generate_diagnosis(user_symptoms)
            st.session_state.health_units = None
    
    if st.session_state.diagnosis_results:
        results = st.session_state.diagnosis_results
        st.divider()
        st.subheader("Resultados da Análise")
        
        for condition in results.get('possible_conditions', []):
            with st.container(border=True):
                st.subheader(f"{condition['name']} - Probabilidade: {int(condition['probability'] * 100)}%")
                st.progress(condition['probability'])
                st.write(f"*{condition['description']}*")
                st.write("**Sintomas correspondentes:** " + ", ".join(condition['matching_symptoms']))
        
        st.divider()
        st.subheader("🚀 O que fazer agora?")
        
        if results.get('possible_conditions'):
            top_condition = results['possible_conditions'][0]['name']
            recommended_specialty = condition_to_specialty.get(top_condition, 'Clínico Geral')
            
            st.markdown(f"##### Opção 1: Encontre um especialista para Telemedicina")
            
            col1, col2 = st.columns(2)
            with col1:
                uf_telemed = st.selectbox("Estado (UF)", ufs_brasil, key="telemed_uf")
            with col2:
                city_telemed = st.text_input("Cidade", key="telemed_city")
            
            if st.button(f"Buscar {recommended_specialty}s Online"):
                if city_telemed:
                    query_text = urllib.parse.quote_plus(f"{recommended_specialty} telemedicina {city_telemed} {uf_telemed}")
                    google_search_url = f"https://www.google.com/search?q={query_text}"
                    st.link_button(f"Ver {recommended_specialty}s em {city_telemed}-{uf_telemed}", google_search_url, use_container_width=True)
                else:
                    st.warning("Por favor, informe sua cidade para uma busca mais precisa.")
            
            st.caption("Esta busca direcionada mostrará profissionais disponíveis em sua região.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.expander("Opção 2: Encontre uma unidade de saúde na sua cidade"):
            col1, col2 = st.columns(2)
            with col1:
                uf_selected = st.selectbox("Selecione seu Estado (UF)", ufs_brasil, key="unit_uf")
            with col2:
                city_input = st.text_input("Digite o nome da sua Cidade", key="unit_city")
            
            if st.button("Buscar Unidades de Saúde Locais"):
                if city_input:
                    specialty_filter = recommended_specialty if 'recommended_specialty' in locals() else None
                    st.session_state.health_units = get_health_units(uf_selected, city_input, specialty_filter)
                else:
                    st.warning("Por favor, informe sua cidade para buscar unidades de saúde.")
            
            if st.session_state.health_units is not None:
                if not st.session_state.health_units:
                    st.warning("Nenhuma unidade de saúde encontrada com os critérios atuais.")
                else:
                    st.success(f"{len(st.session_state.health_units)} unidades encontradas:")
                    
                    for unit in st.session_state.health_units[:5]:
                        with st.container(border=True):
                            st.subheader(unit.get('noFantasia', 'Unidade de Saúde'))
                            
                            endereco = [
                                unit.get('noLogradouro', ''),
                                unit.get('nuEndereco', ''),
                                unit.get('noBairro', ''),
                                unit.get('noMunicipio', ''),
                                unit.get('uf', '')
                            ]
                            endereco = ', '.join(filter(None, endereco))
                            
                            st.write(f"**Endereço:** {endereco}")
                            st.write(f"**Tipo:** {unit.get('dsTipoUnidade', 'Não especificado')}")
                            
                            if unit.get('telefone'):
                                st.write(f"**Telefone:** {unit.get('telefone')}")
        
        st.divider()
        st.subheader("Recomendações Gerais de Saúde")
        for rec in results.get('recommendations', []):
            if "ATENÇÃO" in rec:
                st.error(f"⚠️ {rec}")
            else:
                st.success(f"✅ {rec}")

def info_page():
    st.title("ℹ️ Sobre o MediAssist")
    st.markdown("""
    O **MediAssist** é uma ferramenta de triagem inicial de saúde que ajuda a:
    - Identificar possíveis condições médicas com base nos sintomas
    - Recomendar especialistas apropriados
    - Localizar unidades de saúde próximas
    
    ### Aviso Importante:
    Este sistema não substitui uma consulta médica profissional. 
    Sempre consulte um médico para diagnóstico e tratamento adequados.
    """)

# --- NAVEGAÇÃO E EXECUÇÃO ---
def main():
    with st.sidebar:
        page = option_menu(
            "MediAssist Menu", ["Diagnóstico", "Sobre"],
            icons=['search-heart', 'info-circle-fill'], menu_icon="menu-button-wide",
            default_index=0, styles={"nav-link-selected": {"background-color": "#0d6efd"}}
        )
    if page == "Diagnóstico":
        diagnosis_page()
    elif page == "Sobre":
        info_page()

if __name__ == "__main__":
    main()
