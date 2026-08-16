import re

def extract_subject_fallback(text: str, filename: str) -> str:
    # 1. Tenta pegar a linha ASSUNTO: do cabeçalho do RELINT
    match = re.search(r'(?i)ASSUNTO\s*:\s*([^\r\n]+)', text)
    if match:
        sub = match.group(1).strip()
        if len(sub) > 3:
            return sub
            
    # 2. Tenta extrair do próprio nome do arquivo PDF (ex: RELINT 459 - ADJ-INT-INST - Roubo a...)
    match_fn = re.search(r'(?i)RELINT\s*\d+[^-\n]*-\s*[^-\n]*-\s*(.+?)(?:\.pdf)?$', filename)
    if match_fn:
        return match_fn.group(1).strip()
        
    return ""

def extract_fallback_summary(text: str, subject: str = "") -> str:
    if not text:
        return ""
        
    # 1. Pega o corpo a partir de ANEXOS: ou descarta o cabeçalho técnico
    match_body = re.search(r'(?i)ANEXOS?\s*:\s*(?:XXX|\w+)?\s*[\r\n]+(.*)', text, re.DOTALL)
    body = match_body.group(1).strip() if match_body else text
    
    # 2. Remove legendas de fotos conhecidas
    body = re.sub(r'(?i)(?:FOTO|IMAGEM|REGISTRO|CÂMERA)\s+D[OE]\s+[^\r\n]+', '', body)
    
    # 3. Divide em parágrafos e pega o primeiro parágrafo narrativo significativo
    paragraphs = [p.strip() for p in body.split('\n') if len(p.strip()) > 30]
    
    narrative = ""
    for p in paragraphs:
        # Ignora linhas que parecem ser metadados de cabeçalho
        if any(kw in p.upper() for kw in ["RELATÓRIO DE INTELIGÊNCIA", "ORIGEM:", "DIFUSÃO:", "REFERÊNCIA:"]):
            continue
        narrative = p
        break
        
    if not narrative and len(body) > 0:
        narrative = body[:400]
        
    # Limita tamanho a 450 caracteres sem cortar palavra
    if len(narrative) > 450:
        narrative = narrative[:450].rsplit(' ', 1)[0] + "..."
        
    if subject and not narrative.lower().startswith(subject.lower()[:15]):
        return f"{subject}. {narrative}"
    return narrative

# Teste com o conteúdo bruto do RELINT 459
content_459 = """RELATÓRIO DE INTELIGÊNCIA Nº 4592026/ADJ-INT-CRIM – 30/07/2026
DATA: 30/07/2026
ASSUNTO: ROUBO A ESTABELECIMENTO COMERCIAL EM PANAMBI -RS
ORIGEM: ARI/AJ
DIFUSÃO: ACI
DIFUSÃO ANTERIOR: XXX
REFERÊNCIA:
ANEXOS: XXX
Em 30 de julho de 2026, por volta das 01h30min, quatro indivíduos armados
efetuaram um Roubo ao Estabelecimento Comercial Ótica Rasia Premium, localizado na
Rua Praça Engenheiro Walter Faulhaber, nº 23 – Centro, em Panambi (Localização:
https://maps.app.goo.gl/9qVifWwAHo67Z8KG6).
A Brigada Militar foi acionada por volta das 06h40min na Delegacia de Polícia de
Panambi..."""

filename_459 = "RELINT 459 - ADJ-INT-INST - Roubo a estabelecimento Comercial em Panambi - RS.pdf"

subj = extract_subject_fallback(content_459, filename_459)
summ = extract_fallback_summary(content_459, subj)

print("SUBJECT FALLBACK:", subj)
print("SUMMARY FALLBACK:")
print(summ)
