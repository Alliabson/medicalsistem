import pandas as pd
import random
from datetime import datetime, timedelta

# Sintomas disponíveis
available_symptoms = [
    'tosse', 'febre', 'dor de cabeça', 'náusea', 'fadiga',
    'dor abdominal', 'tontura', 'dor muscular', 'dificuldade respiratória',
    'dor de garganta', 'perda de paladar', 'perda de olfato'
]

# Dados dos médicos
doctors_data = pd.DataFrame([
    {'id': 1, 'name': 'Ana Silva', 'specialty': 'Clínico Geral', 'appointment_type': 'online', 'next_availability': 'Hoje, 14:30'},
    {'id': 2, 'name': 'Carlos Mendes', 'specialty': 'Cardiologia', 'appointment_type': 'presencial', 'next_availability': 'Amanhã, 10:00'},
    {'id': 3, 'name': 'João Pereira', 'specialty': 'Ortopedia', 'appointment_type': 'presencial', 'next_availability': 'Hoje, 17:30'},
    {'id': 4, 'name': 'Mariana Costa', 'specialty': 'Pediatria', 'appointment_type': 'online', 'next_availability': 'Amanhã, 09:00'},
    {'id': 5, 'name': 'Roberto Alves', 'specialty': 'Clínico Geral', 'appointment_type': 'online', 'next_availability': 'Hoje, 16:00'}
])

# Dados de agendamentos
appointments_data = [
    {'id': 1, 'doctor': 'Ana Silva', 'specialty': 'Clínico Geral', 'date': '12/05/2025', 'time': '14:30', 'type': 'online', 'status': 'Agendada'},
    {'id': 2, 'doctor': 'Carlos Mendes', 'specialty': 'Cardiologia', 'date': '20/05/2025', 'time': '10:00', 'type': 'presencial', 'status': 'Agendada'}
]

# Histórico médico
medical_history = {
    'diagnoses': [
        {'id': 1, 'condition': 'Gripe', 'date': '03/05/2025', 'symptoms': 'febre, dor de cabeça, tosse', 'probability': 85},
        {'id': 2, 'condition': 'Dor lombar', 'date': '22/04/2025', 'symptoms': 'dor muscular, fadiga', 'probability': 70}
    ],
    'past_appointments': [
        {'id': 1, 'doctor': 'Paula Ferreira', 'specialty': 'Clínico Geral', 'date': '15/04/2025', 'type': 'Rotina', 'report': 'Consulta de rotina, paciente em boas condições'},
        {'id': 2, 'doctor': 'Marcos Lima', 'specialty': 'Ortopedia', 'date': '02/03/2025', 'type': 'Avaliação', 'report': 'Avaliação de dor lombar, recomendado fisioterapia'}
    ],
    'exams': [
        {'id': 1, 'type': 'Hemograma completo', 'date': '10/04/2025', 'results': 'Dentro dos parâmetros normais'},
        {'id': 2, 'type': 'Raio-X Lombar', 'date': '05/03/2025', 'results': 'Leve desvio postural, sem fraturas'}
    ]
}

# Perfil do paciente
patient_profile = {
    'name': 'Maria Santos',
    'id': '12345678',
    'birth_date': '15/03/1985',
    'gender': 'Feminino',
    'blood_type': 'O+',
    'height': '1.68m',
    'weight': '65kg',
    'conditions': [
        {'name': 'Asma', 'diagnosed': '2010', 'severity': 'Moderada'},
        {'name': 'Hipertensão', 'diagnosed': '2018', 'severity': 'Leve'}
    ],
    'allergies': [
        {'name': 'Penicilina', 'reaction': 'Reação severa - evitar todos os derivados'},
        {'name': 'Pólen', 'reaction': 'Rinite alérgica sazonal'}
    ]
}

# Função para gerar resultados de diagnóstico simulados
def mock_diagnosis_results(symptoms):
    possible_conditions = []
    
    # Condições baseadas em sintomas
    if 'febre' in symptoms and 'tosse' in symptoms and 'dor de cabeça' in symptoms:
        possible_conditions.append({
            'name': 'Gripe',
            'probability': random.uniform(0.7, 0.9),
            'description': 'Infecção viral comum que afeta o sistema respiratório'
        })
        possible_conditions.append({
            'name': 'COVID-19',
            'probability': random.uniform(0.5, 0.8),
            'description': 'Doença respiratória causada pelo SARS-CoV-2'
        })
    
    if 'dor abdominal' in symptoms and 'náusea' in symptoms:
        possible_conditions.append({
            'name': 'Gastrite',
            'probability': random.uniform(0.6, 0.8),
            'description': 'Inflamação do revestimento do estômago'
        })
    
    if 'dificuldade respiratória' in symptoms:
        possible_conditions.append({
            'name': 'Asma',
            'probability': random.uniform(0.7, 0.95),
            'description': 'Condição crônica que afeta as vias respiratórias'
        })
    
    if not possible_conditions:
        possible_conditions.append({
            'name': 'Resfriado Comum',
            'probability': random.uniform(0.4, 0.6),
            'description': 'Infecção viral leve do trato respiratório superior'
        })
    
    # Ordenar por probabilidade
    possible_conditions.sort(key=lambda x: x['probability'], reverse=True)
    
    # Recomendações gerais
    recommendations = [
        'Hidrate-se adequadamente',
        'Descanse o suficiente',
        'Monitore seus sintomas'
    ]
    
    if any(p['probability'] > 0.7 for p in possible_conditions):
        recommendations.append('Considere marcar uma consulta com um médico para avaliação')
    if 'dificuldade respiratória' in symptoms:
        recommendations.append('Procure atendimento de emergência se a dificuldade respiratória piorar')
    
    return {
        'possible_conditions': possible_conditions,
        'recommendations': recommendations,
        'analyzed_symptoms': symptoms
    }
