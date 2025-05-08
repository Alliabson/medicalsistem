def generate_diagnosis_with_epi_data(symptoms, age, uf, epi_data):
    """Gera diagnóstico considerando dados epidemiológicos"""
    conditions = []
    
    # Verifica se há surto de COVID na região
    if epi_data and epi_data.get('casos'):
        covid_cases = sum([d.get('casos', 0) for d in epi_data['casos'] 
                          if d.get('uf') == uf])
        
        if covid_cases > 1000 and any(sym in symptoms for sym in ['febre', 'tosse', 'dificuldade respiratória']):
            conditions.append({
                'name': 'COVID-19',
                'probability': min(0.3 + (covid_cases / 10000), 0.9),  # Probabilidade baseada na incidência
                'description': f"Alta incidência na região ({covid_cases} casos recentes)"
            })
    
    # Adiciona condições baseadas nos sintomas
    if 'febre' in symptoms and 'dor de garganta' in symptoms:
        conditions.append({
            'name': 'Amigdalite',
            'probability': 0.65,
            'description': 'Inflamação das amígdalas'
        })
    
    if not conditions:
        conditions.append({
            'name': 'Resfriado Comum',
            'probability': 0.5,
            'description': 'Infecção viral leve'
        })
    
    return {
        'possible_conditions': sorted(conditions, key=lambda x: x['probability'], reverse=True),
        'recommendations': [
            'Consulte uma unidade de saúde se os sintomas piorarem',
            'Mantenha hidratação',
            'Monitorar temperatura corporal'
        ],
        'analyzed_symptoms': symptoms,
        'epidemiological_data': epi_data.get('casos', [])[:5] if epi_data else []
    }
