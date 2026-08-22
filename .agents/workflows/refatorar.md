<<<<<<< HEAD
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
=======
---
description: Refatoração e Limpeza de Código 
---

# Workflow de Refatoração e Limpeza de Código (Clean Code)

Este workflow define as diretrizes e os passos necessários para realizar uma refatoração completa no repositório, garantindo a remoção de código morto, otimização da estrutura e alinhamento com os princípios de **Clean Code**, sem alterar o comportamento funcional do sistema.

---

## 🎯 Premissas de Execução

1. **Zero Alteração Comportamental:** O sistema deve comportar-se exatamente da mesma forma antes e depois do processo. Nenhuma regra de negócio, contrato de API ou fluxo de interface deve ser modificado.
2. **Eliminação de Código Morto:** Arquivos, funções, métodos, variáveis, importações e dependências sem uso/referência devem ser totalmente removidos.
3. **Clean Code:** Manter código expressivo, modular, com alta coesão, baixo acoplamento e responsabilidade única.

---

## 📋 Passos do Workflow

### Passo 1: Mapeamento de Código Morto e Análise Estática
* Executar linters e ferramentas de análise estática para identificar código inacessível (*unreachable code*), arquivos isolados e importações órfãs.
* Mapear rotas, funções, classes e métodos que não possuem nenhuma chamada ativa no projeto.
* Listar trechos de código comentados antigos para remoção.

---

### Passo 2: Validação da Rede de Segurança (Testes)
* Executar a suíte de testes existente e assegurar que **100% dos testes estão passando** antes de iniciar as modificações.
* Se trechos que sofrerão grandes refatorações não possuírem cobertura, adicionar testes de regressão prévios para garantir a paridade de comportamento.

---

### Passo 3: Limpeza de Código Morto (Dead Code Deletion)
* Excluir arquivos e pastas obsoletos que não possuem referências no sistema.
* Excluir funções, classes, métodos, parâmetros e variáveis não utilizados.
* Limpar importações/dependências não utilizadas no topo dos arquivos.

---

### Passo 4: Refatoração Clean Code
* **Nomes Expressivos:** Renomear variáveis, parâmetros, funções e classes para torná-los autoexplicativos em relação ao seu propósito.
* **Princípio da Responsabilidade Única (SRP):** Extrair funções/métodos longos ou com múltiplas responsabilidades em métodos menores e coesos.
* **Simplificação de Condicionais:** 
  * Aplicar *Early Returns* (Guards) para reduzir o aninhamento de `if/else`.
  * Substituir condicionais complexas por variáveis descritivas ou funções auxiliares.

---

### Passo 5: Validação Final e Regressão
* Executar a suíte completa de testes automatizados e verificar se todos continuam passando.
* Executar a verificação de tipos e a compilação/build do projeto.
* Garantir que a aplicação inicializa e roda sem nenhum erro ou aviso (*warning*) novo.
>>>>>>> 328b89d9a852f43fe0d039462459fdd6a4b5f9e1
