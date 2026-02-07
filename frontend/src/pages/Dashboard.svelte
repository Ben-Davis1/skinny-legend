<script>
  import { onMount, tick } from 'svelte';
  import { dailyLogs, foodEntries, barcode, profile } from '../lib/api.js';
  import { selectedDate } from '../lib/stores.js';
  import FoodEntry from '../components/FoodEntry.svelte';
  import WaterTracker from '../components/WaterTracker.svelte';
  import BarcodeScanner from '../components/BarcodeScanner.svelte';
  import RecentFoods from '../components/RecentFoods.svelte';
  import ExerciseLogger from '../components/ExerciseLogger.svelte';
  import SupplementLogger from '../components/SupplementLogger.svelte';
  import RecentSupplements from '../components/RecentSupplements.svelte';
  import WorkoutTracker from '../components/WorkoutTracker.svelte';
  import RecentWorkouts from '../components/RecentWorkouts.svelte';

  let currentDate;
  selectedDate.subscribe(value => {
    currentDate = value;
    if (currentDate) {
      loadTodayLog();
    }
  });
  let dailyLog = null;
  let entries = [];
  let loading = true;
  let error = '';
  let showScanner = false;
  let scannedProduct = null;
  let scannedMealType = 'snack';
  let expandedEntry = null;
  let waterTarget = 2500; // Default 2.5L
  let addingItem = false;

  onMount(async () => {
    await loadTodayLog();
    await loadWaterTarget();
  });

  async function loadWaterTarget() {
    try {
      const userProfile = await profile.get();
      if (userProfile && userProfile.water_target_ml) {
        waterTarget = userProfile.water_target_ml;
      }
    } catch (err) {
      console.error('Failed to load water target:', err);
    }
  }

  async function loadTodayLog() {
    if (!currentDate) return;
    try {
      loading = true;
      error = '';
      dailyLog = await dailyLogs.getByDate(currentDate);
      await loadEntries();
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }

  async function loadEntries() {
    if (!dailyLog) return;
    try {
      entries = await foodEntries.getByLog(dailyLog.id);
    } catch (err) {
      console.error('Error loading entries:', err);
    }
  }

  async function handleSaveEntry(event) {
    const scrollPos = window.scrollY;
    try {
      addingItem = true;
      await foodEntries.create(event.detail);
      await loadTodayLog();
      await tick();
      window.scrollTo(0, scrollPos);
    } catch (err) {
      error = err.message;
    } finally {
      addingItem = false;
    }
  }

  async function handleQuickAddFood(event) {
    const scrollPos = window.scrollY;
    try {
      addingItem = true;
      const foodData = event.detail;
      await foodEntries.create({
        daily_log_id: dailyLog.id,
        ...foodData
        // meal_type is already included in foodData
      });
      await loadTodayLog();
      await tick();
      window.scrollTo(0, scrollPos);
    } catch (err) {
      error = err.message;
    } finally {
      addingItem = false;
    }
  }

  async function handleDeleteEntry(entryId) {
    if (!confirm('Delete this food entry?')) return;

    const scrollPos = window.scrollY;
    try {
      await foodEntries.delete(entryId);
      await loadTodayLog();
      await tick();
      window.scrollTo(0, scrollPos);
    } catch (err) {
      error = err.message;
    }
  }

  async function handleWaterUpdate(event) {
    const scrollPos = window.scrollY;
    try {
      await dailyLogs.update(dailyLog.id, {
        total_water_ml: event.detail,
        exercise_minutes: dailyLog.exercise_minutes,
        notes: dailyLog.notes
      });
      await loadTodayLog();
      await tick();
      window.scrollTo(0, scrollPos);
    } catch (err) {
      error = err.message;
    }
  }

  async function handleExerciseUpdate() {
    try {
      await dailyLogs.update(dailyLog.id, {
        total_water_ml: dailyLog.total_water_ml,
        exercise_minutes: dailyLog.exercise_minutes,
        notes: dailyLog.notes
      });
    } catch (err) {
      error = err.message;
    }
  }

  async function handleBarcodeScan(event) {
    const code = event.detail;
    try {
      const product = await barcode.lookup(code);
      product.barcode = code;
      scannedProduct = product;
      showScanner = false;
    } catch (err) {
      error = `Barcode lookup failed: ${err.message}`;
    }
  }

  async function addScannedProduct() {
    if (!scannedProduct) return;

    const scrollPos = window.scrollY;
    try {
      addingItem = true;
      const newEntry = {
        daily_log_id: dailyLog.id,
        name: scannedProduct.name,
        calories: scannedProduct.calories,
        protein_g: scannedProduct.protein_g,
        carbs_g: scannedProduct.carbs_g,
        fat_g: scannedProduct.fat_g,
        fiber_g: scannedProduct.fiber_g,
        sugar_g: scannedProduct.sugar_g,
        serving_size: scannedProduct.serving_size,
        meal_type: scannedMealType,
        barcode: scannedProduct.barcode,
        micronutrients: scannedProduct.micronutrients
      };

      await foodEntries.create(newEntry);
      await loadTodayLog();
      await tick();
      window.scrollTo(0, scrollPos);
      scannedProduct = null;
    } catch (err) {
      error = `Failed to add food: ${err.message}`;
    } finally {
      addingItem = false;
    }
  }

  $: totalMacros = entries.reduce((acc, entry) => ({
    protein: acc.protein + entry.protein_g,
    carbs: acc.carbs + entry.carbs_g,
    fat: acc.fat + entry.fat_g
  }), { protein: 0, carbs: 0, fat: 0 });

  function getCalorieColorClass(current, goal) {
    if (!goal) return '';
    const percentage = (current / goal) * 100;
    if (percentage > 100) return 'over-goal';
    if (percentage >= 90) return 'near-goal';
    return '';
  }

  function getMacroColorClass(current, target) {
    if (!target) return '';
    if (current > target) return 'over-target';
    return '';
  }
</script>

<div class="container">
  <h1>Daily Log - {currentDate}</h1>

  {#if addingItem}
    <div class="loading-banner">
      Adding item...
    </div>
  {/if}

  {#if error}
    <div class="error">{error}</div>
  {/if}

  {#if loading}
    <div class="loading">Loading...</div>
  {:else if dailyLog}
    <div class="grid grid-2">
      <div>
        <FoodEntry
          dailyLogId={dailyLog.id}
          on:save={handleSaveEntry}
        />

        <RecentFoods on:add={handleQuickAddFood} />

        <div class="card">
          <h3>Quick Add Options</h3>
          <button class="primary" on:click={() => showScanner = !showScanner}>
            {showScanner ? 'Hide' : 'Show'} Barcode Scanner
          </button>
        </div>

        {#if showScanner}
          <BarcodeScanner on:scan={handleBarcodeScan} />
        {/if}

        {#if scannedProduct}
          <div class="card">
            <h3>Scanned Product</h3>
            <div class="scanned-product">
              <div class="product-info">
                <strong>{scannedProduct.name}</strong>
                {#if scannedProduct.brand}
                  <p class="text-muted">{scannedProduct.brand}</p>
                {/if}
                <p class="text-muted">{scannedProduct.serving_size}</p>
                <p>
                  {scannedProduct.calories} cal •
                  P: {scannedProduct.protein_g}g,
                  C: {scannedProduct.carbs_g}g,
                  F: {scannedProduct.fat_g}g
                </p>
              </div>
              <div class="product-actions">
                <label for="barcode-meal">Meal Type</label>
                <select id="barcode-meal" bind:value={scannedMealType}>
                  <option value="breakfast">Breakfast</option>
                  <option value="lunch">Lunch</option>
                  <option value="dinner">Dinner</option>
                  <option value="snack">Snack</option>
                </select>
                <button class="primary" on:click={addScannedProduct}>
                  Add to Log
                </button>
                <button class="outline" on:click={() => scannedProduct = null}>
                  Cancel
                </button>
              </div>
            </div>
          </div>
        {/if}
      </div>

      <div>
        <div class="card summary">
          <h3>Daily Summary</h3>
          <div class="stat">
            <span class="stat-label">Total Calories</span>
            <span class="stat-value {getCalorieColorClass(dailyLog.total_calories, dailyLog.calorie_goal)}">
              {Math.round(dailyLog.total_calories)} / {dailyLog.calorie_goal || 2000}
            </span>
          </div>
          <div class="stat">
            <span class="stat-label">Protein</span>
            <span class="stat-value {getMacroColorClass(totalMacros.protein, dailyLog.protein_target_g)}">
              {Math.round(totalMacros.protein)}{dailyLog.protein_target_g ? ` / ${Math.round(dailyLog.protein_target_g)}` : ''}g
            </span>
          </div>
          <div class="stat">
            <span class="stat-label">Carbs</span>
            <span class="stat-value {getMacroColorClass(totalMacros.carbs, dailyLog.carbs_target_g)}">
              {Math.round(totalMacros.carbs)}{dailyLog.carbs_target_g ? ` / ${Math.round(dailyLog.carbs_target_g)}` : ''}g
            </span>
          </div>
          <div class="stat">
            <span class="stat-label">Fat</span>
            <span class="stat-value {getMacroColorClass(totalMacros.fat, dailyLog.fat_target_g)}">
              {Math.round(totalMacros.fat)}{dailyLog.fat_target_g ? ` / ${Math.round(dailyLog.fat_target_g)}` : ''}g
            </span>
          </div>
        </div>

        <WaterTracker
          totalWaterMl={dailyLog.total_water_ml}
          waterTarget={waterTarget}
          on:update={handleWaterUpdate}
        />

        <ExerciseLogger
          dailyLogId={dailyLog.id}
          on:update={loadTodayLog}
        />

        <WorkoutTracker
          dailyLogId={dailyLog.id}
          on:update={loadTodayLog}
        />

        <SupplementLogger
          dailyLogId={dailyLog.id}
          on:update={loadTodayLog}
        />

        <RecentSupplements
          dailyLogId={dailyLog.id}
          on:update={loadTodayLog}
        />
      </div>
    </div>

    <div class="card">
      <h3>Food Entries ({entries.length})</h3>
      {#if entries.length === 0}
        <p class="text-muted">No food entries yet. Add your first meal above!</p>
      {:else}
        <div class="entries-list">
          {#each entries as entry (entry.id)}
            <div class="entry-item" class:expanded={expandedEntry === entry.id}>
              <div class="entry-info" on:click={() => expandedEntry = expandedEntry === entry.id ? null : entry.id}>
                <div class="entry-name">
                  <strong>{entry.name}</strong>
                  {#if entry.meal_type}
                    <span class="meal-badge">{entry.meal_type}</span>
                  {/if}
                  <span class="expand-icon">{expandedEntry === entry.id ? '▼' : '▶'}</span>
                </div>
                <div class="entry-details text-muted">
                  {entry.serving_size} • {entry.calories} cal •
                  P: {entry.protein_g}g, C: {entry.carbs_g}g, F: {entry.fat_g}g
                </div>

                {#if expandedEntry === entry.id}
                  <div class="entry-expanded">
                    <h4>Detailed Nutrition</h4>
                    <div class="nutrition-grid">
                      <div class="nutrition-item">
                        <span class="label">Protein:</span>
                        <span class="value">{entry.protein_g}g</span>
                      </div>
                      <div class="nutrition-item">
                        <span class="label">Carbs:</span>
                        <span class="value">{entry.carbs_g}g</span>
                      </div>
                      <div class="nutrition-item">
                        <span class="label">Fat:</span>
                        <span class="value">{entry.fat_g}g</span>
                      </div>
                      <div class="nutrition-item">
                        <span class="label">Fiber:</span>
                        <span class="value">{entry.fiber_g}g</span>
                      </div>
                      <div class="nutrition-item">
                        <span class="label">Sugar:</span>
                        <span class="value">{entry.sugar_g}g</span>
                      </div>
                      <div class="nutrition-item">
                        <span class="label">Serving:</span>
                        <span class="value">{entry.serving_size}</span>
                      </div>
                    </div>
                    {#if entry.ai_notes}
                      <div class="ai-reasoning">
                        <strong>AI Analysis:</strong>
                        <p>{entry.ai_notes}</p>
                      </div>
                    {/if}
                    {#if entry.barcode}
                      <p class="source-info">
                        <strong>Source:</strong> Barcode scan ({entry.barcode})
                      </p>
                    {/if}
                    {#if entry.image_path && !entry.ai_notes}
                      <p class="source-info">
                        <strong>Source:</strong> AI image analysis
                      </p>
                    {/if}
                  </div>
                {/if}
              </div>
              <button class="danger" on:click|stopPropagation={() => handleDeleteEntry(entry.id)}>
                Delete
              </button>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .loading-banner {
    position: fixed;
    top: 80px;
    left: 50%;
    transform: translateX(-50%);
    background: #2196F3;
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    z-index: 1000;
    animation: slideDown 0.3s ease;
  }

  @keyframes slideDown {
    from {
      opacity: 0;
      transform: translateX(-50%) translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateX(-50%) translateY(0);
    }
  }

  .summary .stat {
    display: flex;
    justify-content: space-between;
    padding: 0.75rem 0;
    border-bottom: 1px solid var(--border);
  }

  .summary .stat:last-child {
    border-bottom: none;
  }

  .stat-label {
    font-weight: 500;
  }

  .stat-value {
    font-size: 1.25rem;
    font-weight: bold;
    color: var(--primary);
  }

  .stat-value.near-goal {
    color: #FF9800; /* Orange */
  }

  .stat-value.over-goal,
  .stat-value.over-target {
    color: #F44336; /* Red */
  }

  .entries-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .entry-item {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding: 1rem;
    background: var(--bg);
    border-radius: 4px;
    transition: all 0.2s;
  }

  .entry-item.expanded {
    background: var(--white);
    box-shadow: var(--shadow);
  }

  .entry-info {
    flex: 1;
    cursor: pointer;
  }

  .entry-name {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.25rem;
  }

  .expand-icon {
    margin-left: auto;
    color: var(--text-light);
    font-size: 0.75rem;
  }

  .meal-badge {
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
    background: var(--primary);
    color: white;
    border-radius: 4px;
    text-transform: capitalize;
  }

  .entry-details {
    font-size: 0.875rem;
  }

  .entry-expanded {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border);
  }

  .entry-expanded h4 {
    font-size: 0.875rem;
    margin-bottom: 0.75rem;
    color: var(--text-light);
  }

  .nutrition-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
    margin-bottom: 1rem;
  }

  .nutrition-item {
    display: flex;
    justify-content: space-between;
    padding: 0.5rem;
    background: var(--bg);
    border-radius: 4px;
  }

  .nutrition-item .label {
    font-weight: 500;
    color: var(--text-light);
  }

  .nutrition-item .value {
    font-weight: 600;
  }

  .ai-reasoning {
    margin-top: 1rem;
    padding: 0.75rem;
    background: #e3f2fd;
    border-left: 3px solid #2196F3;
    border-radius: 4px;
  }

  .ai-reasoning strong {
    color: #1976D2;
    display: block;
    margin-bottom: 0.5rem;
  }

  .ai-reasoning p {
    font-size: 0.875rem;
    color: var(--text);
    margin: 0;
    white-space: pre-wrap;
  }

  .source-info {
    font-size: 0.875rem;
    color: var(--text-light);
    margin-top: 0.5rem;
  }

  .form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
  }

  .scanned-product {
    display: flex;
    gap: 1rem;
    padding: 1rem;
    background: var(--bg);
    border-radius: 4px;
  }

  .product-info {
    flex: 1;
  }

  .product-info p {
    margin: 0.25rem 0;
  }

  .product-actions {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    min-width: 150px;
  }

  .product-actions label {
    font-size: 0.875rem;
    font-weight: 500;
  }

  .product-actions select {
    padding: 0.5rem;
    border: 1px solid var(--border);
    border-radius: 4px;
  }

  @media (max-width: 768px) {
    .scanned-product {
      flex-direction: column;
    }

    .product-actions {
      width: 100%;
      min-width: auto;
    }
  }
</style>
