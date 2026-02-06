<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { supplements } from '../lib/api.js';

  export let dailyLogId;

  const dispatch = createEventDispatcher();

  let supplementList = [];
  let loading = false;
  let showForm = false;

  let newSupplement = {
    name: '',
    dosage: '',
    type: 'supplement',
    time_taken: '',
    notes: ''
  };

  const supplementTypes = ['vitamin', 'medication', 'supplement'];

  onMount(async () => {
    await loadSupplements();
  });

  async function loadSupplements() {
    if (!dailyLogId) return;
    try {
      loading = true;
      supplementList = await supplements.getByLog(dailyLogId);
    } catch (err) {
      console.error('Failed to load supplements:', err);
    } finally {
      loading = false;
    }
  }

  async function handleAdd() {
    if (!newSupplement.name.trim()) return;

    try {
      await supplements.create({
        daily_log_id: dailyLogId,
        ...newSupplement
      });
      await loadSupplements();
      dispatch('update');
      showForm = false;
      resetForm();
    } catch (err) {
      console.error('Failed to add supplement:', err);
    }
  }

  async function handleDelete(supplementId) {
    try {
      await supplements.delete(supplementId);
      await loadSupplements();
      dispatch('update');
    } catch (err) {
      console.error('Failed to delete supplement:', err);
    }
  }

  function resetForm() {
    newSupplement = {
      name: '',
      dosage: '',
      type: 'supplement',
      time_taken: '',
      notes: ''
    };
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

<div class="supplement-logger card">
  <div class="flex-between">
    <h3>Vitamins & Medications</h3>
    <button class="outline" on:click={() => showForm = !showForm}>
      {showForm ? 'Cancel' : '+ Add'}
    </button>
  </div>

  {#if showForm}
    <div class="supplement-form">
      <div class="form-group">
        <label for="supplement-name">Name *</label>
        <input
          id="supplement-name"
          type="text"
          bind:value={newSupplement.name}
          placeholder="e.g., Vitamin D, Aspirin"
          required
        />
      </div>

      <div class="form-row">
        <div class="form-group">
          <label for="supplement-type">Type</label>
          <select id="supplement-type" bind:value={newSupplement.type}>
            {#each supplementTypes as type}
              <option value={type} style="text-transform: capitalize;">{type}</option>
            {/each}
          </select>
        </div>

        <div class="form-group">
          <label for="dosage">Dosage</label>
          <input
            id="dosage"
            type="text"
            bind:value={newSupplement.dosage}
            placeholder="e.g., 1000mg, 2 tablets"
          />
        </div>
      </div>

      <div class="form-group">
        <label for="time-taken">Time Taken</label>
        <input
          id="time-taken"
          type="time"
          bind:value={newSupplement.time_taken}
        />
      </div>

      <div class="form-group">
        <label for="supplement-notes">Notes (optional)</label>
        <input
          id="supplement-notes"
          type="text"
          bind:value={newSupplement.notes}
          placeholder="e.g., With breakfast"
        />
      </div>

      <button class="primary" on:click={handleAdd} disabled={!newSupplement.name.trim()}>
        Add Supplement
      </button>
    </div>
  {/if}

  {#if supplementList.length > 0}
    <div class="supplement-list">
      {#each supplementList as supplement (supplement.id)}
        <div class="supplement-item">
          <div class="supplement-info">
            <div class="supplement-header">
              <span class="supplement-icon">{getTypeIcon(supplement.type)}</span>
              <strong>{supplement.name}</strong>
              <span class="supplement-type">{supplement.type}</span>
            </div>
            <div class="supplement-details">
              {#if supplement.dosage}
                <span class="text-muted">{supplement.dosage}</span>
              {/if}
              {#if supplement.time_taken}
                <span class="text-muted">• {supplement.time_taken}</span>
              {/if}
            </div>
            {#if supplement.notes}
              <p class="text-muted supplement-notes">{supplement.notes}</p>
            {/if}
          </div>
          <button class="danger" on:click={() => handleDelete(supplement.id)}>
            Delete
          </button>
        </div>
      {/each}
    </div>
  {:else if !showForm}
    <p class="text-muted text-center" style="margin-top: 1rem;">No vitamins or medications logged today</p>
  {/if}
</div>

<style>
  .supplement-logger {
    margin-bottom: 2rem;
  }

  .supplement-form {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border);
  }

  .form-group {
    margin-bottom: 1rem;
  }

  .form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
  }

  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }

  .supplement-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    margin-top: 1rem;
  }

  .supplement-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem;
    background: var(--bg);
    border-radius: 4px;
  }

  .supplement-info {
    flex: 1;
  }

  .supplement-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.25rem;
  }

  .supplement-icon {
    font-size: 1.25rem;
  }

  .supplement-type {
    font-size: 0.75rem;
    padding: 0.125rem 0.375rem;
    background: var(--primary);
    color: white;
    border-radius: 3px;
    text-transform: capitalize;
  }

  .supplement-details {
    font-size: 0.875rem;
    margin-top: 0.25rem;
  }

  .supplement-notes {
    font-size: 0.875rem;
    margin-top: 0.25rem;
  }

  @media (max-width: 768px) {
    .form-row {
      grid-template-columns: 1fr;
    }

    .supplement-item {
      flex-direction: column;
      align-items: flex-start;
      gap: 0.5rem;
    }

    .supplement-item button {
      width: 100%;
    }
  }
</style>
