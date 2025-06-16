import pandas as pd

# --- BASE DE CONHECIMENTO DE DOENÇAS ---
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
    {'id': 1, 'name': 'Ana Silva', 'specialty': 'Clínico Geral', 'appointment_type': 'online', 'next_availability': 'Hoje, 16:30'},
    {'id': 2, 'name': 'Carlos Mendes', 'specialty': 'Cardiologia', 'appointment_type': 'presencial', 'next_availability': 'Amanhã, 10:00'},
    {'id': 3, 'name': 'Mariana Costa', 'specialty': 'Ortopedia', 'appointment_type': 'online', 'next_availability': 'Quarta-feira, 09:00'}
])

# Dados de exemplo que serão mantidos na sessão
appointments_data = []
medical_history = {'diagnoses': [], 'past_appointments': [], 'exams': []}
