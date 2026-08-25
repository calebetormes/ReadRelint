<script>
  import '../app.css';
  import { page } from '$app/stores';
  import AppShell from '$lib/components/layout/AppShell.svelte';

  let { children } = $props();
</script>

<AppShell>
  {#key $page.url.pathname}
    <div class="page-enter-animation" style="width: 100%; height: 100%;">
      {@render children()}
    </div>
  {/key}
</AppShell>

