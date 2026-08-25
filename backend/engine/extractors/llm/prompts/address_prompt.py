# -*- coding: utf-8 -*-
"""
Diretrizes e regras especializadas para extração de Endereço, Município e Coordenadas via LLM.
"""

ADDRESS_PROMPT = """
DIRETRIZES DE ENDEREÇO E LOCALIZAÇÃO (address, municipality, coordinates, map_url):
1. Extraia o logradouro exato onde o fato ocorreu:
   - 'street': Nome da rua, avenida, travessa, rodovia, beco ou estrada (ex: 'Rua General Osório', 'Av. Presidente Vargas', 'RS-118').
   - 'number': Número predial ou 'S/N' caso não informado.
   - 'municipality': Nome do município ou cidade (ex: 'Porto Alegre', 'Canoas', 'Santa Maria').
2. ATENÇÃO - LOCAL DO FATO vs ÓRGÃOS:
   - Extraia o endereço ONDE O CRIME/FATO OCORREU. Não confunda com o endereço da Delegacia de Polícia, Batalhão da BM ou Hospital.
3. COORDENADAS E LINKS DO GOOGLE MAPS:
   - 'coordinates': Se houver coordenadas geográficas no texto (ex: '-29.6842, -53.8069' ou '29°41\'03"S 53°48\'25"W'), extraia em formato decimal padrão Google Maps ('-29.xxxx, -51.xxxx').
   - 'map_url': Se houver link explícito do Google Maps (ex: 'https://maps.app.goo.gl/...' ou 'https://www.google.com/maps/...'), extraia neste campo.
"""
