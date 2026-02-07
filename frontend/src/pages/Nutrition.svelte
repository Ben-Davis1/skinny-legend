<script>
  import { onMount } from 'svelte';
  import { nutrition } from '../lib/api.js';
  import { push } from 'svelte-spa-router';

  export let params = {};

  let selectedDay = params.date || new Date().toISOString().split('T')[0];
  let nutritionData = null;
  let loading = false;
  let error = '';
  let expandedMicro = null; // Track which micronutrient is expanded

  $: if (params.date) {
    selectedDay = params.date;
    loadNutrition();
  }

  const defaultTargets = {
    'Vitamin A': { amount: 900, unit: 'mcg' },
    'Vitamin C': { amount: 90, unit: 'mg' },
    'Vitamin D': { amount: 20, unit: 'mcg' },
    'Calcium': { amount: 1000, unit: 'mg' },
    'Iron': { amount: 18, unit: 'mg' },
    'Potassium': { amount: 3500, unit: 'mg' }
  };

  onMount(async () => {
    await loadNutrition();
  });

  async function loadNutrition() {
    try {
      loading = true;
      error = '';
      nutritionData = await nutrition.getBreakdown(selectedDay);
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }

  function getProgress(current, target) {
    return Math.min((current / target) * 100, 100);
  }

  function formatNumber(num) {
    return Math.round(num * 10) / 10;
  }
</script>

<div class="container">
  <div class="flex-between mb-2">
    <h1>Nutrition Breakdown</h1>
    <button class="outline" on:click={() => push('/history')}>
      ← Back to History
    </button>
  </div>

  <div class="card">
    <h2>{selectedDay}</h2>
  </div>

  {#if error}
    <div class="error">{error}</div>
  {/if}

  {#if loading}
    <div class="loading">Loading nutrition data...</div>
  {:else if nutritionData}
    <div class="grid grid-2">
      <div class="card">
        <h3>Water Intake</h3>
        <div class="big-stat">
          <span class="stat-value">{(nutritionData.daily_log.total_water_ml / 1000).toFixed(1)}L</span>
          <span class="stat-label">({Math.floor(nutritionData.daily_log.total_water_ml / 250)} cups)</span>
        </div>
      </div>

      <div class="card">
        <h3>Exercise</h3>
        <div class="big-stat">
          <span class="stat-value">{nutritionData.daily_log.exercise_minutes}</span>
          <span class="stat-label">minutes</span>
        </div>
      </div>
    </div>

    <div class="grid grid-2">
      <div class="card">
        <h3>Macronutrients</h3>
        <div class="macro-breakdown">
          <div class="macro-item">
            <div class="macro-header">
              <span class="macro-label">Protein</span>
              <span class="macro-value">{formatNumber(nutritionData.macros.protein_g)} / {nutritionData.daily_log.protein_target_g || 150}g</span>
            </div>
            <div class="macro-bar protein">
              <div class="macro-fill" style="width: {getProgress(nutritionData.macros.protein_g, nutritionData.daily_log.protein_target_g || 150)}%"></div>
            </div>
          </div>

          <div class="macro-item">
            <div class="macro-header">
              <span class="macro-label">Carbohydrates</span>
              <span class="macro-value">{formatNumber(nutritionData.macros.carbs_g)} / {nutritionData.daily_log.carbs_target_g || 200}g</span>
            </div>
            <div class="macro-bar carbs">
              <div class="macro-fill" style="width: {getProgress(nutritionData.macros.carbs_g, nutritionData.daily_log.carbs_target_g || 200)}%"></div>
            </div>
          </div>

          <div class="macro-item">
            <div class="macro-header">
              <span class="macro-label">Fat</span>
              <span class="macro-value">{formatNumber(nutritionData.macros.fat_g)} / {nutritionData.daily_log.fat_target_g || 70}g</span>
            </div>
            <div class="macro-bar fat">
              <div class="macro-fill" style="width: {getProgress(nutritionData.macros.fat_g, nutritionData.daily_log.fat_target_g || 70)}%"></div>
            </div>
          </div>

          <div class="macro-item">
            <div class="macro-header">
              <span class="macro-label">Fiber</span>
              <span class="macro-value">{formatNumber(nutritionData.macros.fiber_g)} / 30g</span>
            </div>
            <div class="macro-bar fiber">
              <div class="macro-fill" style="width: {getProgress(nutritionData.macros.fiber_g, 30)}%"></div>
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <h3>Total Calories</h3>
        <div class="calorie-display">
          <span class="calorie-value">{Math.round(nutritionData.daily_log.total_calories)}</span>
          <span class="calorie-label">
            {#if nutritionData.daily_log.calorie_goal}
              / {Math.round(nutritionData.daily_log.calorie_goal)} goal
            {:else}
              calories
            {/if}
          </span>
        </div>
        <div class="calorie-breakdown">
          <div class="breakdown-item">
            <span class="dot protein-dot"></span>
            <span>Protein: {Math.round((nutritionData.macros.protein_g * 4) / nutritionData.daily_log.total_calories * 100)}%</span>
          </div>
          <div class="breakdown-item">
            <span class="dot carbs-dot"></span>
            <span>Carbs: {Math.round((nutritionData.macros.carbs_g * 4) / nutritionData.daily_log.total_calories * 100)}%</span>
          </div>
          <div class="breakdown-item">
            <span class="dot fat-dot"></span>
            <span>Fat: {Math.round((nutritionData.macros.fat_g * 9) / nutritionData.daily_log.total_calories * 100)}%</span>
          </div>
        </div>
      </div>
    </div>

    <div class="card">
      <h3>Micronutrients</h3>
      <div class="micronutrients">
        <div class="micro-item" class:expanded={expandedMicro === 'vitamin_a_mcg'}>
          <div class="micro-header clickable" on:click={() => expandedMicro = expandedMicro === 'vitamin_a_mcg' ? null : 'vitamin_a_mcg'}>
            <span>Vitamin A {expandedMicro === 'vitamin_a_mcg' ? '▼' : '▶'}</span>
            <span>{formatNumber(nutritionData.micronutrients.vitamin_a_mcg)} / {defaultTargets['Vitamin A'].amount} mcg</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" style="width: {getProgress(nutritionData.micronutrients.vitamin_a_mcg, defaultTargets['Vitamin A'].amount)}%"></div>
          </div>
          {#if expandedMicro === 'vitamin_a_mcg' && nutritionData.micronutrient_sources?.vitamin_a_mcg}
            <div class="micro-sources">
              <strong>Sources:</strong>
              {#if nutritionData.micronutrient_sources.vitamin_a_mcg.length === 0}
                <p class="text-muted">No sources logged today</p>
              {:else}
                <ul>
                  {#each nutritionData.micronutrient_sources.vitamin_a_mcg as source}
                    <li>
                      <span class="source-name">{source.name}</span>
                      <span class="source-amount">{source.amount} mcg</span>
                      <span class="source-type {source.type}">{source.type}</span>
                    </li>
                  {/each}
                </ul>
              {/if}
            </div>
          {/if}
        </div>

        <div class="micro-item">
          <div class="micro-header">
            <span>Vitamin C</span>
            <span>{formatNumber(nutritionData.micronutrients.vitamin_c_mg)} / {defaultTargets['Vitamin C'].amount} mg</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" style="width: {getProgress(nutritionData.micronutrients.vitamin_c_mg, defaultTargets['Vitamin C'].amount)}%"></div>
          </div>
        </div>

        <div class="micro-item">
          <div class="micro-header">
            <span>Vitamin D</span>
            <span>{formatNumber(nutritionData.micronutrients.vitamin_d_mcg)} / {defaultTargets['Vitamin D'].amount} mcg</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" style="width: {getProgress(nutritionData.micronutrients.vitamin_d_mcg, defaultTargets['Vitamin D'].amount)}%"></div>
          </div>
        </div>

        <div class="micro-item">
          <div class="micro-header">
            <span>Calcium</span>
            <span>{formatNumber(nutritionData.micronutrients.calcium_mg)} / {defaultTargets['Calcium'].amount} mg</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" style="width: {getProgress(nutritionData.micronutrients.calcium_mg, defaultTargets['Calcium'].amount)}%"></div>
          </div>
        </div>

        <div class="micro-item">
          <div class="micro-header">
            <span>Iron</span>
            <span>{formatNumber(nutritionData.micronutrients.iron_mg)} / {defaultTargets['Iron'].amount} mg</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" style="width: {getProgress(nutritionData.micronutrients.iron_mg, defaultTargets['Iron'].amount)}%"></div>
          </div>
        </div>

        <div class="micro-item">
          <div class="micro-header">
            <span>Potassium</span>
            <span>{formatNumber(nutritionData.micronutrients.potassium_mg)} / {defaultTargets['Potassium'].amount} mg</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" style="width: {getProgress(nutritionData.micronutrients.potassium_mg, defaultTargets['Potassium'].amount)}%"></div>
          </div>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  .macro-breakdown {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .macro-item {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .macro-header {
    display: flex;
    justify-content: space-between;
    font-weight: 500;
  }

  .macro-bar {
    height: 24px;
    background: var(--bg);
    border-radius: 12px;
    overflow: hidden;
  }

  .macro-fill {
    height: 100%;
    transition: width 0.3s ease;
  }

  .macro-bar.protein .macro-fill { background: #FF6B6B; }
  .macro-bar.carbs .macro-fill { background: #4ECDC4; }
  .macro-bar.fat .macro-fill { background: #FFE66D; }
  .macro-bar.fiber .macro-fill { background: #95E1D3; }

  .calorie-display {
    text-align: center;
    margin: 2rem 0;
  }

  .calorie-value {
    display: block;
    font-size: 3rem;
    font-weight: bold;
    color: var(--primary);
  }

  .calorie-label {
    font-size: 1.25rem;
    color: var(--text-light);
  }

  .calorie-breakdown {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .breakdown-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
  }

  .protein-dot { background: #FF6B6B; }
  .carbs-dot { background: #4ECDC4; }
  .fat-dot { background: #FFE66D; }

  .micronutrients {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .micro-item {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    padding: 1rem;
    background: var(--white);
    border-radius: 8px;
    transition: all 0.2s;
  }

  .micro-item.expanded {
    background: var(--bg);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .micro-header {
    display: flex;
    justify-content: space-between;
    font-size: 0.875rem;
  }

  .micro-header.clickable {
    cursor: pointer;
    user-select: none;
  }

  .micro-header.clickable:hover {
    color: var(--primary);
  }

  .micro-sources {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border);
  }

  .micro-sources strong {
    display: block;
    margin-bottom: 0.5rem;
    font-size: 0.875rem;
    color: var(--text-light);
  }

  .micro-sources ul {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .micro-sources li {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem;
    background: var(--white);
    border-radius: 4px;
    font-size: 0.875rem;
  }

  .source-name {
    flex: 1;
    font-weight: 500;
  }

  .source-amount {
    color: var(--primary);
    font-weight: 600;
  }

  .source-type {
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    text-transform: capitalize;
  }

  .source-type.food {
    background: #e3f2fd;
    color: #1976D2;
  }

  .source-type.supplement {
    background: #f3e5f5;
    color: #7B1FA2;
  }

  .progress-bar {
    height: 20px;
    background: var(--bg);
    border-radius: 10px;
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    background: var(--primary);
    transition: width 0.3s ease;
  }

  .big-stat {
    text-align: center;
    padding: 2rem 1rem;
  }

  .big-stat .stat-value {
    display: block;
    font-size: 3rem;
    font-weight: bold;
    color: var(--primary);
    margin-bottom: 0.5rem;
  }

  .big-stat .stat-label {
    font-size: 1.25rem;
    color: var(--text-light);
  }

  .mb-2 {
    margin-bottom: 1rem;
  }

  .flex-between {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  @media (max-width: 768px) {
    .calorie-value {
      font-size: 2.5rem;
    }

    .big-stat .stat-value {
      font-size: 2.5rem;
    }

    .calorie-label,
    .big-stat .stat-label {
      font-size: 1rem;
    }

    .mb-2 {
      margin-bottom: 0.75rem;
    }

    .flex-between {
      flex-direction: column;
      align-items: flex-start;
      gap: 0.5rem;
    }

    .flex-between button {
      width: 100%;
    }
  }

  @media (max-width: 480px) {
    .calorie-value {
      font-size: 2rem;
    }

    .big-stat .stat-value {
      font-size: 2rem;
    }

    .big-stat {
      padding: 1.5rem 1rem;
    }

    .macro-breakdown,
    .micronutrients {
      gap: 1rem;
    }
  }
</style>
