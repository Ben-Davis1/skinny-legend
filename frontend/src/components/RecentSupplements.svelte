<script>
  import { onMount, createEventDispatcher } from 'svelte';
  import { supplements } from '../lib/api.js';

  export let dailyLogId;

  const dispatch = createEventDispatcher();

  let recentSupplements = [];
  let loading = true;

  onMount(async () => {
    await loadRecentSupplements();
  });

  async function loadRecentSupplements() {
    try {
      loading = true;
      // Get all supplements from the last 30 days, get unique ones
      const allSupplements = await supplements.getRecent();
      
      // Group by name and get the most recent
      const supplementMap = new Map();
      allSupplements.forEach(supp => {
        if (!supplementMap.has(supp.name)) {
          supplementMap.set(supp.name, supp);
        }
      });
      
      recentSupplements = Array.from(supplementMap.values()).slice(0, 10);
    } catch (err) {
      console.error('Failed to load recent supplements:', err);
      recentSupplements = [];
    } finally {
      loading = false;
    }
  }

  async function handleQuickAdd(supplement) {
    try {
      await supplements.create({
        daily_log_id: dailyLogId,
        name: supplement.name,
        dosage: supplement.dosage,
        type: supplement.type,
        time_taken: new Date().toTimeString().split(' ')[0].substring(0, 5),
        notes: 'Quick add from recent'
      });
      dispatch('update');
    } catch (err) {
      console.error('Failed to add supplement:', err);
    }
  }

  function getTypeIcon(type) {
    switch(type) {
      case 'vitamin': return '💊';
      case 'medication': return '💉';
      case 'supplement': return '🌿';
      default: return '💊';
    }
  }
</script>

<div class="recent-supplements card">
  <h3>Recently Used Supplements</h3>

  {#if loading}
    <p class="text-muted">Loading...</p>
  {:else if recentSupplements.length === 0}
    <p class="text-muted">No recent supplements yet. Start logging!</p>
  {:else}
    <div class="supplements-list">
      {#each recentSupplements as supplement (supplement.name + supplement.dosage)}
        <div class="supplement-item">
          <div class="supplement-info">
            <strong>{getTypeIcon(supplement.type)} {supplement.name}</strong>
            <p class="text-muted">{supplement.dosage}</p>
          </div>
          <button class="primary" on:click={() => handleQuickAdd(supplement)}>
            Add
          </button>
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .recent-supplements {
    margin-bottom: 2rem;
  }

  .supplements-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .supplement-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem;
    background: var(--bg);
    border-radius: 4px;
    gap: 1rem;
  }

  .supplement-info {
    flex: 1;
  }

  .supplement-info p {
    margin: 0.25rem 0 0 0;
    font-size: 0.875rem;
  }

  @media (max-width: 768px) {
    .supplement-item {
      flex-direction: column;
      align-items: stretch;
    }

    .supplement-item button {
      width: 100%;
    }
  }
</style>
