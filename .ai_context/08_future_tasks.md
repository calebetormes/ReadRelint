# Tarefas Futuras e Backlog (Ideias de Melhoria)

Este arquivo serve como repositório de ideias, discussões de arquitetura e futuras melhorias que foram levantadas durante as sessões de desenvolvimento.

---

## 1. Verificação de Alteração de Arquivos via Hash (SHA-256)
* **Objetivo:** Identificar se um arquivo PDF que já foi processado/descartado sofreu alguma modificação posterior no conteúdo e, caso positivo, forçar a sua releitura automática.
* **Proposta de Solução:**
  * Calcular o hash criptográfico SHA-256 do arquivo no momento do processamento.
  * Armazenar o hash no banco de histórico `processed_registry.json`.
  * Na varredura ou detecção do monitorador, comparar o hash atual com o armazenado. Se houver divergência, limpar a entrada e mandar o arquivo de volta à fila de leitura.

---

## 2. Regra de Precedência de Fatos (Homicídio como Bloqueador)
* **Objetivo:** Evitar que um mesmo documento seja fragmentado ou analisado para múltiplos fatos de menor gravidade se ele já foi identificado como um Homicídio consumado/tentado ou Feminicídio.
* **Proposta de Solução:**
  * Ao rodar qualquer regra (ex: escolas, roubos), o sistema consulta se o arquivo já possui o status `"confirmed"` na regra `"Homicídio"`.
  * Caso positivo, o arquivo é ignorado de forma global para outras regras menores, protegendo a integridade da catalogação de crimes violentos letais intencionais.
