<script>
  import { createEventDispatcher } from 'svelte';

  export let totalWaterMl = 0;
  export let waterTarget = 2500; // Default 2.5L

  const dispatch = createEventDispatcher();

  const cupSizes = [
    { label: '250ml (1 cup)', value: 250 },
    { label: '500ml (bottle)', value: 500 },
    { label: '1000ml (1L)', value: 1000 }
  ];

  let customAmount = 250;

  function addWater(amount) {
    totalWaterMl += amount;
    dispatch('update', totalWaterMl);
  }

  function removeWater(amount) {
    totalWaterMl = Math.max(0, totalWaterMl - amount);
    dispatch('update', totalWaterMl);
  }

  $: liters = (totalWaterMl / 1000).toFixed(2);
  $: cups = Math.floor(totalWaterMl / 250);
  $: targetLiters = (waterTarget / 1000).toFixed(1);
  $: progress = waterTarget > 0 ? Math.min((totalWaterMl / waterTarget) * 100, 100) : 0;
</script>

<div class="water-tracker card">
  <h3>Water Intake</h3>

  <div class="water-display">
    <div class="water-amount">
      <span class="amount">{liters}L</span>
      <span class="target text-muted">/ {targetLiters}L target</span>
    </div>
    <div class="water-visual">
      <div class="water-bar" style="width: {progress}%"></div>
    </div>
    <p class="progress-text text-muted">{Math.round(progress)}% of daily target</p>
  </div>

  <div class="quick-add">
    <h4>Quick Add</h4>
    <div class="button-group">
      {#each cupSizes as size}
        <button class="outline" on:click={() => addWater(size.value)}>
          + {size.label}
        </button>
      {/each}
    </div>
  </div>

  <div class="custom-amount">
    <label for="custom">Custom Amount (ml)</label>
    <div class="flex">
      <input
        id="custom"
        type="number"
        bind:value={customAmount}
        min="0"
        step="50"
        style="flex: 1;"
      />
      <button class="primary" on:click={() => addWater(customAmount)}>Add</button>
    </div>
  </div>

  {#if totalWaterMl > 0}
    <div class="reset-section">
      <button class="danger" on:click={() => { totalWaterMl = 0; dispatch('update', 0); }}>
        Reset Water
      </button>
    </div>
  {/if}
</div>

<style>
  .water-tracker {
    margin-bottom: 2rem;
  }

  .water-display {
    text-align: center;
    margin: 1.5rem 0;
  }

  .water-amount {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  .amount {
    font-size: 2.5rem;
    font-weight: bold;
    color: var(--primary);
  }

  .cups,
  .target {
    font-size: 1rem;
  }

  .progress-text {
    margin-top: 0.5rem;
    font-size: 0.875rem;
  }

  .water-visual {
    height: 30px;
    background: #e0f2f1;
    border-radius: 15px;
    overflow: hidden;
    position: relative;
  }

  .water-bar {
    height: 100%;
    background: linear-gradient(90deg, #4CAF50, #2196F3);
    transition: width 0.3s ease;
  }

  .quick-add {
    margin: 1.5rem 0;
  }

  .quick-add h4 {
    margin-bottom: 0.5rem;
  }

  .button-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .custom-amount {
    margin-top: 1rem;
  }

  .custom-amount label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
  }

  .reset-section {
    margin-top: 1rem;
    text-align: center;
  }
</style>