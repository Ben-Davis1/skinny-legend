<script>
  import { onMount } from 'svelte';
  import { ai, foodEntries, dailyLogs, exercises, supplements, recentFoods } from '../lib/api.js';
  import { selectedDate } from '../lib/stores.js';

  let messages = [];
  let inputMessage = '';
  let loading = false;
  let error = '';
  let conversationHistory = [];
  let currentDate;
  let currentLog = null;
  let currentEntries = [];
  let recentFoodsList = [];

  selectedDate.subscribe(async value => {
    currentDate = value;
    if (currentDate) {
      currentLog = await dailyLogs.getByDate(currentDate);
    }
  });

  onMount(async () => {
    currentLog = await dailyLogs.getByDate(currentDate);
    await loadTodayContext();
    messages.push({
      role: 'assistant',
      content: 'Hi! I\'m your nutrition assistant. Tell me what you ate and I\'ll help log it.',
      timestamp: new Date()
    });
  });

  async function loadTodayContext() {
    try {
      // Load current food entries
      if (currentLog) {
        currentEntries = await foodEntries.getByLog(currentLog.id);
      }
      // Load recent foods
      recentFoodsList = await recentFoods.get();
    } catch (err) {
      console.error('Failed to load context:', err);
    }
  }

  async function sendMessage() {
    if (!inputMessage.trim()) return;

    const userMessage = inputMessage;
    inputMessage = '';

    messages.push({
      role: 'user',
      content: userMessage,
      timestamp: new Date()
    });
    messages = messages;

    try {
      loading = true;
      error = '';

      // Build context about today's meals
      const totalCalories = currentEntries.reduce((sum, entry) => sum + entry.calories, 0);
      const context = {
        current_meals: currentEntries.map(e => ({
          name: e.name,
          calories: e.calories,
          meal_type: e.meal_type
        })),
        total_calories: totalCalories,
        calorie_goal: currentLog?.calorie_goal || 2000,
        recent_foods: recentFoodsList.slice(0, 20).map(f => ({
          name: f.name,
          calories: f.calories,
          serving_size: f.serving_size
        }))
      };

      const response = await ai.chat(userMessage, conversationHistory, context);

      // Debug log the response
      console.log('AI Response:', JSON.stringify(response, null, 2));

      conversationHistory.push(
        { role: 'user', content: userMessage },
        { role: 'assistant', content: JSON.stringify(response) }
      );

      // Handle actions (water, exercise, and supplements)
      if (response.actions) {
        if (response.actions.water_ml && response.actions.water_ml > 0) {
          await updateWater(response.actions.water_ml);
        }
        if (response.actions.exercise && response.actions.exercise.type && response.actions.exercise.duration_minutes > 0) {
          await addExercise(response.actions.exercise);
        }
        if (response.actions.supplements && response.actions.supplements.length > 0) {
          await addSupplements(response.actions.supplements);
        }
      }

      if (response.needs_clarification) {
        messages.push({
          role: 'assistant',
          content: response.message,
          timestamp: new Date()
        });
      } else if (response.items && response.items.length > 0) {
        messages.push({
          role: 'assistant',
          content: response.message || `I found ${response.items.length} item(s). Would you like to add them to your log?`,
          items: response.items,
          timestamp: new Date()
        });
      } else if (response.actions && (response.actions.water_ml > 0 || (response.actions.exercise && response.actions.exercise.duration_minutes > 0))) {
        // Actions were performed but no food items
        messages.push({
          role: 'assistant',
          content: response.message || 'Updated!',
          timestamp: new Date()
        });
      } else {
        messages.push({
          role: 'assistant',
          content: response.message || 'I couldn\'t extract any information. Could you provide more details?',
          timestamp: new Date()
        });
      }

      messages = messages;
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }

  async function updateWater(waterMl) {
    if (!currentLog) return;

    try {
      const newTotal = (currentLog.total_water_ml || 0) + waterMl;
      await dailyLogs.update(currentLog.id, {
        ...currentLog,
        total_water_ml: newTotal
      });
      currentLog.total_water_ml = newTotal;
    } catch (err) {
      console.error('Failed to update water:', err);
    }
  }

  async function addExercise(exerciseData) {
    if (!currentLog) return;

    try {
      await exercises.create({
        daily_log_id: currentLog.id,
        exercise_type: exerciseData.type,
        duration_minutes: exerciseData.duration_minutes,
        notes: exerciseData.notes || 'Logged via AI Chat'
      });
    } catch (err) {
      console.error('Failed to add exercise:', err);
    }
  }

  async function addSupplements(supplementsList) {
    if (!currentLog || !supplementsList || supplementsList.length === 0) return;

    try {
      for (const supp of supplementsList) {
        await supplements.create({
          daily_log_id: currentLog.id,
          name: supp.name,
          dosage: supp.dosage || '',
          type: supp.type || 'supplement',
          time_taken: new Date().toTimeString().split(' ')[0].substring(0, 5),
          notes: supp.notes || 'Logged via AI Chat'
        });
      }
    } catch (err) {
      console.error('Failed to add supplements:', err);
    }
  }

  async function addItemToLog(item) {
    if (!currentLog) {
      error = 'Could not load daily log';
      return;
    }

    try {
      const aiNotes = `AI Chat Assistant - Natural language food entry (Auto-detected: ${item.meal_type || 'snack'})`;

      await foodEntries.create({
        daily_log_id: currentLog.id,
        name: item.name,
        calories: item.calories,
        protein_g: item.protein_g || 0,
        carbs_g: item.carbs_g || 0,
        fat_g: item.fat_g || 0,
        fiber_g: item.fiber_g || 0,
        sugar_g: item.sugar_g || 0,
        serving_size: item.serving_size || '1 serving',
        meal_type: item.meal_type || 'snack',
        ai_notes: aiNotes
      });

      messages.push({
        role: 'assistant',
        content: `Added "${item.name}" to your log!`,
        timestamp: new Date()
      });
      messages = messages;

      // Reload context after adding
      await loadTodayContext();
    } catch (err) {
      error = `Failed to add food: ${err.message}`;
    }
  }

  async function addAllItems(items) {
    if (!currentLog || !items || items.length === 0) {
      error = 'Could not load daily log or no items to add';
      return;
    }

    try {
      let successCount = 0;

      for (const item of items) {
        const aiNotes = `AI Chat Assistant - Natural language food entry (Auto-detected: ${item.meal_type || 'snack'})`;

        await foodEntries.create({
          daily_log_id: currentLog.id,
          name: item.name,
          calories: item.calories,
          protein_g: item.protein_g || 0,
          carbs_g: item.carbs_g || 0,
          fat_g: item.fat_g || 0,
          fiber_g: item.fiber_g || 0,
          sugar_g: item.sugar_g || 0,
          serving_size: item.serving_size || '1 serving',
          meal_type: item.meal_type || 'snack',
          ai_notes: aiNotes
        });
        successCount++;
      }

      messages.push({
        role: 'assistant',
        content: `Added all ${successCount} items to your log!`,
        timestamp: new Date()
      });
      messages = messages;

      // Show success alert
      alert(`✅ Successfully added all ${successCount} items to your log!`);

      // Reload context after adding
      await loadTodayContext();
    } catch (err) {
      error = `Failed to add items: ${err.message}`;
    }
  }

  function handleKeydown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  }
</script>

<div class="container">
  <h1>AI Chat</h1>

  {#if error}
    <div class="error">{error}</div>
  {/if}

  <div class="chat-container card">
    <div class="messages">
      {#each messages as message (message.timestamp)}
        <div class="message {message.role}">
          <div class="message-content">
            <p>{message.content}</p>

            {#if message.items}
              <div class="food-items">
                {#if message.items.length > 1}
                  <button class="primary add-all-btn" on:click={() => addAllItems(message.items)}>
                    ➕ Add All ({message.items.length} items)
                  </button>
                {/if}
                {#each message.items as item (item.name + item.calories)}
                  <div class="food-item">
                    <div class="item-details">
                      <strong>{item.name || 'Unknown'}</strong>
                      {#if item.meal_type}
                        <span class="meal-badge">{item.meal_type}</span>
                      {/if}
                      <span class="text-muted">
                        {item.serving_size || 'N/A'} • {item.calories || 0} cal
                      </span>
                      <span class="text-muted">
                        P: {item.protein_g || 0}g, C: {item.carbs_g || 0}g, F: {item.fat_g || 0}g
                      </span>
                      {#if item.reasoning}
                        <span class="reasoning">💡 {item.reasoning}</span>
                      {/if}
                    </div>
                    <button class="primary" on:click={() => addItemToLog(item)}>
                      Add
                    </button>
                  </div>
                {/each}
              </div>
            {/if}
          </div>
          <small class="timestamp">
            {message.timestamp.toLocaleTimeString()}
          </small>
        </div>
      {/each}

      {#if loading}
        <div class="message assistant">
          <div class="message-content">
            <p class="text-muted">Thinking...</p>
          </div>
        </div>
      {/if}
    </div>

    <div class="input-area">
      <textarea
        bind:value={inputMessage}
        on:keydown={handleKeydown}
        placeholder="Type your message... (e.g., 'I ate 2 eggs and toast for breakfast')"
        rows="2"
        disabled={loading}
      ></textarea>
      <button
        class="primary"
        on:click={sendMessage}
        disabled={loading || !inputMessage.trim()}
      >
        Send
      </button>
    </div>
  </div>
</div>

<style>
  .chat-container {
    display: flex;
    flex-direction: column;
    height: calc(100vh - 250px);
    min-height: 500px;
  }

  .messages {
    flex: 1;
    overflow-y: auto;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .message {
    display: flex;
    flex-direction: column;
    max-width: 80%;
  }

  .message.user {
    align-self: flex-end;
  }

  .message.assistant {
    align-self: flex-start;
  }

  .message-content {
    padding: 1rem;
    border-radius: 8px;
    background: var(--bg);
  }

  .message.user .message-content {
    background: var(--primary);
    color: white;
  }

  .message-content p {
    margin: 0;
  }

  .timestamp {
    margin-top: 0.25rem;
    color: var(--text-light);
    font-size: 0.75rem;
  }

  .message.user .timestamp {
    text-align: right;
  }

  .food-items {
    margin-top: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .add-all-btn {
    width: 100%;
    margin-bottom: 0.5rem;
    background: var(--secondary);
    font-weight: 600;
    padding: 0.75rem;
  }

  .add-all-btn:hover {
    background: #F57C00;
  }

  .food-item {
    padding: 0.75rem;
    background: var(--white);
    border-radius: 4px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
  }

  .item-details {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    flex: 1;
  }

  .item-details span {
    font-size: 0.875rem;
  }

  .reasoning {
    display: block;
    font-size: 0.8rem;
    color: var(--secondary);
    font-style: italic;
    margin-top: 0.25rem;
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

  .input-area {
    padding: 1rem;
    border-top: 1px solid var(--border);
    display: flex;
    gap: 0.5rem;
  }

  .input-area textarea {
    flex: 1;
    resize: none;
    font-family: inherit;
  }

  @media (max-width: 768px) {
    .chat-container {
      height: calc(100vh - 200px);
    }

    .message {
      max-width: 90%;
    }

    .food-item {
      flex-direction: column;
      align-items: flex-start;
      gap: 0.5rem;
    }

    .food-item button {
      width: 100%;
    }

    .input-area {
      padding: 0.75rem;
    }

    .input-area textarea {
      font-size: 16px; /* Prevents zoom on iOS */
    }
  }

  @media (max-width: 480px) {
    .chat-container {
      height: calc(100vh - 180px);
      min-height: 400px;
    }

    .messages {
      padding: 0.75rem;
    }

    .message-content {
      padding: 0.75rem;
    }

    .item-details strong {
      font-size: 0.9rem;
    }
  }
</style>
