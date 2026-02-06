<script>
  import { onMount, createEventDispatcher } from 'svelte';
  import { recentFoods } from '../lib/api.js';

  const dispatch = createEventDispatcher();

  let foods = [];
  let loading = true;
  let servingMultipliers = {}; // Track serving size multiplier for each food
  let mealTypes = {}; // Track meal type for each food
  let addingIndex = null; // Track which item is being added

  onMount(async () => {
    await loadRecentFoods();
  });

  async function loadRecentFoods() {
    try {
      loading = true;
      foods = await recentFoods.get();
      // Initialize multipliers to 1 and meal types to snack
      foods.forEach((food, index) => {
        servingMultipliers[index] = 1;
        mealTypes[index] = 'snack';
      });
    } catch (err) {
      console.error('Failed to load recent foods:', err);
    } finally {
      loading = false;
    }
  }

  function calculateAdjustedNutrition(food, multiplier) {
    return {
      name: food.name,
      calories: Math.round(food.calories * multiplier),
      protein_g: parseFloat((food.protein_g * multiplier).toFixed(1)),
      carbs_g: parseFloat((food.carbs_g * multiplier).toFixed(1)),
      fat_g: parseFloat((food.fat_g * multiplier).toFixed(1)),
      fiber_g: parseFloat((food.fiber_g * multiplier).toFixed(1)),
      sugar_g: parseFloat((food.sugar_g * multiplier).toFixed(1)),
      serving_size: `${multiplier}x ${food.serving_size}`
    };
  }

  async function handleQuickAdd(food, index) {
    addingIndex = index;
    const multiplier = servingMultipliers[index] || 1;
    const adjustedFood = calculateAdjustedNutrition(food, multiplier);
    const mealType = mealTypes[index] || 'snack';
    dispatch('add', { ...adjustedFood, meal_type: mealType });

    // Reset after a delay to allow parent to process
    setTimeout(() => {
      addingIndex = null;
    }, 2000);
  }
</script>

<div class="recent-foods card">
  <h3>Recently Used Foods</h3>

  {#if loading}
    <p class="text-muted">Loading...</p>
  {:else if foods.length === 0}
    <p class="text-muted">No recent foods yet. Start logging your meals!</p>
  {:else}
    <div class="foods-list scrollable">
      {#each foods as food, index (food.name + food.last_used)}
        <div class="food-item">
          <div class="food-info">
            <strong>{food.name}</strong>
            <p class="text-muted">
              {food.serving_size} • {food.calories} cal
            </p>
          </div>
          <div class="food-actions">
            <div class="serving-adjuster">
              <label for="multiplier-{index}">Servings:</label>
              <input
                id="multiplier-{index}"
                type="number"
                bind:value={servingMultipliers[index]}
                min="0.25"
                max="10"
                step="0.25"
                class="serving-input"
              />
            </div>
            <div class="meal-type-selector">
              <select bind:value={mealTypes[index]} class="meal-select">
                <option value="breakfast">Breakfast</option>
                <option value="lunch">Lunch</option>
                <option value="dinner">Dinner</option>
                <option value="snack">Snack</option>
              </select>
            </div>
            <div class="adjusted-cals">
              {calculateAdjustedNutrition(food, servingMultipliers[index]).calories} cal
            </div>
            <button class="primary" on:click={() => handleQuickAdd(food, index)} disabled={addingIndex === index}>
              {addingIndex === index ? '⏳' : 'Add'}
            </button>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .recent-foods {
    margin-bottom: 2rem;
  }

  .foods-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    max-height: 500px;
    overflow-y: auto;
    padding-right: 0.5rem;
  }

  .foods-list::-webkit-scrollbar {
    width: 8px;
  }

  .foods-list::-webkit-scrollbar-thumb {
    background: var(--border);
    border-radius: 4px;
  }

  .foods-list::-webkit-scrollbar-track {
    background: var(--bg);
  }

  .food-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem;
    background: var(--bg);
    border-radius: 4px;
    gap: 1rem;
  }

  .food-info {
    flex: 1;
  }

  .food-info p {
    margin: 0.25rem 0 0 0;
    font-size: 0.875rem;
  }

  .food-actions {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .serving-adjuster {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .serving-adjuster label {
    font-size: 0.875rem;
    font-weight: 500;
    white-space: nowrap;
  }

  .serving-input {
    width: 70px;
    padding: 0.4rem;
    border: 1px solid var(--border);
    border-radius: 4px;
    text-align: center;
  }

  .meal-type-selector {
    min-width: 120px;
  }

  .meal-select {
    width: 100%;
    padding: 0.4rem;
    border: 1px solid var(--border);
    border-radius: 4px;
    font-size: 0.875rem;
  }

  .adjusted-cals {
    font-weight: 600;
    color: var(--primary);
    min-width: 70px;
    text-align: right;
  }

  @media (max-width: 768px) {
    .food-item {
      flex-direction: column;
      align-items: stretch;
    }

    .food-actions {
      flex-direction: column;
      width: 100%;
    }

    .serving-adjuster {
      justify-content: space-between;
    }

    .adjusted-cals {
      text-align: center;
    }
  }
</style>
