<script>
  import { onMount } from 'svelte';
  import { workouts } from '../lib/api.js';

  let recentWorkouts = [];
  let loading = true;
  let error = '';
  let expanded = {};

  onMount(async () => {
    await loadRecentWorkouts();
  });

  async function loadRecentWorkouts() {
    try {
      loading = true;
      // Get workouts from last 7 days
      const endDate = new Date().toISOString().split('T')[0];
      const startDate = new Date();
      startDate.setDate(startDate.getDate() - 7);
      const startDateStr = startDate.toISOString().split('T')[0];

      const summaries = await workouts.getDailySummary(startDateStr, endDate);
      recentWorkouts = summaries.sort((a, b) => b.date.localeCompare(a.date)).slice(0, 5);
    } catch (err) {
      console.error('Failed to load recent workouts:', err);
      error = err.message;
    } finally {
      loading = false;
    }
  }

  async function toggleDetails(date) {
    if (expanded[date]) {
      expanded[date] = null;
      return;
    }

    try {
      const details = await workouts.getByDate(date);
      expanded[date] = details;
      expanded = { ...expanded };
    } catch (err) {
      console.error('Failed to load workout details:', err);
    }
  }
</script>

<div class="recent-workouts card">
  <h3>Recent Workouts</h3>

  {#if loading}
    <p class="text-muted">Loading recent workouts...</p>
  {:else if error}
    <p class="error">{error}</p>
  {:else if recentWorkouts.length === 0}
    <p class="text-muted">No workouts in the last 7 days. Start tracking your strength training!</p>
  {:else}
    <div class="workouts-list">
      {#each recentWorkouts as workout (workout.date)}
        <div class="workout-item">
          <button class="workout-header" on:click={() => toggleDetails(workout.date)}>
            <div class="workout-info">
              <strong>{workout.date}</strong>
              {#if workout.workout_names}
                <span class="workout-names">• {workout.workout_names.replace(/,/g, ', ')}</span>
              {/if}
            </div>
            <div class="workout-stats">
              <span>{workout.total_exercises} exercises</span>
              <span>•</span>
              <span>{workout.total_sets} sets</span>
              {#if workout.total_volume > 0}
                <span>•</span>
                <span>{Math.round(workout.total_volume)}kg</span>
              {/if}
            </div>
          </button>

          {#if expanded[workout.date]}
            <div class="workout-details">
              {#each expanded[workout.date] as session}
                <div class="session-detail">
                  <h5>{session.name}</h5>
                  {#each session.exercises as exercise}
                    <div class="exercise-detail">
                      <strong>{exercise.exercise_name}</strong>
                      <div class="sets-summary">
                        {#each exercise.sets as set, i}
                          <span class="set-badge">
                            {set.reps} × {set.weight_kg}kg
                            {#if set.rpe}
                              @ RPE {set.rpe}
                            {/if}
                          </span>
                        {/each}
                      </div>
                    </div>
                  {/each}
                </div>
              {/each}
            </div>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</div>

<style>
  .recent-workouts {
    margin-bottom: 1rem;
  }

  .workouts-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .workout-item {
    background: var(--bg);
    border-radius: 8px;
    overflow: hidden;
  }

  .workout-header {
    width: 100%;
    padding: 1rem;
    background: var(--bg);
    border: none;
    cursor: pointer;
    text-align: left;
    transition: background 0.2s;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .workout-header:hover {
    background: #e8e8e8;
  }

  .workout-info {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .workout-names {
    color: var(--text-light);
    font-size: 0.9rem;
  }

  .workout-stats {
    display: flex;
    gap: 0.5rem;
    font-size: 0.9rem;
    color: var(--text-light);
  }

  .workout-details {
    padding: 1rem;
    background: white;
    border-top: 1px solid var(--border);
  }

  .session-detail {
    margin-bottom: 1rem;
  }

  .session-detail:last-child {
    margin-bottom: 0;
  }

  .session-detail h5 {
    color: var(--primary);
    margin-bottom: 0.5rem;
  }

  .exercise-detail {
    margin-bottom: 0.75rem;
    padding-left: 1rem;
  }

  .exercise-detail strong {
    display: block;
    margin-bottom: 0.25rem;
  }

  .sets-summary {
    display: flex;
    flex-wrap: wrap;
    gap: 0.25rem;
  }

  .set-badge {
    background: var(--primary);
    color: white;
    padding: 0.125rem 0.5rem;
    border-radius: 12px;
    font-size: 0.85rem;
  }

  .text-muted {
    color: var(--text-light);
    text-align: center;
    padding: 1rem;
  }

  .error {
    color: var(--danger);
    padding: 1rem;
  }
</style>
