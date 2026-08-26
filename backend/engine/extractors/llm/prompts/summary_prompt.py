# -*- coding: utf-8 -*-
"""
Diretrizes e regras especializadas para extração da Síntese Factual Resumida via LLM.
"""

SUMMARY_PROMPT = """
DIRETRIZES DA SÍNTESE FACTUAL (summary):
1. Escreva um resumo narrativo explicativo em 1 único parágrafo fluido (de 2 a 4 frases).
2. Explique com clareza O QUE ACONTECEU: a dinâmica dos fatos, motivação preliminar (se houver), meios ou armas empregadas e o desfecho (ex: vítima socorrida, autores presos, fuga, apreensões).
3. REGRA ANTI-REDUNDÂNCIA:
   - NÃO inclua o endereço, rua, número ou bairro no texto da síntese (o local possui campo próprio).
   - NÃO inclua dados cadastrais ou burocráticos de participantes (como RG, CPF, filiação, data de nascimento). Se necessário para o entendimento da narrativa, mencione apenas o nome ou primeiro nome dos indivíduos.
   - NÃO inclua preâmbulos operacionais da polícia (ex: "chegando ao local a guarnição constatou...", "conforme boletim de ocorrência..."). Vá direto aos fatos.
4. OBRIGATÓRIO: Jamais omita ou deixe o campo summary vazio.
5. OBRIGATÓRIO: JAMAIS repita ou copie o Assunto (título) do documento. Escreva com suas próprias palavras o texto do fato principal.
"""
