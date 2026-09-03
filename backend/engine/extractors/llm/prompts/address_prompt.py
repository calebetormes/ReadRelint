# -*- coding: utf-8 -*-
"""
Diretrizes e regras especializadas para extração de Endereço, Município e Coordenadas via LLM.
"""

ADDRESS_PROMPT = """
DIRETRIZES DE ENDEREÇO E LOCALIZAÇÃO (street, number, neighborhood, municipality, coordinates, map_url):
1. LOGRADOURO DO FATO:
   - 'street': Nome da rua, avenida, travessa, rodovia (com Km), beco, linha rural ou estrada, exatamente como aparece no texto (formato: '<Tipo de via> <Nome>', ex: 'Rua <Nome>', 'BR-<número>, Km <número>', 'Linha <Nome>'). Se não houver logradouro identificável, retorne null (NUNCA copie um exemplo genérico).
   - 'number': Número predial ou 'S/N' (ou 'Km XX' se for rodovia).
   - 'neighborhood': Nome do bairro urbano. REGRA OBRIGATÓRIA: quando for zona rural (linhas, assentamentos, fazendas, rodovias ou estradas do interior), preencha SEMPRE 'Interior'.
   - 'municipality': Nome da cidade/município onde o fato ocorreu. Dica: confira também a cidade citada no campo ASSUNTO do cabeçalho.

2. DESAMBIGUAÇÃO CRÍTICA (LOCAL DO FATO vs SUSPEITO vs ÓRGÃOS):
   - Extraia ESTRITAMENTE o endereço do 1º parágrafo ONDE O CRIME/FATO OCORREU.
   - NUNCA extraia o endereço residencial de suspeitos citados posteriormente no texto.
   - NUNCA extraia o endereço da Delegacia de Polícia (onde lavrou o flagrante) nem do Hospital (onde a vítima foi socorrida).

3. COORDENADAS E LINKS DO GOOGLE MAPS:
   - 'coordinates': Se houver coordenadas geográficas REAIS digitadas no texto (ex: '-28.6645, -53.5688' ou '28°15\'40"S'), extraia em formato decimal. ATENÇÃO: Se não houver coordenadas digitadas no texto, retorne estritamente null (NUNCA invente números de GPS fictícios).
   - 'map_url': Se houver link explícito do Google Maps (ex: 'https://maps.app.goo.gl/...' ou 'https://www.google.com/maps/...'), extraia neste campo. Se não houver link no documento, retorne null.
"""
