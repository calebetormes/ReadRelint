import re
from typing import Dict, Tuple, List, Set, Any

class BrazilianNameParser:
    """
    Parser determinístico e limpador sintático de nomes próprios civis no Português do Brasil (pt-BR),
    projetado para higienizar entradas ruidosas de Ocorrências Policiais e RELINTs.
    """

    # Preposições e conectivos civis válidos do Português do Brasil
    VALID_CONNECTIVES: Set[str] = {
        "de", "da", "do", "dos", "das", "e", "san", "santa"
    }

    # Palavras e tokens institucionais, geográficos ou contextuais que NUNCA fazem parte de um nome civil
    INVALID_TOKENS: Set[str] = {
        "bairro", "rua", "av", "avenida", "alameda", "travessa", "rodovia", "br", "rs", "centro",
        "brigada", "militar", "polícia", "policia", "relatório", "relatorio", "inteligência", "inteligencia",
        "veículo", "veiculo", "carro", "moto", "motocicleta", "apreendido", "apreendida", "conduzido", "conduzida",
        "vítima", "vitima", "suspeito", "suspeita", "acusado", "acusada", "comunicante", "testemunha", "autor", "autora",
        "efetuada", "sofrida", "contato", "presentes", "ocorrência", "ocorrencia", "batalhão", "batalhao", "bpm",
        "dp", "delegacia", "guarnição", "guarnicao", "viatura", "documento", "preparatório", "preparatorio",
        "acesso", "restrito", "lei", "artigo", "inciso", "código", "codigo", "penal", "local", "fato", "fatos",
        "mordida", "agressão", "agressao", "disparo", "arma", "fogo", "posse", "tráfico", "trafico", "roubo", "furto"
    }

    # Prefixos narrativos policiais para remoção
    PREFIX_PATTERNS = re.compile(
        r'(?i)^\s*(?:'
        r'posteriormente\s+identificad[oa]\s+(?:apenas\s+)?como|'
        r'identificad[oa]\s+(?:apenas\s+)?como|'
        r'v[íi]tima\s+identificad[oa]\s+como|'
        r'suspeito\s+identificad[oa]\s+como|'
        r'acusad[oa]\s+identificad[oa]\s+como|'
        r'conduzid[oa]\s+(?:\à\s+dp\s+)?o\s+suspeito|'
        r'conforme\s+relato\s+d[ao](?:\s+v[íi]tima)?|'
        r'momento\s+em\s+que\s+foi\s+feito\s+contato\s+com|'
        r'(?:foi\s+)?feito\s+contato\s+com|'
        r'em\s+contato\s+com|'
        r'contato\s+com|'
        r'na\s+pessoa\s+de|'
        r'pela\s+pessoa\s+de|'
        r'em\s+desfavor\s+de|'
        r'em\s+rela[çc][ãa]o\s+a|'
        r'com\s+o\s+conduzido|'
        r'na\s+companhia\s+de|'
        r'estavam?\s+presentes?|'
        r'estavam?|'
        r'estava|'
        r'tratar-se\s+de|'
        r'trata-se\s+de|'
        r'uma\s+(?:agress[ãa]o|mordida|les[ãa]o)\s+(?:sofrida|efetuada)\s+(?:por|pela?)|'
        r'uma\s+agress[ãa]o\s+sofrida\s+por|'
        r'v[íi]tima|'
        r'suspeito|'
        r'acusado|'
        r'comunicante|'
        r'testemunha|'
        r'envolvid[oa]|'
        r'o\s+indiv[íi]duo|'
        r'indiv[íi]duos?|'
        r'para\s+[oa]|'
        r'para|'
        r'sr[a]?\.'
        r')\s+',
        re.IGNORECASE
    )

    # Sufixos narrativos e de dados pessoais para corte
    SUFFIX_PATTERNS = re.compile(
        r'(?i)\s*(?:'
        r'[,–—\-]?\s*(?:residente|morador|nascid[oa]|qualificad[oa]|natural)\b.*|'
        r'[,–—\-]?\s*(?:RG|CPF|ID\s*FUNC|MATR[ÍI]CULA)[:\s\.\d\-]+.*|'
        r'[,–—\-]?\s*(?:com\s+idade\s+de|\d+\s*anos).*|'
        r'[,–—\-]?\s*no\s+local.*|'
        r'[,–—\-]?\s*a\s+qual\s+relatou.*'
        r')$',
        re.IGNORECASE
    )

    @classmethod
    def extract_nickname(cls, raw_text: Any) -> Tuple[str, str]:
        """
        Extrai alcúnhas/vulgos do texto do participante (ex: vulgo 'Alemão', "Guto" ou (Marquinhos)).
        Retorna uma tupla: (texto_sem_alcunha, alcunha_extraida)
        """
        if not raw_text or isinstance(raw_text, bool):
            return "", ""

        text = str(raw_text).strip()
        nickname = ""

        # 1. Padrão explícito: vulgo 'XXX', vulgo "XXX", alcunha XXX, conhecido por XXX
        vulgo_match = re.search(
            r'(?i)[,\s–—\-]*\b(?:vulgo|alcunha|conhecid[oa]\s+por)\s*[\r\n]*["\'\(\s]*([^"\'\)\r\n,–—\-]+)["\'\)]?',
            text
        )
        if vulgo_match:
            nickname = vulgo_match.group(1).strip()
            text = text[:vulgo_match.start()] + text[vulgo_match.end():]

        # 2. Padrão de aspas isoladas no meio ou fim do nome: João da Silva "Alemão"
        if not nickname:
            quote_match = re.search(r'["\']([^"\'\r\n]{2,30})["\']', text)
            if quote_match:
                nickname = quote_match.group(1).strip()
                text = text[:quote_match.start()] + " " + text[quote_match.end():]

        # Normaliza alcunha
        nickname = nickname.strip(" ,.-–—:;\"'()")
        if nickname.lower() in ["-", "-.", "não possui", "nao possui", "n/i", "none", "sem alcunha"]:
            nickname = ""

        return text.strip(), nickname.title() if nickname else ""

    @classmethod
    def _strip_prefixes_and_suffixes(cls, text: str) -> str:
        """
        Remove iterativamente prefixos policiais, sufixos de contexto e pontuação periférica.
        """
        if not text:
            return ""

        # 1. Limpa prefixos conhecidos repetidamente
        prev_text = ""
        while text != prev_text:
            prev_text = text
            text = cls.PREFIX_PATTERNS.sub("", text).strip()

        # 2. Limpa sufixos conhecidos
        text = cls.SUFFIX_PATTERNS.sub("", text).strip()

        # 3. Limpa pontuações periféricas e separadores
        return re.sub(r'^[,\.–—\-:;]+|[,\.–—\-:;]+$', '', text).strip()

    @classmethod
    def _filter_valid_tokens(cls, text: str) -> List[str]:
        """
        Tokeniza a string e filtra apenas os substantivos próprios e conectivos civis válidos em pt-BR.
        """
        if not text:
            return []

        words = text.split()
        valid_words: List[str] = []

        for word in words:
            clean_word = re.sub(r'[^a-zA-Z\u00C0-\u00FF]', '', word)
            if not clean_word:
                continue

            lower_word = clean_word.lower()

            # Descarta tokens institucionais/ruídos banidos
            if lower_word in cls.INVALID_TOKENS:
                continue

            # Aceita conectivos válidos apenas se já houver um nome próprio anterior
            if lower_word in cls.VALID_CONNECTIVES:
                if valid_words:
                    valid_words.append(lower_word)
                continue

            # Aceita substantivos próprios civis (tamanho >= 2)
            if len(clean_word) >= 2:
                formatted_word = clean_word.capitalize()
                valid_words.append(formatted_word)

        # Remove conectivo solto no final (ex: "Marcos da" -> "Marcos")
        while valid_words and valid_words[-1].lower() in cls.VALID_CONNECTIVES:
            valid_words.pop()

        return valid_words

    @classmethod
    def _format_name_parts(cls, valid_words: List[str]) -> str:
        """
        Formata as partes do nome mantendo caixa baixa para conectivos (de, da, do) e Title Case para os nomes.
        """
        if not valid_words:
            return ""

        final_parts: List[str] = []
        for idx, w in enumerate(valid_words):
            l_w = w.lower()
            if l_w in cls.VALID_CONNECTIVES and idx > 0:
                final_parts.append(l_w)
            else:
                final_parts.append(w.capitalize())

        # Descarta se houver apenas 1 palavra curta/ruído
        if len(final_parts) == 1 and len(final_parts[0]) < 3:
            return ""

        return " ".join(final_parts)

    @classmethod
    def clean_name(cls, raw_name: Any) -> str:
        """
        Higieniza uma string bruta de nome, aplicando remoção de prefixos, sufixos e
        filtragem de tokens válidos de nomes próprios civis do Português do Brasil.
        """
        if not raw_name or isinstance(raw_name, bool):
            return ""

        raw_name_str = str(raw_name)

        # Extrai alcunha se estiver grudada na string
        text_without_nick, _ = cls.extract_nickname(raw_name_str)
        target_text = text_without_nick if text_without_nick else raw_name_str

        stripped_text = cls._strip_prefixes_and_suffixes(target_text)
        valid_tokens = cls._filter_valid_tokens(stripped_text)
        return cls._format_name_parts(valid_tokens)

    @classmethod
    def parse_person(cls, raw_string: Any) -> Dict[str, str]:
        """
        Recebe uma string bruta de participante e retorna um dicionário estruturado:
        {"name": "Nome Limpo em Title Case", "nickname": "Alcunha se encontrada"}
        """
        if not raw_string or isinstance(raw_string, bool):
            return {"name": "", "nickname": ""}

        text_without_nick, nickname = cls.extract_nickname(str(raw_string))
        cleaned_name = cls.clean_name(text_without_nick)

        return {
            "name": cleaned_name,
            "nickname": nickname
        }
