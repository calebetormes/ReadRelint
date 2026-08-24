<script>
  import RelintListPane from '$lib/components/relint/RelintListPane.svelte';
  import RelintDetailPane from '$lib/components/relint/RelintDetailPane.svelte';

  // Dados MOCK estruturados de RELINTs para demonstração e interação fluida
  let relintsList = $state([
    {
      id: 1,
      code: 'RELINT-2026-001',
      subject: 'Homicídio Consumado por Arma de Fogo - Facção Os Manos',
      date_of_fact: '2026-08-20',
      bm_group: 'Homicídio',
      user_edited: true,
      registry_number: '9012/2026',
      police_unit: '1ª DP Homicídios',
      registry_year: 2026,
      address: 'Rua Voluntários da Pátria, 450',
      neighborhood: 'Centro Histórico',
      municipality: 'Porto Alegre',
      summary: 'Vítima atingida por disparos provenientes de veículo em movimento. Suspeita de conflito de facções na região central.',
      homicide_details: {
        fact_type: 'Homicídio Consumado',
        motivation: 'Disputa de Território',
        means_used: 'Arma de Fogo (9mm)',
        police_dept: 'DHPP'
      },
      participants: [
        { id: 101, name: 'Marcos Vinícius "Vini"', alias: 'Vini', role: 'Vítima', photo_path: null },
        { id: 102, name: 'Diego Ferreira', alias: 'Alemão', role: 'Autor', photo_path: null }
      ],
      raw_text: `RELINT Nº 2026-001 - DEPARTAMENTO DE HOMICÍDIOS
FATO: Homicídio consumado registrado no Bairro Centro Histórico, Porto Alegre.
PARTICIPANTES: Marcos Vinícius (Vítima) e Diego Ferreira (Autor).
ANEXOS: Fotografias e cápsulas recolhidas no local.

No dia 20 de agosto de 2026, por volta das 22h, a guarnição respondeu ao chamado referente a disparos efetuados na Rua Voluntários da Pátria...`
    },
    {
      id: 2,
      code: 'RELINT-2026-002',
      subject: 'Apreensão de Entorpecentes e Armamento de Alto Calibre',
      date_of_fact: '2026-08-22',
      bm_group: 'Tráfico de Drogas',
      user_edited: false,
      registry_number: '4302/2026',
      police_unit: '2ª DP de Alvorada',
      registry_year: 2026,
      address: 'Rua das Camélias, 120',
      neighborhood: 'Americana',
      municipality: 'Alvorada',
      summary: 'Cumprimento de mandado de busca resultando na apreensão de 12kg de maconha, 2kg de cocaína e 1 fuzil 5.56.',
      participants: [
        { id: 103, name: 'Lucas Mendes', alias: 'Gordo', role: 'Suspeito', photo_path: null }
      ],
      raw_text: `RELINT Nº 2026-002 - OPERAÇÃO DE TRÁFICO
FATO: Cumprimento de mandado na cidade de Alvorada com grande volume de apreensão.
PARTICIPANTES: Lucas Mendes (Suspeito).
ANEXOS: Auto de apreensão de drogas e armamento.`
    },
    {
      id: 3,
      code: 'RELINT-2026-003',
      subject: 'Roubo a Estabelecimento Comercial com Retenção de Vítimas',
      date_of_fact: '2026-08-23',
      bm_group: 'Roubos e Furtos',
      user_edited: false,
      registry_number: '1105/2026',
      police_unit: '3ª DP Canoas',
      registry_year: 2026,
      address: 'Av. Getúlio Vargas, 2200',
      neighborhood: 'Niterói',
      municipality: 'Canoas',
      summary: 'Dois indivíduos armados renderam funcionários de farmácia e subtraíram valores do caixa e pertences.',
      participants: [
        { id: 104, name: 'Ana Paula Rocha', alias: '', role: 'Testemunha', photo_path: null }
      ],
      raw_text: `RELINT Nº 2026-003 - DELEGACIA DE CANOAS
FATO: Roubo qualificado a estabelecimento comercial.
PARTICIPANTES: Ana Paula Rocha (Testemunha).`
    }
  ]);

  let selectedRelintId = $state(1);

  let activeRelint = $derived(
    relintsList.find((r) => r.id === selectedRelintId) || relintsList[0]
  );

  /**
   * @param {any} relint
   */
  function handleSelectRelint(relint) {
    selectedRelintId = relint.id;
  }

  /**
   * @param {any} updatedRelint
   */
  function handleSaveRelint(updatedRelint) {
    const idx = relintsList.findIndex((r) => r.id === updatedRelint.id);
    if (idx !== -1) {
      relintsList[idx] = { ...updatedRelint, user_edited: true };
    }
  }
</script>

<svelte:head>
  <title>Boletins RELINT | ReadRelint Dashboard</title>
</svelte:head>

<div class="relints-master-detail-page">
  <div class="pane-left">
    <RelintListPane 
      relints={relintsList} 
      selectedId={selectedRelintId} 
      onSelect={handleSelectRelint} 
    />
  </div>

  <div class="pane-right">
    <RelintDetailPane 
      relint={activeRelint} 
      onSave={handleSaveRelint} 
    />
  </div>
</div>

<style>
  .relints-master-detail-page {
    display: grid;
    grid-template-columns: 320px 1fr;
    height: calc(100vh - 64px - var(--space-6) * 2);
    background-color: var(--color-bg-surface-card);
    border: 1px solid var(--color-border-subtle);
    border-radius: var(--radius-lg);
    overflow: hidden;
  }

  .pane-left {
    height: 100%;
    overflow: hidden;
  }

  .pane-right {
    height: 100%;
    overflow: hidden;
  }

  @media (max-width: 992px) {
    .relints-master-detail-page {
      grid-template-columns: 1fr;
    }
    
    .pane-left {
      height: 300px;
    }
  }
</style>
