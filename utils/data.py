import os
import requests
from fhirpy import SyncFHIRClient
from datetime import datetime

# Configurações das APIs
INFERMEDICA_APP_ID = os.getenv('INFERMEDICA_APP_ID', 'sua_app_id')
INFERMEDICA_APP_KEY = os.getenv('INFERMEDICA_APP_KEY', 'sua_app_key')
INFERMEDICA_URL = 'https://api.infermedica.com/v3/'

FHIR_SERVER_URL = 'https://hapi.fhir.org/baseR4'
OPENFDA_URL = 'https://api.fda.gov/drug/'

# Cliente FHIR
fhir_client = SyncFHIRClient(FHIR_SERVER_URL)

def get_infermedica_headers():
    return {
        'App-Id': INFERMEDICA_APP_ID,
        'App-Key': INFERMEDICA_APP_KEY,
        'Content-Type': 'application/json'
    }

# Função para diagnóstico real usando Infermedica
def get_real_diagnosis(symptoms, age, sex):
    url = f"{INFERMEDICA_URL}diagnosis"
    
    data = {
        "sex": sex,
        "age": {"value": age},
        "evidence": [{"id": sym, "choice_id": "present"} for sym in symptoms]
    }
    
    try:
        response = requests.post(url, json=data, headers=get_infermedica_headers())
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro na API Infermedica: {e}")
        return None

# Função para buscar informações de medicamentos na OpenFDA
def get_drug_info(drug_name):
    url = f"{OPENFDA_URL}label.json?search=openfda.brand_name:{drug_name}&limit=1"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data.get('results'):
            drug = data['results'][0]
            return {
                'name': drug.get('openfda', {}).get('brand_name', [drug_name])[0],
                'indications': drug.get('indications_and_usage', ['Informação não disponível']),
                'warnings': drug.get('warnings', ['Nenhum alerta específico']),
                'side_effects': drug.get('adverse_reactions', ['Nenhum efeito colateral relatado'])
            }
        return None
    except requests.exceptions.RequestException as e:
        print(f"Erro na API OpenFDA: {e}")
        return None

# Função para salvar dados no servidor FHIR
def save_to_fhir(resource_type, data):
    try:
        resource = fhir_client.resource(resource_type, **data)
        resource.save()
        return resource.id
    except Exception as e:
        print(f"Erro ao salvar no FHIR: {e}")
        return None

# Função para buscar histórico médico no FHIR
def get_fhir_history(patient_id):
    try:
        patient = fhir_client.resource('Patient', id=patient_id)
        conditions = fhir_client.resources('Condition').search(subject=f'Patient/{patient_id}').fetch()
        appointments = fhir_client.resources('Appointment').search(actor=f'Patient/{patient_id}').fetch()
        
        return {
            'patient': patient.serialize(),
            'conditions': [c.serialize() for c in conditions],
            'appointments': [a.serialize() for a in appointments]
        }
    except Exception as e:
        print(f"Erro ao buscar no FHIR: {e}")
        return None
