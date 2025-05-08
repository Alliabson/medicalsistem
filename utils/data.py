import pandas as pd
from datetime import datetime

# Dados básicos
available_symptoms = [
    'febre', 'tosse', 'dor de garganta', 'dificuldade respiratória',
    'cefaleia', 'mialgia', 'coriza', 'náusea', 'vômito', 'diarreia'
]

doctors_data = pd.DataFrame([
    {'id': 1, 'name': 'Ana Silva', 'specialty': 'Clínico Geral', 'appointment_type': 'online', 'next_availability': 'Hoje, 14:30'},
    {'id': 2, 'name': 'Carlos Mendes', 'specialty': 'Cardiologia', 'appointment_type': 'presencial', 'next_availability': 'Amanhã, 10:00'}
])

appointments_data = []
medical_history = {'diagnoses': [], 'past_appointments': [], 'exams': []}

def mock_diagnosis_results(symptoms):
    return {
        'possible_conditions': [
            {'name': 'Gripe', 'probability': 0.85, 'description': 'Infecção viral comum'},
            {'name': 'Resfriado', 'probability': 0.45, 'description': 'Infecção viral leve'}
        ],
        'recommendations': ['Descanse bastante', 'Beba líquidos'],
        'analyzed_symptoms': symptoms
    }
