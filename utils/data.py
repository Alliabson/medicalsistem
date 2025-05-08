import pandas as pd
import requests
from datetime import datetime

# Dados básicos
available_symptoms = [
    'febre', 'tosse', 'dor de garganta', 'dificuldade respiratória',
    'cefaleia', 'mialgia', 'coriza', 'náusea', 'vômito', 'diarreia'
]

# Dados mockados para quando as APIs não estiverem disponíveis
doctors_data = pd.DataFrame([
    {'id': 1, 'name': 'Ana Silva', 'specialty': 'Clínico Geral', 'appointment_type': 'online', 'next_availability': 'Hoje, 14:30'},
    {'id': 2, 'name': 'Carlos Mendes', 'specialty': 'Cardiologia', 'appointment_type': 'presencial', 'next_availability': 'Amanhã, 10:00'}
])

appointments_data = []
medical_history = {'diagnoses': [], 'past_appointments': [], 'exams': []}

# Funções para acessar dados abertos
def get_health_establishments(uf='all', municipio=''):
    """Busca estabelecimentos de saúde por UF ou município"""
    try:
        url = "https://apidadosabertos.saude.gov.br/cnes/estabelecimentos"
        params = {}
        if uf != 'all':
            params['uf'] = uf
        if municipio:
            params['municipio'] = municipio
            
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json().get('estabelecimentos', [])
    except Exception as e:
        print(f"Erro ao buscar estabelecimentos: {e}")
        return []

def get_epidemiological_data(disease='covid'):
    """Busca dados epidemiológicos"""
    try:
        url = f"https://apidadosabertos.saude.gov.br/{disease}/casos"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Erro ao buscar dados epidemiológicos: {e}")
        return None

def get_drugs_info(search_term=''):
    """Busca informações sobre medicamentos"""
    try:
        url = "https://apidadosabertos.saude.gov.br/medicamentos"
        params = {'search': search_term} if search_term else {}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json().get('medicamentos', [])
    except Exception as e:
        print(f"Erro ao buscar medicamentos: {e}")
        return []

def mock_diagnosis_results(symptoms):
    """Resultados simulados de diagnóstico"""
    conditions = []
    
    if 'febre' in symptoms and 'tosse' in symptoms:
        conditions.append({
            'name': 'COVID-19', 
            'probability': 0.75,
            'description': 'Infecção respiratória causada pelo vírus SARS-CoV-2'
        })
    
    if 'dor de garganta' in symptoms and 'febre' in symptoms:
        conditions.append({
            'name': 'Amigdalite',
            'probability': 0.65,
            'description': 'Inflamação das amígdalas'
        })
    
    if not conditions:
        conditions.append({
            'name': 'Resfriado Comum',
            'probability': 0.5,
            'description': 'Infecção viral leve do trato respiratório'
        })
    
    return {
        'possible_conditions': conditions,
        'recommendations': [
            'Hidrate-se adequadamente',
            'Descanse o suficiente',
            'Monitore seus sintomas'
        ],
        'analyzed_symptoms': symptoms
    }
