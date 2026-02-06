<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { exercises } from '../lib/api.js';

  export let dailyLogId;

  const dispatch = createEventDispatcher();

  let exerciseList = [];
  let loading = false;
  let showForm = false;

  let newExercise = {
    exercise_type: 'Running',
    duration_minutes: 30,
    notes: ''
  };

  const exerciseTypes = [
    'Running',
    'Walking',
    'Cycling',
    'Swimming',
    'Weightlifting',
    'Yoga',
    'Pilates',
    'Dancing',
    'Sports',
    'HIIT',
    'Cardio',
    'Stretching',
    'Other'
  ];

  onMount(async () => {
    await loadExercises();
  });

  async function loadExercises() {
    if (!dailyLogId) return;
    try {
      loading = true;
      exerciseList = await exercises.getByLog(dailyLogId);
    } catch (err) {
      console.error('Failed to load exercises:', err);
    } finally {
      loading = false;
    }
  }

  async function handleAdd() {
    try {
      await exercises.create({
        daily_log_id: dailyLogId,
        ...newExercise
      });
      await loadExercises();
      dispatch('update');
      showForm = false;
      resetForm();
    } catch (err) {
      console.error('Failed to add exercise:', err);
    }
  }

  async function handleDelete(exerciseId) {
    try {
      await exercises.delete(exerciseId);
      await loadExercises();
      dispatch('update');
    } catch (err) {
      console.error('Failed to delete exercise:', err);
    }
  }

  function resetForm() {
    newExercise = {
      exercise_type: 'Running',
      duration_minutes: 30,
      notes: ''
    };
  }

  $: totalMinutes = exerciseList.reduce((sum, ex) => sum + ex.duration_minutes, 0);
</script>

<div class="exercise-logger card">
  <div class="flex-between">
    <h3>Exercise</h3>
    <button class="outline" on:click={() => showForm = !showForm}>
      {showForm ? 'Cancel' : '+ Add Exercise'}
    </button>
  </div>

  {#if showForm}
    <div class="exercise-form">
      <div class="form-group">
        <label for="exercise-type">Exercise Type</label>
        <select id="exercise-type" bind:value={newExercise.exercise_type}>
          {#each exerciseTypes as type}
            <option value={type}>{type}</option>
          {/each}
        </select>
      </div>

      <div class="form-group">
        <label for="duration">Duration (minutes)</label>
        <input
          id="duration"
          type="number"
          bind:value={newExercise.duration_minutes}
          min="1"
          step="1"
        />
      </div>

      <div class="form-group">
        <label for="exercise-notes">Notes (optional)</label>
        <input
          id="exercise-notes"
          type="text"
          bind:value={newExercise.notes}
          placeholder="e.g., Morning run, felt great"
        />
      </div>

      <button class="primary" on:click={handleAdd}>
        Add Exercise
      </button>
    </div>
  {/if}

  <div class="exercise-summary">
    <div class="summary-stat">
      <span class="label">Total Today:</span>
      <span class="value">{totalMinutes} minutes</span>
    </div>
  </div>

  {#if exerciseList.length > 0}
    <div class="exercise-list">
      {#each exerciseList as exercise (exercise.id)}
        <div class="exercise-item">
          <div class="exercise-info">
            <strong>{exercise.exercise_type}</strong>
            <span class="text-muted">
              {exercise.duration_minutes} min
            </span>
            {#if exercise.notes}
              <p class="text-muted exercise-notes">{exercise.notes}</p>
            {/if}
          </div>
          <button class="danger" on:click={() => handleDelete(exercise.id)}>
            Delete
          </button>
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .exercise-logger {
    margin-bottom: 2rem;
  }

  .exercise-form {
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

  .exercise-summary {
    margin: 1rem 0;
    padding: 1rem;
    background: var(--bg);
    border-radius: 4px;
  }

  .summary-stat {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .summary-stat .label {
    font-weight: 500;
  }

  .summary-stat .value {
    font-size: 1.25rem;
    font-weight: bold;
    color: var(--secondary);
  }

  .exercise-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    margin-top: 1rem;
  }

  .exercise-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem;
    background: var(--bg);
    border-radius: 4px;
  }

  .exercise-info {
    flex: 1;
  }

  .exercise-info span {
    display: block;
    font-size: 0.875rem;
    margin-top: 0.25rem;
  }

  .exercise-notes {
    font-size: 0.875rem;
    margin-top: 0.25rem;
  }
</style>
