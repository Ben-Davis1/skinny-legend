<script>
  import { onMount } from 'svelte';
  import { profile, weightLogs } from '../lib/api.js';
  import { Chart, registerables } from 'chart.js';

  Chart.register(...registerables);

  let userProfile = null;
  let calculations = null;
  let loading = false;
  let error = '';
  let success = '';
  let editMode = false;
  let weightHistory = [];
  let weightChartInstance = null;

  let formData = {
    age: 30,
    weight_kg: 70,
    height_cm: 170,
    gender: 'female',
    activity_level: 'moderately_active',
    goal: 'maintain',
    protein_target_g: 150,
    carbs_target_g: 200,
    fat_target_g: 70,
    use_custom_targets: false,
    custom_calorie_goal: null,
    custom_protein_target_g: null,
    custom_carbs_target_g: null,
    custom_fat_target_g: null,
    custom_water_target_ml: null
  };

  onMount(async () => {
    await loadProfile();
    await loadWeightHistory();
  });

  async function loadProfile() {
    try {
      loading = true;
      error = '';
      userProfile = await profile.get();
      calculations = await profile.getCalculations();

      if (userProfile) {
        formData = {
          age: userProfile.age,
          weight_kg: userProfile.weight_kg,
          height_cm: userProfile.height_cm,
          gender: userProfile.gender,
          activity_level: userProfile.activity_level,
          goal: userProfile.goal,
          protein_target_g: userProfile.protein_target_g || 150,
          carbs_target_g: userProfile.carbs_target_g || 200,
          fat_target_g: userProfile.fat_target_g || 70,
          use_custom_targets: userProfile.use_custom_targets || false,
          custom_calorie_goal: userProfile.custom_calorie_goal,
          custom_protein_target_g: userProfile.custom_protein_target_g,
          custom_carbs_target_g: userProfile.custom_carbs_target_g,
          custom_fat_target_g: userProfile.custom_fat_target_g,
          custom_water_target_ml: userProfile.custom_water_target_ml
        };
      } else {
        editMode = true;
      }
    } catch (err) {
      if (err.message.includes('404') || err.message.includes('not found')) {
        editMode = true;
      } else {
        error = err.message;
      }
    } finally {
      loading = false;
    }
  }

  async function handleSubmit() {
    try {
      loading = true;
      error = '';
      success = '';

      if (userProfile) {
        await profile.update({ ...formData, user_id: 1 });
        success = 'Profile updated successfully!';
      } else {
        await profile.create({ ...formData, user_id: 1 });
        success = 'Profile created successfully!';
      }

      await loadProfile();
      editMode = false;
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }

  $: bmi = formData.weight_kg && formData.height_cm
    ? (formData.weight_kg / Math.pow(formData.height_cm / 100, 2)).toFixed(1)
    : 0;

  function getBMICategory(bmi) {
    if (bmi < 18.5) return { label: 'Underweight', color: '#FFC107' };
    if (bmi < 25) return { label: 'Normal', color: '#4CAF50' };
    if (bmi < 30) return { label: 'Overweight', color: '#FF9800' };
    return { label: 'Obese', color: '#F44336' };
  }

  $: bmiCategory = getBMICategory(bmi);

  async function loadWeightHistory() {
    try {
      weightHistory = await weightLogs.getAll();
      renderWeightChart();
    } catch (err) {
      console.error('Failed to load weight history:', err);
    }
  }

  function renderWeightChart() {
    if (weightChartInstance) {
      weightChartInstance.destroy();
    }

    const ctx = document.getElementById('weightChart');
    if (!ctx || weightHistory.length === 0) return;

    const labels = weightHistory.map(w => w.date);
    const weights = weightHistory.map(w => w.weight_kg);

    weightChartInstance = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: 'Weight (kg)',
          data: weights,
          borderColor: '#4CAF50',
          backgroundColor: 'rgba(76, 175, 80, 0.1)',
          tension: 0.4,
          fill: true
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: true,
            position: 'top'
          }
        },
        scales: {
          y: {
            beginAtZero: false
          }
        }
      }
    });
  }

  async function handleDeleteWeight(id) {
    if (!confirm('Delete this weight entry?')) return;

    try {
      await weightLogs.delete(id);
      await loadWeightHistory();
    } catch (err) {
      error = err.message;
    }
  }
</script>

<div class="container">
  <h1>Profile</h1>

  {#if error}
    <div class="error">{error}</div>
  {/if}

  {#if success}
    <div class="success">{success}</div>
  {/if}

  {#if loading && !userProfile}
    <div class="loading">Loading profile...</div>
  {:else}
    <div class="grid grid-2">
      <div class="card">
        <div class="flex-between">
          <h3>{userProfile ? 'Your Profile' : 'Create Profile'}</h3>
          {#if userProfile && !editMode}
            <button class="outline" on:click={() => editMode = true}>Edit</button>
          {/if}
        </div>

        {#if editMode}
          <form on:submit|preventDefault={handleSubmit}>
            <div class="form-group">
              <label for="age">Age *</label>
              <input
                id="age"
                type="number"
                bind:value={formData.age}
                min="1"
                max="120"
                required
              />
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="weight">Weight (kg) *</label>
                <input
                  id="weight"
                  type="number"
                  bind:value={formData.weight_kg}
                  min="1"
                  step="0.1"
                  required
                />
              </div>

              <div class="form-group">
                <label for="height">Height (cm) *</label>
                <input
                  id="height"
                  type="number"
                  bind:value={formData.height_cm}
                  min="1"
                  step="0.1"
                  required
                />
              </div>
            </div>

            <div class="form-group">
              <label for="gender">Gender *</label>
              <select id="gender" bind:value={formData.gender} required>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div class="form-group">
              <label for="activity">Activity Level *</label>
              <select id="activity" bind:value={formData.activity_level} required>
                <option value="sedentary">Sedentary (little or no exercise)</option>
                <option value="lightly_active">Lightly Active (1-3 days/week)</option>
                <option value="moderately_active">Moderately Active (3-5 days/week)</option>
                <option value="very_active">Very Active (6-7 days/week)</option>
                <option value="extra_active">Extra Active (very hard exercise & physical job)</option>
              </select>
            </div>

            <div class="form-group">
              <label for="goal">Goal *</label>
              <select id="goal" bind:value={formData.goal} required>
                <option value="lose">Lose Weight</option>
                <option value="maintain">Maintain Weight</option>
                <option value="gain">Gain Weight</option>
              </select>
            </div>

            <div class="custom-targets-section">
              <div class="flex-between">
                <h4>Daily Targets</h4>
                <label class="toggle-label">
                  <input
                    type="checkbox"
                    bind:checked={formData.use_custom_targets}
                  />
                  <span>Use Custom Targets</span>
                </label>
              </div>

              {#if !formData.use_custom_targets}
                <p class="text-muted" style="font-size: 0.875rem; margin-top: 0.5rem;">
                  Auto-calculated based on weight, activity, and goal
                </p>
              {:else}
                <div class="custom-targets-form">
                  <div class="form-row">
                    <div class="form-group">
                      <label for="custom-calories">Calories</label>
                      <input
                        id="custom-calories"
                        type="number"
                        bind:value={formData.custom_calorie_goal}
                        min="0"
                        step="50"
                        placeholder="e.g., 2000"
                      />
                    </div>

                    <div class="form-group">
                      <label for="custom-water">Water (ml)</label>
                      <input
                        id="custom-water"
                        type="number"
                        bind:value={formData.custom_water_target_ml}
                        min="0"
                        step="250"
                        placeholder="e.g., 2500"
                      />
                    </div>
                  </div>

                  <div class="form-row">
                    <div class="form-group">
                      <label for="custom-protein">Protein (g)</label>
                      <input
                        id="custom-protein"
                        type="number"
                        bind:value={formData.custom_protein_target_g}
                        min="0"
                        step="5"
                        placeholder="e.g., 150"
                      />
                    </div>

                    <div class="form-group">
                      <label for="custom-carbs">Carbs (g)</label>
                      <input
                        id="custom-carbs"
                        type="number"
                        bind:value={formData.custom_carbs_target_g}
                        min="0"
                        step="5"
                        placeholder="e.g., 200"
                      />
                    </div>

                    <div class="form-group">
                      <label for="custom-fat">Fat (g)</label>
                      <input
                        id="custom-fat"
                        type="number"
                        bind:value={formData.custom_fat_target_g}
                        min="0"
                        step="5"
                        placeholder="e.g., 70"
                      />
                    </div>
                  </div>
                </div>
              {/if}
            </div>

            <div class="form-actions">
              <button type="submit" class="primary" disabled={loading}>
                {loading ? 'Saving...' : 'Save Profile'}
              </button>
              {#if userProfile}
                <button type="button" class="outline" on:click={() => { editMode = false; loadProfile(); }}>
                  Cancel
                </button>
              {/if}
            </div>
          </form>
        {:else if userProfile}
          <div class="profile-display">
            <div class="profile-item">
              <span class="label">Age:</span>
              <span class="value">{userProfile.age} years</span>
            </div>
            <div class="profile-item">
              <span class="label">Weight:</span>
              <span class="value">{userProfile.weight_kg} kg</span>
            </div>
            <div class="profile-item">
              <span class="label">Height:</span>
              <span class="value">{userProfile.height_cm} cm</span>
            </div>
            <div class="profile-item">
              <span class="label">Gender:</span>
              <span class="value" style="text-transform: capitalize;">{userProfile.gender}</span>
            </div>
            <div class="profile-item">
              <span class="label">Activity Level:</span>
              <span class="value" style="text-transform: capitalize;">{userProfile.activity_level.replace('_', ' ')}</span>
            </div>
            <div class="profile-item">
              <span class="label">Goal:</span>
              <span class="value" style="text-transform: capitalize;">{userProfile.goal} Weight</span>
            </div>
          </div>

          <h4 style="margin-top: 1.5rem; margin-bottom: 0.75rem;">
            Daily Targets
            {#if userProfile.use_custom_targets}
              <span class="custom-badge">Custom</span>
            {:else}
              <span class="auto-badge">Auto</span>
            {/if}
          </h4>
          <div class="profile-display">
            <div class="profile-item">
              <span class="label">Calories:</span>
              <span class="value">
                {#if userProfile.use_custom_targets && userProfile.custom_calorie_goal}
                  {userProfile.custom_calorie_goal}
                {:else if calculations}
                  {calculations.calorie_goal}
                {:else}
                  -
                {/if}
                cal/day
              </span>
            </div>
            <div class="profile-item">
              <span class="label">Water:</span>
              <span class="value">
                {#if userProfile.use_custom_targets && userProfile.custom_water_target_ml}
                  {(userProfile.custom_water_target_ml / 1000).toFixed(1)}L
                {:else if userProfile.water_target_ml}
                  {(userProfile.water_target_ml / 1000).toFixed(1)}L
                {:else}
                  2.5L
                {/if}
              </span>
            </div>
            <div class="profile-item">
              <span class="label">Protein:</span>
              <span class="value">
                {#if userProfile.use_custom_targets && userProfile.custom_protein_target_g}
                  {userProfile.custom_protein_target_g}g
                {:else}
                  {userProfile.protein_target_g || 150}g
                {/if}
              </span>
            </div>
            <div class="profile-item">
              <span class="label">Carbs:</span>
              <span class="value">
                {#if userProfile.use_custom_targets && userProfile.custom_carbs_target_g}
                  {userProfile.custom_carbs_target_g}g
                {:else}
                  {userProfile.carbs_target_g || 200}g
                {/if}
              </span>
            </div>
            <div class="profile-item">
              <span class="label">Fat:</span>
              <span class="value">
                {#if userProfile.use_custom_targets && userProfile.custom_fat_target_g}
                  {userProfile.custom_fat_target_g}g
                {:else}
                  {userProfile.fat_target_g || 70}g
                {/if}
              </span>
            </div>
          </div>
        {/if}
      </div>

      <div>
        <div class="card">
          <h3>Body Mass Index (BMI)</h3>
          <div class="bmi-display">
            <span class="bmi-value" style="color: {bmiCategory.color}">{bmi}</span>
            <span class="bmi-category" style="color: {bmiCategory.color}">{bmiCategory.label}</span>
          </div>
        </div>

        {#if calculations}
          <div class="card">
            <h3>Calorie Calculations</h3>
            <div class="calculation-item">
              <div class="calc-label">
                <strong>BMR</strong>
                <small class="text-muted">Basal Metabolic Rate</small>
              </div>
              <div class="calc-value">{calculations.bmr} cal/day</div>
            </div>
            <div class="calculation-item">
              <div class="calc-label">
                <strong>TDEE</strong>
                <small class="text-muted">Total Daily Energy Expenditure</small>
              </div>
              <div class="calc-value">{calculations.tdee} cal/day</div>
            </div>
            <div class="calculation-item highlight">
              <div class="calc-label">
                <strong>Daily Goal</strong>
                <small class="text-muted">Recommended for your goal</small>
              </div>
              <div class="calc-value primary">{calculations.calorie_goal} cal/day</div>
            </div>
          </div>

          <div class="card">
            <h3>About Your Numbers</h3>
            <p class="text-muted">
              <strong>BMR</strong> is the number of calories your body burns at rest.
            </p>
            <p class="text-muted">
              <strong>TDEE</strong> is your total calorie burn including activity.
            </p>
            <p class="text-muted">
              <strong>Daily Goal</strong> is adjusted based on your weight goal
              ({calculations.goal === 'lose' ? '-500 cal for weight loss' :
                calculations.goal === 'gain' ? '+500 cal for weight gain' :
                'maintenance calories'}).
            </p>
          </div>
        {/if}
      </div>
    </div>

    <!-- Weight Tracking Section -->
    <div class="card">
      <h2>Weight Tracking</h2>
      <p class="info-banner">
        💡 Weight is automatically logged when you update your profile above. Your weight history is tracked automatically!
      </p>

      <div>
          <h3>Recent Entries</h3>
          {#if weightHistory.length === 0}
            <p class="text-muted">No weight entries yet. Start tracking!</p>
          {:else}
            <div class="weight-list">
              {#each weightHistory.slice(-5).reverse() as entry (entry.id)}
                <div class="weight-entry">
                  <div>
                    <strong>{entry.weight_kg} kg</strong>
                    <span class="text-muted"> - {entry.date}</span>
                    {#if entry.notes}
                      <p class="text-muted" style="font-size: 0.875rem;">{entry.notes}</p>
                    {/if}
                  </div>
                  <button class="danger" on:click={() => handleDeleteWeight(entry.id)}>
                    Delete
                  </button>
                </div>
              {/each}
            </div>
          {/if}
        </div>
      </div>

      {#if weightHistory.length > 0}
        <div class="weight-chart-container">
          <h3>Weight Progress</h3>
          <div class="chart-wrapper">
            <canvas id="weightChart"></canvas>
          </div>
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .info-banner {
    padding: 1rem;
    background: #e3f2fd;
    border-left: 4px solid #2196F3;
    border-radius: 4px;
    margin-bottom: 1.5rem;
    color: #1976D2;
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

  .form-actions {
    display: flex;
    gap: 1rem;
    margin-top: 1.5rem;
  }

  .profile-display {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .profile-item {
    display: flex;
    justify-content: space-between;
    padding: 0.75rem 0;
    border-bottom: 1px solid var(--border);
  }

  .profile-item:last-child {
    border-bottom: none;
  }

  .profile-item .label {
    font-weight: 500;
  }

  .bmi-display {
    text-align: center;
    padding: 2rem;
  }

  .bmi-value {
    display: block;
    font-size: 3rem;
    font-weight: bold;
  }

  .bmi-category {
    display: block;
    font-size: 1.25rem;
    font-weight: 500;
    margin-top: 0.5rem;
  }

  .calculation-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 0;
    border-bottom: 1px solid var(--border);
  }

  .calculation-item:last-child {
    border-bottom: none;
  }

  .calculation-item.highlight {
    background: var(--bg);
    padding: 1rem;
    border-radius: 4px;
    margin-top: 0.5rem;
  }

  .calc-label {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .calc-value {
    font-size: 1.5rem;
    font-weight: bold;
  }

  .calc-value.primary {
    color: var(--primary);
  }

  .weight-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .weight-entry {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem;
    background: var(--bg);
    border-radius: 4px;
  }

  .weight-chart-container {
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid var(--border);
  }

  .chart-wrapper {
    height: 300px;
    position: relative;
    margin-top: 1rem;
  }

  .custom-targets-section {
    margin-top: 1.5rem;
    padding-top: 1.5rem;
    border-top: 2px solid var(--border);
  }

  .custom-targets-section h4 {
    margin: 0;
  }

  .toggle-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    cursor: pointer;
    font-weight: 500;
    font-size: 0.875rem;
  }

  .toggle-label input[type="checkbox"] {
    cursor: pointer;
  }

  .custom-targets-form {
    margin-top: 1rem;
    padding: 1rem;
    background: var(--bg);
    border-radius: 4px;
  }

  .custom-badge,
  .auto-badge {
    display: inline-block;
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    margin-left: 0.5rem;
    font-weight: 500;
  }

  .custom-badge {
    background: #FF9800;
    color: white;
  }

  .auto-badge {
    background: #4CAF50;
    color: white;
  }

  @media (max-width: 768px) {
    .form-row {
      grid-template-columns: 1fr;
    }
  }
</style>
