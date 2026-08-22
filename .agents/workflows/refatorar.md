# Workflow de Refatoração

Este workflow foca em ações práticas e diretas, otimizado para equipes com domínio em Clean Code.

## 1. Remoção de Código Morto
- [ ] Identificar e deletar arquivos órfãos e dependências não utilizadas.
- [ ] Remover classes, métodos e funções inalcançáveis (dead code).
- [ ] Limpar variáveis, parâmetros e atributos declarados mas sem leitura/uso.
- [ ] *Check de segurança:* Verificar injeções de dependência, reflexões ou rotinas de inicialização antes de deletar.

## 2. Nomenclatura
- [ ] **Arquivos/Módulos:** Ajustar nomes para o padrão do projeto (ex: kebab-case) refletindo sua responsabilidade.
- [ ] **Classes/Interfaces:** Substantivos ou sintagmas nominais claros e específicos.
- [ ] **Funções/Métodos:** `Verbo + Substantivo` indicando a ação exata.
- [ ] **Variáveis:** Evitar abreviações; o nome deve carregar a intenção e o contexto.

## 3. Comentários
- [ ] Eliminar todo código comentado (confiar no Git).
- [ ] Remover comentários que explicam o "como" ou descrevem o que está óbvio no código.
- [ ] Escrever ou reescrever comentários exclusivamente para explicar o "porquê" (regras de negócio peculiares, limitações técnicas ou integrações específicas).

## 4. Garantia de Estabilidade (Zero Regressão)
- [ ] Manter 100% das interfaces públicas, payloads de entrada/saída e comportamentos intactos.
- [ ] Executar a validação da rotina (ou rodar a suíte de testes) garantindo que nenhum comportamento paralelo foi afetado.
