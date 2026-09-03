# -*- coding: utf-8 -*-
"""
Instruções específicas por especialidade (bm_group), usadas como system_prompt dedicado
no Passo 3 do Pipeline Multi-Pass. Cada RELINT recebe SOMENTE a instrução da sua própria
especialidade (já classificada deterministicamente antes deste passo) — nunca todas juntas.
"""

SPECIALTY_INSTRUCTIONS = {
    "Homicídio": """
DIRETRIZES DE ESPECIALIDADE — HOMICÍDIO (fact_type, motivation):
Analise estritamente o fato descrito e determine se foi Tentado ou Consumado, e a motivação
dentre as opções fornecidas no schema. Nunca invente uma motivação sem base textual explícita:
prefira retornar null a adivinhar.
""".strip(),

    "Prisão por Tráfico": """
DIRETRIZES DE ESPECIALIDADE — PRISÃO POR TRÁFICO (drug_quantity, drug_types):
Extraia a quantidade e o(s) tipo(s) de droga exatamente como aparecem no texto. Não some,
não converta unidades e não estime — copie o valor literal do documento.
""".strip(),

    "Roubo a Estabelecimento": """
DIRETRIZES DE ESPECIALIDADE — ROUBO A ESTABELECIMENTO (establishment_type):
Identifique o tipo de estabelecimento comercial roubado exatamente como descrito no texto.
""".strip(),

    "Roubo de Veículo": """
DIRETRIZES DE ESPECIALIDADE — ROUBO DE VEÍCULO (vehicle_model, license_plate, recovery_location):
Extraia marca/modelo e placa exatamente como aparecem no texto. Só preencha recovery_location
se o texto confirmar explicitamente que o veículo foi recuperado.
""".strip(),

    "Furto de Veículo": """
DIRETRIZES DE ESPECIALIDADE — FURTO DE VEÍCULO (vehicle_model, license_plate, recovery_location):
Extraia marca/modelo e placa exatamente como aparecem no texto. Só preencha recovery_location
se o texto confirmar explicitamente que o veículo foi recuperado.
""".strip(),

    "Roubo a Pedestre": """
DIRETRIZES DE ESPECIALIDADE — ROUBO A PEDESTRE (weapon_used, stolen_object):
Identifique a arma utilizada dentre as opções do schema e o(s) objeto(s) roubado(s) da vítima,
exatamente como descrito no texto.
""".strip(),
}
