<script>
  import { onMount } from 'svelte';
  import { nutrition, dailyLogs } from '../lib/api.js';
  import { push } from 'svelte-spa-router';
  import { Chart, registerables } from 'chart.js';

  Chart.register(...registerables);

  let startDate = '';
  let endDate = '';
  let history = [];
  let loading = false;
  let error = '';
  let chartInstance = null;

  onMount(() => {
    // Default to last 30 days
    const end = new Date();
    const start = new Date();
    start.setDate(start.getDate() - 30);

    endDate = end.toISOString().split('T')[0];
    startDate = start.toISOString().split('T')[0];

    loadHistory();
  });

  async function loadHistory() {
    if (!startDate || !endDate) return;

    try {
      loading = true;
      error = '';
      history = await nutrition.getHistory(startDate, endDate);
      renderChart();
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }

  function renderChart() {
    if (chartInstance) {
      chartInstance.destroy();
    }

    const ctx = document.getElementById('caloriesChart');
    if (!ctx) return;

    const labels = history.map(h => h.date);
    const calories = history.map(h => h.total_calories);

    chartInstance = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: 'Calories',
          data: calories,
          borderColor: '#4CAF50',
          backgroundColor: 'rgba(76, 175, 80, 0.1)',
          tension: 0.4
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
            beginAtZero: true
          }
        }
      }
    });
  }

  $: avgCalories = history.length > 0
    ? Math.round(history.reduce((sum, h) => sum + h.total_calories, 0) / history.length)
    : 0;

  $: totalDays = history.length;

  function handleDayClick(day) {
    // Navigate to nutrition page for this date
    push(`/nutrition/${day.date}`);
  }

  async function handleDeleteDay(day, event) {
    event.stopPropagation(); // Prevent navigation

    if (!confirm(`Delete all data for ${day.date}? This will remove all food entries, exercise, water, and supplements for this day.`)) {
      return;
    }

    try {
      loading = true;
      // Get the daily log ID for this date
      const log = await dailyLogs.getByDate(day.date);
      if (log && log.id) {
        await dailyLogs.delete(log.id);
        await loadHistory(); // Reload history
      }
    } catch (err) {
      error = `Failed to delete day: ${err.message}`;
    } finally {
      loading = false;
    }
  }
</script>

<div class="container">
  <h1>History</h1>

  <div class="card">
    <h3>Date Range</h3>
    <div class="date-picker">
      <div class="form-group">
        <label for="start">Start Date</label>
        <input
          id="start"
          type="date"
          bind:value={startDate}
          on:change={loadHistory}
        />
      </div>
      <div class="form-group">
        <label for="end">End Date</label>
        <input
          id="end"
          type="date"
          bind:value={endDate}
          on:change={loadHistory}
        />
      </div>
    </div>
  </div>

  {#if error}
    <div class="error">{error}</div>
  {/if}

  {#if loading}
    <div class="loading">Loading history...</div>
  {:else if history.length > 0}
    <div class="grid grid-2">
      <div class="card">
        <h3>Summary Stats</h3>
        <div class="stat">
          <span class="stat-label">Total Days</span>
          <span class="stat-value">{totalDays}</span>
        </div>
        <div class="stat">
          <span class="stat-label">Average Calories</span>
          <span class="stat-value">{avgCalories}</span>
        </div>
      </div>

      <div class="card">
        <h3>Quick Stats</h3>
        <div class="stat">
          <span class="stat-label">Days with Exercise</span>
          <span class="stat-value">
            {history.filter(h => h.exercise_minutes > 0).length}
          </span>
        </div>
        <div class="stat">
          <span class="stat-label">Total Entries</span>
          <span class="stat-value">
            {history.reduce((sum, h) => sum + h.entry_count, 0)}
          </span>
        </div>
      </div>
    </div>

    <div class="card">
      <h3>Calorie Chart</h3>
      <div class="chart-container">
        <canvas id="caloriesChart"></canvas>
      </div>
    </div>

    <div class="card">
      <h3>Daily Breakdown (Click to see full nutrition)</h3>
      <div class="history-list">
        {#each history.slice().reverse() as day (day.date)}
          <div class="history-item" on:click={() => handleDayClick(day)}>
            <div class="history-date">
              <strong>{day.date}</strong>
              <div class="date-actions">
                <span class="view-link">View Details →</span>
                <button
                  class="danger delete-day-btn"
                  on:click={(e) => handleDeleteDay(day, e)}
                  title="Delete this day"
                >
                  Delete
                </button>
              </div>
            </div>
            <div class="history-stats">
              <span>{Math.round(day.total_calories)} cal</span>
              <span>•</span>
              <span>P: {Math.round(day.macros.protein_g)}g</span>
              <span>C: {Math.round(day.macros.carbs_g)}g</span>
              <span>F: {Math.round(day.macros.fat_g)}g</span>
            </div>
            <div class="history-extras">
              {#if day.total_water_ml > 0}
                <span class="water-indicator">💧 {(day.total_water_ml / 1000).toFixed(1)}L</span>
              {/if}
              {#if day.exercise_minutes > 0}
                <span class="exercise-indicator">🏃 {day.exercise_minutes} min</span>
              {/if}
            </div>
          </div>
        {/each}
      </div>
    </div>
  {:else}
    <div class="card">
      <p class="text-muted text-center">No history data for this date range.</p>
    </div>
  {/if}
</div>

<style>
  .date-picker {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }

  .form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
  }

  .stat {
    display: flex;
    justify-content: space-between;
    padding: 0.75rem 0;
    border-bottom: 1px solid var(--border);
  }

  .stat:last-child {
    border-bottom: none;
  }

  .stat-value {
    font-size: 1.25rem;
    font-weight: bold;
    color: var(--primary);
  }

  .chart-container {
    height: 300px;
    position: relative;
  }

  .history-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .history-item {
    padding: 1rem;
    background: var(--bg);
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .history-item:hover {
    background: var(--white);
    box-shadow: var(--shadow);
  }

  .history-item.selected {
    background: var(--white);
    box-shadow: var(--shadow);
  }

  .history-date {
    margin-bottom: 0.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .date-actions {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .view-link {
    color: var(--primary);
    font-size: 0.875rem;
    font-weight: 500;
  }

  .delete-day-btn {
    padding: 0.25rem 0.5rem;
    font-size: 0.75rem;
  }

  .history-stats {
    font-size: 0.875rem;
    color: var(--text-light);
  }

  .history-stats span {
    margin-right: 0.5rem;
  }

  .history-extras {
    display: flex;
    gap: 1rem;
    margin-top: 0.5rem;
    font-size: 0.875rem;
  }

  .water-indicator {
    color: #2196F3;
    font-weight: 500;
  }

  .exercise-indicator {
    color: #FF9800;
    font-weight: 500;
  }

  .day-details {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 2px solid var(--border);
  }

  .day-details h4 {
    margin-bottom: 0.75rem;
    color: var(--text-light);
  }

  .food-entries-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
  }

  .entry-detail {
    padding: 0.75rem;
    background: var(--bg);
    border-radius: 4px;
  }

  .entry-detail p {
    margin: 0.25rem 0 0 0;
    font-size: 0.875rem;
  }

  .meal-badge {
    display: inline-block;
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
    background: var(--primary);
    color: white;
    border-radius: 4px;
    text-transform: capitalize;
    margin-left: 0.5rem;
  }

  .day-totals {
    padding: 1rem;
    background: #f0f7ff;
    border-radius: 4px;
  }

  .totals-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.75rem;
    margin-top: 0.75rem;
  }

  .totals-grid div {
    font-size: 0.875rem;
  }

  @media (max-width: 768px) {
    .date-picker {
      grid-template-columns: 1fr;
    }

    .history-stats {
      display: flex;
      flex-wrap: wrap;
      gap: 0.25rem;
    }

    .history-stats span {
      margin-right: 0.25rem;
    }

    .delete-day-btn {
      padding: 0.5rem 0.75rem;
      font-size: 0.875rem;
    }

    .history-extras {
      flex-wrap: wrap;
    }

    .chart-container {
      height: 250px;
    }
  }

  @media (max-width: 480px) {
    .date-actions {
      flex-direction: column;
      align-items: flex-end;
      gap: 0.5rem;
    }

    .delete-day-btn {
      width: 100%;
    }

    .history-item {
      padding: 0.75rem;
    }
  }
</style>
