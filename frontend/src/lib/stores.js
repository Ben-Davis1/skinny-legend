import { writable } from 'svelte/store';

// Global selected date for the app
export const selectedDate = writable(new Date().toISOString().split('T')[0]);
