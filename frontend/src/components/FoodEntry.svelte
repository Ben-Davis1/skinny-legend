<script>
  import { createEventDispatcher } from 'svelte';

  export let entry = null;
  export let dailyLogId = null;

  const dispatch = createEventDispatcher();

  let formData = {
    name: '',
    calories: 0,
    protein_g: 0,
    carbs_g: 0,
    fat_g: 0,
    fiber_g: 0,
    sugar_g: 0,
    meal_type: 'breakfast',
    serving_size: '1 serving'
  };

  $: if (entry) {
    formData = { ...entry };
  }

  function handleSubmit() {
    if (!formData.name || formData.calories <= 0) {
      return;
    }

    dispatch('save', { ...formData, daily_log_id: dailyLogId });
    resetForm();
  }

  function resetForm() {
    formData = {
      name: '',
      calories: 0,
      protein_g: 0,
      carbs_g: 0,
      fat_g: 0,
      fiber_g: 0,
      sugar_g: 0,
      meal_type: 'breakfast',
      serving_size: '1 serving'
    };
  }
</script>

<div class="food-entry-form card">
  <h3>Add Food Entry</h3>

  <form on:submit|preventDefault={handleSubmit}>
    <div class="form-group">
      <label for="name">Food Name *</label>
      <input
        id="name"
        type="text"
        bind:value={formData.name}
        placeholder="e.g., Chicken breast"
        required
      />
    </div>

    <div class="form-row">
      <div class="form-group">
        <label for="meal_type">Meal Type</label>
        <select id="meal_type" bind:value={formData.meal_type}>
          <option value="breakfast">Breakfast</option>
          <option value="lunch">Lunch</option>
          <option value="dinner">Dinner</option>
          <option value="snack">Snack</option>
        </select>
      </div>

      <div class="form-group">
        <label for="serving_size">Serving Size</label>
        <input
          id="serving_size"
          type="text"
          bind:value={formData.serving_size}
          placeholder="e.g., 100g"
        />
      </div>
    </div>

    <div class="form-row">
      <div class="form-group">
        <label for="calories">Calories *</label>
        <input
          id="calories"
          type="number"
          bind:value={formData.calories}
          min="0"
          step="1"
          required
        />
      </div>

      <div class="form-group">
        <label for="protein">Protein (g)</label>
        <input
          id="protein"
          type="number"
          bind:value={formData.protein_g}
          min="0"
          step="0.1"
        />
      </div>
    </div>

    <div class="form-row">
      <div class="form-group">
        <label for="carbs">Carbs (g)</label>
        <input
          id="carbs"
          type="number"
          bind:value={formData.carbs_g}
          min="0"
          step="0.1"
        />
      </div>

      <div class="form-group">
        <label for="fat">Fat (g)</label>
        <input
          id="fat"
          type="number"
          bind:value={formData.fat_g}
          min="0"
          step="0.1"
        />
      </div>
    </div>

    <div class="form-row">
      <div class="form-group">
        <label for="fiber">Fiber (g)</label>
        <input
          id="fiber"
          type="number"
          bind:value={formData.fiber_g}
          min="0"
          step="0.1"
        />
      </div>

      <div class="form-group">
        <label for="sugar">Sugar (g)</label>
        <input
          id="sugar"
          type="number"
          bind:value={formData.sugar_g}
          min="0"
          step="0.1"
        />
      </div>
    </div>

    <div class="form-actions">
      <button type="submit" class="primary">Add Food</button>
      <button type="button" class="outline" on:click={resetForm}>Clear</button>
    </div>
  </form>
</div>

<style>
  .food-entry-form {
    margin-bottom: 2rem;
  }

  .form-group {
    margin-bottom: 1rem;
  }

  .form-group label {
    display: block;
    margin-bottom: 0.25rem;
    font-weight: 500;
  }

  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }

  .form-actions {
    display: flex;
    gap: 1rem;
    margin-top: 1.5rem;
  }

  @media (max-width: 768px) {
    .form-row {
      grid-template-columns: 1fr;
    }
  }
</style>
