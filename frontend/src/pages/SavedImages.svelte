<script>
  import { onMount } from 'svelte';
  import { images, ai, foodEntries, dailyLogs } from '../lib/api.js';
  import { selectedDate } from '../lib/stores.js';

  let savedImages = [];
  let loading = false;
  let error = '';
  let analyzing = false;
  let analysisResult = null;
  let selectedImageId = null;
  let currentDate;
  let currentLog = null;

  selectedDate.subscribe(async value => {
    currentDate = value;
    if (currentDate) {
      currentLog = await dailyLogs.getByDate(currentDate);
    }
  });
  let itemMealTypes = {}; // Track meal type for each item
  let itemServingMultipliers = {}; // Track serving multiplier for each item
  let analysisNotes = ''; // Custom notes for AI analysis
  let showNotesInput = {}; // Track which images show notes input

  onMount(async () => {
    await loadImages();
    currentLog = await dailyLogs.getByDate(currentDate);
  });

  async function loadImages() {
    try {
      loading = true;
      error = '';
      savedImages = await images.getAll();
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }

  async function handleFileUpload(event) {
    const files = Array.from(event.target.files);
    if (files.length === 0) return;

    try {
      loading = true;
      await images.uploadMultiple(files);
      await loadImages();
      event.target.value = '';
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }

  async function handleDelete(imageId) {
    if (!confirm('Delete this image?')) return;

    try {
      await images.delete(imageId);
      await loadImages();
    } catch (err) {
      error = err.message;
    }
  }

  async function handleAnalyze(imageId, forceReanalyze = false) {
    try {
      analyzing = true;
      error = '';
      selectedImageId = imageId;

      // Automatically uses all images in the group
      analysisResult = await ai.analyzeImage(imageId, analysisNotes, forceReanalyze);

      // Initialize serving multipliers to 1 for each item
      if (analysisResult && analysisResult.items) {
        analysisResult.items.forEach((item, index) => {
          itemServingMultipliers[index] = 1;
        });
      }

      // Clear notes input after analysis
      analysisNotes = '';
      showNotesInput[imageId] = false;
    } catch (err) {
      error = `Analysis failed: ${err.message}`;
      analysisResult = null;
    } finally {
      analyzing = false;
    }
  }

  function calculateAdjustedNutrition(item, multiplier) {
    return {
      name: item.name,
      calories: Math.round(item.calories * multiplier),
      protein_g: parseFloat((item.protein_g * multiplier).toFixed(1)),
      carbs_g: parseFloat((item.carbs_g * multiplier).toFixed(1)),
      fat_g: parseFloat((item.fat_g * multiplier).toFixed(1)),
      fiber_g: parseFloat((item.fiber_g * multiplier).toFixed(1)),
      sugar_g: parseFloat((item.sugar_g * multiplier).toFixed(1)),
      serving_size: multiplier === 1 ? item.serving_size : `${multiplier}x ${item.serving_size}`,
      micronutrients: item.micronutrients ? {
        vitamin_a_mcg: item.micronutrients.vitamin_a_mcg * multiplier,
        vitamin_c_mg: item.micronutrients.vitamin_c_mg * multiplier,
        vitamin_d_mcg: item.micronutrients.vitamin_d_mcg * multiplier,
        calcium_mg: item.micronutrients.calcium_mg * multiplier,
        iron_mg: item.micronutrients.iron_mg * multiplier,
        potassium_mg: item.micronutrients.potassium_mg * multiplier,
        sodium_mg: item.micronutrients.sodium_mg * multiplier
      } : null
    };
  }

  async function handleAddFood(item, mealType, index) {
    if (!currentLog) {
      error = 'Could not load daily log';
      return;
    }

    try {
      const multiplier = itemServingMultipliers[index] || 1;
      const adjustedItem = calculateAdjustedNutrition(item, multiplier);

      // Build AI notes with confidence and analysis details
      const aiNotes = `AI Analysis (Confidence: ${analysisResult.confidence})${analysisResult.notes ? '\n' + analysisResult.notes : ''}${analysisResult.is_cached ? '\n(Loaded from previous analysis)' : ''}`;

      await foodEntries.create({
        daily_log_id: currentLog.id,
        name: adjustedItem.name,
        calories: adjustedItem.calories,
        protein_g: adjustedItem.protein_g,
        carbs_g: adjustedItem.carbs_g,
        fat_g: adjustedItem.fat_g,
        fiber_g: adjustedItem.fiber_g || 0,
        sugar_g: adjustedItem.sugar_g || 0,
        serving_size: adjustedItem.serving_size,
        meal_type: mealType,
        image_path: selectedImageId,
        ai_notes: aiNotes,
        micronutrients: adjustedItem.micronutrients
      });

      analysisResult = null;
      error = '';
      // Success - item added, analysis closed
    } catch (err) {
      error = `Failed to add food: ${err.message}`;
    }
  }
</script>

<div class="container">
  <h1>Saved Images</h1>

  <div class="card">
    <h3>Upload Image(s)</h3>
    <p class="text-muted" style="margin-bottom: 0.5rem; font-size: 0.875rem;">
      Select multiple images of the same food from different angles for better portion size estimation
    </p>
    <input
      type="file"
      accept="image/*"
      capture="environment"
      multiple
      on:change={handleFileUpload}
    />
  </div>

  {#if error}
    <div class="error">{error}</div>
  {/if}

  {#if analyzing}
    <div class="card">
      <div class="loading">Analyzing image with AI...</div>
    </div>
  {/if}

  {#if analysisResult}
    <div class="card">
      <div class="flex-between">
        <div>
          <h3>Analysis Results</h3>
          <p class="text-muted">
            Confidence: {analysisResult.confidence}
            {#if analysisResult.is_cached}
              <span class="cached-badge">Previous Analysis</span>
            {/if}
          </p>
        </div>
        {#if analysisResult.is_cached}
          <button class="outline" on:click={() => handleAnalyze(selectedImageId, true)}>
            Re-analyze
          </button>
        {/if}
      </div>

      {#if analysisResult.notes}
        <p><em>{analysisResult.notes}</em></p>
      {/if}

      <h4 class="mt-2">Detected Items:</h4>
      <div class="detected-items">
        {#each analysisResult.items as item, index (item.name + index)}
          {@const multiplier = itemServingMultipliers[index] || 1}
          {@const adjusted = calculateAdjustedNutrition(item, multiplier)}
          <div class="detected-item">
            <div class="item-info">
              <strong>{item.name}</strong>
              <p class="text-muted">Base: {item.serving_size} • {item.calories} cal</p>
              {#if multiplier !== 1}
                <p class="adjusted-info">
                  Adjusted: {adjusted.serving_size} • {adjusted.calories} cal
                </p>
              {/if}
            </div>
            <div class="item-actions">
              <div class="serving-control">
                <label for="serving-{index}">Servings:</label>
                <input
                  id="serving-{index}"
                  type="number"
                  bind:value={itemServingMultipliers[index]}
                  min="0.25"
                  max="10"
                  step="0.25"
                  class="serving-input"
                />
              </div>
              <select bind:value={itemMealTypes[index]} class="meal-select">
                <option value="breakfast">Breakfast</option>
                <option value="lunch">Lunch</option>
                <option value="dinner">Dinner</option>
                <option value="snack">Snack</option>
              </select>
              <button class="primary" on:click={() => handleAddFood(item, itemMealTypes[index] || 'snack', index)}>
                Add ({adjusted.calories} cal)
              </button>
            </div>
          </div>
        {/each}
      </div>

      <button class="outline mt-2" on:click={() => analysisResult = null}>
        Close Results
      </button>
    </div>
  {/if}

  {#if loading}
    <div class="loading">Loading images...</div>
  {:else if savedImages.length === 0}
    <div class="card">
      <p class="text-muted text-center">No images saved yet. Upload your first food photo!</p>
    </div>
  {:else}
    <div class="images-grid">
      {#each savedImages as imageGroup (imageGroup.id)}
        <div class="image-card">
          <!-- Show all images in the group -->
          <div class="image-group-display">
            {#if imageGroup.group_images && imageGroup.group_images.length > 1}
              <div class="multi-image-grid">
                {#each imageGroup.group_images as img (img.id)}
                  <img
                    src={images.getImageUrl(img.id)}
                    alt="Food view"
                    class="group-image"
                  />
                {/each}
              </div>
              <p class="image-count">{imageGroup.image_count} views</p>
            {:else}
              <img
                src={images.getImageUrl(imageGroup.id)}
                alt={imageGroup.description || 'Food image'}
                class="single-image"
              />
            {/if}
          </div>

          <div class="image-info">
            {#if imageGroup.description}
              <p class="text-muted">{imageGroup.description}</p>
            {/if}
            <small class="text-muted">{imageGroup.created_at}</small>
            {#if imageGroup.analyzed && imageGroup.analysis_result}
              <p class="previous-analysis">
                ✓ Previously analyzed
              </p>
            {/if}
          </div>

          {#if showNotesInput[imageGroup.id]}
            <div class="notes-input">
              <label for="notes-{imageGroup.id}">Custom instructions for AI:</label>
              <textarea
                id="notes-{imageGroup.id}"
                bind:value={analysisNotes}
                placeholder="e.g., 'This is a large portion' or 'Include the drink on the side'"
                rows="2"
              ></textarea>
            </div>
          {/if}

          <div class="image-actions">
            <button
              class="outline"
              on:click={() => showNotesInput[imageGroup.id] = !showNotesInput[imageGroup.id]}
            >
              {showNotesInput[imageGroup.id] ? 'Hide' : 'Add'} Notes
            </button>
            <button class="primary" on:click={() => handleAnalyze(imageGroup.id)}>
              Analyze
            </button>
            <button class="danger" on:click={() => handleDelete(imageGroup.id)}>
              Delete
            </button>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .images-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1rem;
  }

  .image-card {
    background: var(--white);
    border-radius: 8px;
    box-shadow: var(--shadow);
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }

  .image-group-display {
    position: relative;
  }

  .single-image {
    width: 100%;
    height: 200px;
    object-fit: cover;
  }

  .multi-image-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 2px;
    background: #fff;
  }

  .group-image {
    width: 100%;
    height: 140px;
    object-fit: cover;
  }

  .image-count {
    position: absolute;
    bottom: 0.5rem;
    right: 0.5rem;
    background: rgba(0, 0, 0, 0.7);
    color: white;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 500;
  }

  .image-card img {
    width: 100%;
    height: 200px;
    object-fit: cover;
  }

  .image-info {
    padding: 1rem;
    flex: 1;
  }

  .image-actions {
    padding: 0 1rem 1rem;
    display: flex;
    gap: 0.5rem;
  }

  .image-actions button {
    flex: 1;
  }

  .detected-items {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-top: 1rem;
  }

  .detected-item {
    padding: 1rem;
    background: var(--bg);
    border-radius: 4px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
  }

  .item-info {
    flex: 1;
  }

  .item-info p {
    margin: 0.25rem 0;
  }

  .item-actions {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    min-width: 150px;
  }

  .meal-select {
    padding: 0.5rem;
    border: 1px solid var(--border);
    border-radius: 4px;
    font-size: 0.875rem;
  }

  .serving-control {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .serving-control label {
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

  .adjusted-info {
    color: var(--primary);
    font-weight: 600;
    margin-top: 0.25rem;
  }

  .cached-badge {
    display: inline-block;
    background: #e3f2fd;
    color: #1976D2;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    margin-left: 0.5rem;
  }

  .previous-analysis {
    color: var(--primary);
    font-size: 0.875rem;
    margin-top: 0.5rem;
    font-weight: 500;
  }

  .notes-input {
    padding: 0 1rem 1rem;
  }

  .notes-input label {
    display: block;
    margin-bottom: 0.5rem;
    font-size: 0.875rem;
    font-weight: 500;
  }

  .notes-input textarea {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid var(--border);
    border-radius: 4px;
    font-family: inherit;
    resize: vertical;
  }

  @media (max-width: 768px) {
    .detected-item {
      flex-direction: column;
      align-items: stretch;
    }

    .item-actions {
      width: 100%;
      min-width: auto;
    }

    .serving-control {
      justify-content: space-between;
    }
  }
</style>
