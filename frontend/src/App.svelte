<script>
  import Router from 'svelte-spa-router';
  import { wrap } from 'svelte-spa-router/wrap';
  import { selectedDate } from './lib/stores.js';

  // Import pages
  import Dashboard from './pages/Dashboard.svelte';
  import History from './pages/History.svelte';
  import SavedImages from './pages/SavedImages.svelte';
  import AIChat from './pages/AIChat.svelte';
  import Nutrition from './pages/Nutrition.svelte';
  import Profile from './pages/Profile.svelte';

  let currentDate;
  selectedDate.subscribe(value => {
    currentDate = value;
  });

  function goToToday() {
    selectedDate.set(new Date().toISOString().split('T')[0]);
  }

  function changeDay(offset) {
    const date = new Date(currentDate);
    date.setDate(date.getDate() + offset);
    selectedDate.set(date.toISOString().split('T')[0]);
  }

  // Define routes
  const routes = {
    '/': Dashboard,
    '/history': History,
    '/images': SavedImages,
    '/ai-chat': AIChat,
    '/chat': AIChat, // Alias for backwards compatibility
    '/nutrition': Nutrition,
    '/nutrition/:date': Nutrition,
    '/profile': Profile,
  };

  // Router options to prevent scroll reset
  const routeOptions = {
    restoreScrollState: true
  };

  let activeRoute = '/';

  function handleRouteLoaded(event) {
    activeRoute = event.detail.location;
  }
</script>

<div class="app">
  <nav class="nav">
    <div class="nav-content">
      <div class="nav-left">
        <h2>Skinny Legend</h2>
        <div class="date-selector">
          <button class="date-nav" on:click={() => changeDay(-1)}>◀</button>
          <input
            type="date"
            bind:value={currentDate}
            on:change={(e) => selectedDate.set(e.target.value)}
            class="date-input"
          />
          <button class="date-nav" on:click={() => changeDay(1)}>▶</button>
          <button class="today-btn" on:click={goToToday}>Today</button>
        </div>
      </div>
      <ul class="nav-links">
        <li><a href="#/" class:active={activeRoute === '/'}>Dashboard</a></li>
        <li><a href="#/history" class:active={activeRoute === '/history'}>History</a></li>
        <li><a href="#/images" class:active={activeRoute === '/images'}>Images</a></li>
        <li><a href="#/ai-chat" class:active={activeRoute === '/ai-chat' || activeRoute === '/chat'}>AI Chat</a></li>
        <li><a href="#/profile" class:active={activeRoute === '/profile'}>Profile</a></li>
      </ul>
    </div>
  </nav>

  <main>
    <Router {routes} {routeOptions} on:routeLoaded={handleRouteLoaded} />
  </main>
</div>

<style>
  .app {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  main {
    flex: 1;
  }

  .nav-left {
    display: flex;
    align-items: center;
    gap: 2rem;
  }

  .date-selector {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .date-nav {
    padding: 0.25rem 0.5rem;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 4px;
    font-size: 0.875rem;
  }

  .date-nav:hover {
    background: var(--border);
  }

  .date-input {
    padding: 0.25rem 0.5rem;
    border: 1px solid var(--border);
    border-radius: 4px;
    font-size: 0.875rem;
  }

  .today-btn {
    padding: 0.25rem 0.75rem;
    background: var(--primary);
    color: white;
    border-radius: 4px;
    font-size: 0.875rem;
  }

  @media (max-width: 768px) {
    .nav-content {
      flex-direction: column;
      gap: 1rem;
    }

    .nav-left {
      flex-direction: column;
      gap: 1rem;
      width: 100%;
    }

    .date-selector {
      width: 100%;
      justify-content: center;
    }
  }
</style>
