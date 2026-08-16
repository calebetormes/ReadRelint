import re

def clean_transcript_text(text: str) -> str:
    if not text:
        return ""

    # 1. Normaliza finais de linha \r\n para \n e remove espaços ao redor de newlines
    text = re.sub(r'[ \t]*\r?\n[ \t]*', '\n', text)

    # 2. Preserva parágrafos reais (\n\n ou mais) usando um token temporário
    MARKER = "___PARAGRAPH_BREAK___"
    text = re.sub(r'\n{2,}', MARKER, text)

    # 3. Processa cada bloco de parágrafo
    blocks = text.split(MARKER)
    cleaned_blocks = []

    for block in blocks:
        lines = [l.strip() for l in block.split('\n') if l.strip()]
        if not lines:
            continue

        merged_lines = []
        for line in lines:
            if not merged_lines:
                merged_lines.append(line)
            else:
                last_line = merged_lines[-1]

                # Critérios para MANTER uma quebra de linha:
                # - A linha atual é um campo formal (ex: ASSUNTO:, DATA:, RG:, NOME:, SUSPEITO 01:)
                # - A linha atual começa com um marcador de lista (- ou * ou 1.)
                # - A linha anterior termina com dois pontos (:)
                is_field_header = bool(re.match(r'^(?:[A-Z0-9_\- ]{2,25}:|SUSPEITO|ANTECEDENTES|FOTO|REGISTRO|IMAGEM|ANEXOS|\-|\*|\d+[\.\)])', line, re.IGNORECASE))
                last_ended_with_colon = last_line.endswith(':')

                if is_field_header or last_ended_with_colon:
                    merged_lines.append(line)
                else:
                    # Junta com a linha anterior usando espaço
                    merged_lines[-1] = last_line + " " + line

        cleaned_blocks.append("\n".join(merged_lines))

    # 4. Reconstitui os parágrafos com \n\n
    result = "\n\n".join(cleaned_blocks)

    # 5. Normaliza múltiplos espaços consecutivos no meio do texto
    result = re.sub(r'[ \t]{2,}', ' ', result)

    # 6. Corrige pontuação grudada (ex: "anos , ATUAL" -> "anos, ATUAL")
    result = re.sub(r'\s+([,\.\;:\?\!])', r'\1', result)

    return result.strip()

# Teste com o texto da foto enviada pelo usuário
raw_sample = """como
GILMAR
LAURINDO
BELLINI
RG7036249394 - 60 anos , ATUAL PREFEITO DO MUNICÍPIO DE BOA VISTA DO
INCRA/RS pelo Partido Democrático Brasileiro (MDB).
Conforme realto da vítima LUANA, o indivíduo compareceu ao estabelecimento e,
durante o atendimento, solicitou seu número de telefone. Percebendo o comportamento
inadequado, a comunicante forneceu número incorreto. Após ser atendido, Gilmar permaneceu
por longo período circulando pela farmácia, observando insistentemente as funcionárias,
realizando perguntas sobre dados pessoais.
Relata ainda, que o autor ingeriu medicamento para disfunção erétil no interior do
estabelecimento e realizou gestos de conotação sexual, passando as mãos em suas partes íntimas
na presença das funcionárias.
LUANA informa que sua colega de trabalho, AMANDA
CARRAVETTA DE CASTRO - RG: 8083529712 - 38 Anos, presenciou os fatos e igualmente"""

print("=== TEXTO LIMPO ===")
cleaned = clean_transcript_text(raw_sample)
print(cleaned)
