<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { workouts } from '../lib/api.js';

  const dispatch = createEventDispatcher();

  export let dailyLogId;

  let sessions = [];
  let activeSession = null;
  let showNewWorkout = false;
  let loading = false;
  let error = '';
  let expandedSessions = {}; // Track which past workouts are expanded

  // New session form
  let newSessionName = '';

  // Current exercise being added
  let currentExerciseName = '';
  let currentExerciseCategory = '';

  // Current set being logged
  let currentReps = 10;
  let currentWeight = 0;
  let currentRpe = null;

  // Common exercise names
  const commonExercises = {
    'Chest': ['Bench Press', 'Incline Press', 'Decline Press', 'Chest Fly', 'Push-ups'],
    'Back': ['Pull-ups', 'Lat Pulldown', 'Barbell Row', 'Dumbbell Row', 'Deadlift'],
    'Legs': ['Squat', 'Leg Press', 'Lunges', 'Leg Curl', 'Leg Extension', 'Calf Raise'],
    'Shoulders': ['Overhead Press', 'Lateral Raise', 'Front Raise', 'Rear Delt Fly'],
    'Arms': ['Bicep Curl', 'Hammer Curl', 'Tricep Extension', 'Tricep Dips', 'Skull Crusher'],
    'Core': ['Plank', 'Crunches', 'Russian Twist', 'Leg Raise', 'Ab Wheel']
  };

  onMount(async () => {
    await loadSessions();
  });

  async function loadSessions() {
    try {
      loading = true;
      sessions = await workouts.getSessions(dailyLogId);

      // Load full details for each session
      for (let session of sessions) {
        const details = await workouts.getSessionDetails(session.id);
        session.exercises = details.exercises || [];
      }
    } catch (err) {
      console.error('Failed to load workout sessions:', err);
      error = err.message;
    } finally {
      loading = false;
    }
  }

  async function startNewWorkout() {
    try {
      const session = await workouts.createSession({
        daily_log_id: dailyLogId,
        name: newSessionName || 'Workout'
      });
      activeSession = { ...session, exercises: [] };
      sessions = [activeSession, ...sessions];
      showNewWorkout = false;
      newSessionName = '';
      // Don't dispatch update here - it will reload and clear activeSession
      // dispatch('update');
    } catch (err) {
      error = err.message;
    }
  }

  async function addExercise() {
    if (!currentExerciseName || !activeSession) return;

    try {
      const exercise = await workouts.createExercise({
        workout_session_id: activeSession.id,
        exercise_name: currentExerciseName,
        exercise_category: currentExerciseCategory,
        order_index: activeSession.exercises.length
      });

      exercise.sets = [];
      activeSession.exercises = [...activeSession.exercises, exercise];

      // Reset form
      currentExerciseName = '';
      currentExerciseCategory = '';
    } catch (err) {
      error = err.message;
    }
  }

  async function logSet(exercise) {
    try {
      const set = await workouts.createSet({
        workout_exercise_id: exercise.id,
        set_number: exercise.sets.length + 1,
        reps: currentReps,
        weight_kg: currentWeight || null,
        rpe: currentRpe
      });

      exercise.sets = [...exercise.sets, set];
      activeSession.exercises = [...activeSession.exercises];

      // Keep weight same, reset reps to default
      currentReps = 10;
      currentRpe = null;
    } catch (err) {
      error = err.message;
    }
  }

  async function finishWorkout() {
    if (!activeSession) return;

    try {
      await workouts.updateSession(activeSession.id, {
        ...activeSession,
        completed_at: new Date().toISOString()
      });
      activeSession = null;
      await loadSessions();
      dispatch('update');
    } catch (err) {
      error = err.message;
    }
  }

  async function deleteSession(sessionId) {
    if (!confirm('Delete this workout? This cannot be undone.')) return;

    try {
      await workouts.deleteSession(sessionId);
      sessions = sessions.filter(s => s.id !== sessionId);
      if (activeSession && activeSession.id === sessionId) {
        activeSession = null;
      }
      dispatch('update');
    } catch (err) {
      error = err.message;
    }
  }

  function selectCategory(category) {
    currentExerciseCategory = category;
  }

  function selectExercise(name) {
    currentExerciseName = name;
  }

  function toggleSession(sessionId) {
    expandedSessions[sessionId] = !expandedSessions[sessionId];
    expandedSessions = { ...expandedSessions };
  }
</script>

<div class="workout-tracker card">
  <h3>💪 Strength Training</h3>

  {#if error}
    <div class="error-banner">{error}</div>
  {/if}

  {#if loading}
    <p>Loading workouts...</p>
  {:else if activeSession}
    <!-- Active Workout View -->
    <div class="active-workout">
      <div class="workout-header">
        <h4>{activeSession.name}</h4>
        <button class="btn-success" on:click={finishWorkout}>Finish Workout</button>
      </div>

      <!-- Add Exercise Section -->
      <div class="add-exercise">
        <h5>Add Exercise</h5>

        <!-- Category Selection -->
        <div class="category-grid">
          {#each Object.keys(commonExercises) as category}
            <button
              class="category-btn"
              class:active={currentExerciseCategory === category}
              on:click={() => selectCategory(category)}
            >
              {category}
            </button>
          {/each}
        </div>

        <!-- Exercise Selection -->
        {#if currentExerciseCategory}
          <div class="exercise-grid">
            {#each commonExercises[currentExerciseCategory] as exercise}
              <button
                class="exercise-btn"
                on:click={() => selectExercise(exercise)}
              >
                {exercise}
              </button>
            {/each}
          </div>

          <!-- Custom exercise name -->
          <input
            type="text"
            placeholder="Or enter custom exercise..."
            bind:value={currentExerciseName}
            class="form-control"
          />
        {/if}

        {#if currentExerciseName}
          <button class="btn-primary" on:click={addExercise}>
            Add {currentExerciseName}
          </button>
        {/if}
      </div>

      <!-- Current Exercises & Sets -->
      <div class="exercises-list">
        {#each activeSession.exercises as exercise (exercise.id)}
          <div class="exercise-card">
            <div class="exercise-header">
              <h5>{exercise.exercise_name}</h5>
              <span class="badge">{exercise.sets.length} sets</span>
            </div>

            <!-- Sets List -->
            <div class="sets-list">
              {#each exercise.sets as set, i (set.id)}
                <div class="set-row">
                  <span class="set-num">Set {set.set_number}</span>
                  <span class="set-detail">{set.reps} reps</span>
                  {#if set.weight_kg}
                    <span class="set-detail">{set.weight_kg} kg</span>
                  {/if}
                  {#if set.rpe}
                    <span class="rpe-badge">RPE {set.rpe}</span>
                  {/if}
                </div>
              {/each}
            </div>

            <!-- Log New Set -->
            <div class="log-set">
              <input
                type="number"
                placeholder="Weight (kg)"
                bind:value={currentWeight}
                min="0"
                step="0.5"
                class="weight-input"
              />
              <input
                type="number"
                placeholder="Reps"
                bind:value={currentReps}
                min="1"
                class="reps-input"
              />
              <input
                type="number"
                placeholder="RPE (optional)"
                bind:value={currentRpe}
                min="1"
                max="10"
                class="rpe-input"
              />
              <button class="btn-add-set" on:click={() => logSet(exercise)}>
                + Set
              </button>
            </div>
          </div>
        {/each}
      </div>
    </div>
  {:else}
    <!-- No Active Workout -->
    <div class="start-workout">
      {#if showNewWorkout}
        <div class="new-workout-form">
          <input
            type="text"
            placeholder="Workout name (optional)"
            bind:value={newSessionName}
            class="form-control"
          />
          <div class="form-actions">
            <button class="btn-primary" on:click={startNewWorkout}>
              Start Workout
            </button>
            <button class="btn-secondary" on:click={() => showNewWorkout = false}>
              Cancel
            </button>
          </div>
        </div>
      {:else}
        <button class="btn-large btn-primary" on:click={() => showNewWorkout = true}>
          Start Workout
        </button>
      {/if}
    </div>

    <!-- Previous Workouts Today -->
    {#if sessions.length > 0}
      <div class="previous-workouts">
        <h5>Today's Workouts</h5>
        {#each sessions as session (session.id)}
          <div class="workout-summary" class:expanded={expandedSessions[session.id]}>
            <div class="summary-header">
              <button class="expand-btn" on:click={() => toggleSession(session.id)}>
                <div class="summary-info">
                  <strong>{session.name}</strong>
                  <div class="summary-stats">
                    {session.exercises?.length || 0} exercises •
                    {session.exercises?.reduce((sum, ex) => sum + (ex.sets?.length || 0), 0) || 0} sets
                  </div>
                </div>
                <span class="expand-icon">{expandedSessions[session.id] ? '▼' : '▶'}</span>
              </button>
              <button class="btn-delete" on:click={(e) => { e.stopPropagation(); deleteSession(session.id); }}>
                Delete
              </button>
            </div>

            {#if expandedSessions[session.id] && session.exercises && session.exercises.length > 0}
              <div class="session-details">
                {#each session.exercises as exercise}
                  <div class="exercise-detail">
                    <h6>{exercise.exercise_name}</h6>
                    {#if exercise.exercise_category}
                      <span class="category-badge">{exercise.exercise_category}</span>
                    {/if}
                    <div class="sets-display">
                      {#each exercise.sets as set}
                        <div class="set-row-display">
                          <span class="set-num">Set {set.set_number}</span>
                          <span class="set-detail">
                            {set.reps} reps × {set.weight_kg}kg
                            {#if set.rpe}
                              • RPE {set.rpe}
                            {/if}
                          </span>
                        </div>
                      {/each}
                    </div>
                  </div>
                {/each}
              </div>
            {/if}
          </div>
        {/each}
      </div>
    {/if}
  {/if}
</div>

<style>
  .workout-tracker {
    margin-bottom: 1rem;
  }

  .active-workout {
    margin-top: 1rem;
  }

  .workout-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid var(--border);
  }

  .add-exercise {
    background: var(--bg);
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
  }

  .category-grid, .exercise-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    gap: 0.5rem;
    margin: 0.5rem 0;
  }

  .category-btn, .exercise-btn {
    padding: 0.5rem;
    border: 1px solid var(--border);
    background: white;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .category-btn:hover, .exercise-btn:hover {
    background: var(--primary);
    color: white;
    border-color: var(--primary);
  }

  .category-btn.active {
    background: var(--primary);
    color: white;
    border-color: var(--primary);
  }

  .exercise-card {
    background: white;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
  }

  .exercise-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
  }

  .sets-list {
    margin-bottom: 1rem;
  }

  .set-row {
    display: flex;
    gap: 1rem;
    padding: 0.5rem;
    background: var(--bg);
    border-radius: 4px;
    margin-bottom: 0.25rem;
  }

  .set-num {
    font-weight: 600;
    min-width: 50px;
  }

  .set-detail {
    color: var(--text-light);
  }

  .rpe-badge {
    background: var(--secondary);
    color: white;
    padding: 0.125rem 0.5rem;
    border-radius: 12px;
    font-size: 0.85rem;
  }

  .log-set {
    display: flex;
    gap: 0.5rem;
  }

  .weight-input, .reps-input, .rpe-input {
    flex: 1;
    padding: 0.5rem;
    border: 1px solid var(--border);
    border-radius: 4px;
  }

  .btn-add-set {
    background: var(--primary);
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
    white-space: nowrap;
  }

  .start-workout {
    text-align: center;
    padding: 2rem;
  }

  .btn-large {
    padding: 1rem 2rem;
    font-size: 1.1rem;
  }

  .previous-workouts {
    margin-top: 1.5rem;
    padding-top: 1rem;
    border-top: 1px solid var(--border);
  }

  .workout-summary {
    background: var(--bg);
    border-radius: 8px;
    margin-bottom: 0.5rem;
    border: 1px solid var(--border);
    overflow: hidden;
  }

  .workout-summary.expanded {
    background: white;
  }

  .summary-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 0.5rem;
  }

  .expand-btn {
    flex: 1;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    background: transparent;
    border: none;
    cursor: pointer;
    text-align: left;
    transition: background 0.2s;
  }

  .expand-btn:hover {
    background: rgba(0, 0, 0, 0.03);
  }

  .summary-info {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .summary-stats {
    color: var(--text-light);
    font-size: 0.9rem;
  }

  .expand-icon {
    color: var(--primary);
    font-size: 0.9rem;
    margin-left: 1rem;
  }

  .session-details {
    padding: 0 1rem 1rem 1rem;
    background: white;
  }

  .exercise-detail {
    margin-bottom: 1rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border);
  }

  .exercise-detail:last-child {
    margin-bottom: 0;
    padding-bottom: 0;
    border-bottom: none;
  }

  .exercise-detail h6 {
    color: var(--primary);
    margin-bottom: 0.5rem;
    display: inline-block;
  }

  .category-badge {
    background: var(--secondary);
    color: white;
    padding: 0.125rem 0.5rem;
    border-radius: 12px;
    font-size: 0.75rem;
    margin-left: 0.5rem;
  }

  .sets-display {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    margin-top: 0.5rem;
  }

  .set-row-display {
    display: flex;
    justify-content: space-between;
    padding: 0.5rem;
    background: var(--bg);
    border-radius: 4px;
  }

  .error-banner {
    background: var(--danger);
    color: white;
    padding: 0.75rem;
    border-radius: 4px;
    margin-bottom: 1rem;
  }

  .badge {
    background: var(--primary);
    color: white;
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
    font-size: 0.85rem;
  }

  .btn-primary {
    background: var(--primary);
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
  }

  .btn-secondary {
    background: var(--border);
    color: var(--text);
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
  }

  .btn-success {
    background: var(--primary);
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 600;
  }

  .btn-delete {
    background: var(--danger);
    color: white;
    border: none;
    padding: 0.5rem 0.75rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.85rem;
    margin-right: 0.5rem;
    white-space: nowrap;
  }

  .btn-delete:hover {
    background: #d32f2f;
  }

  .form-control {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid var(--border);
    border-radius: 4px;
    margin: 0.5rem 0;
  }

  .form-actions {
    display: flex;
    gap: 0.5rem;
    margin-top: 0.5rem;
  }
</style>
