const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function request(endpoint, options = {}) {
    const url = `${API_URL}${endpoint}`;
    const config = {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        },
        ...options
    };

    const response = await fetch(url, config);

    if (!response.ok) {
        const error = await response.json().catch(() => ({ error: 'Request failed' }));
        throw new Error(error.error || `HTTP ${response.status}`);
    }

    return response.json();
}

// Daily Logs API
export const dailyLogs = {
    getAll: (userId = 1) => request(`/api/daily-logs?user_id=${userId}`),
    getByDate: (date, userId = 1) => request(`/api/daily-logs/${date}?user_id=${userId}`),
    create: (data) => request('/api/daily-logs', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => request(`/api/daily-logs/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id) => request(`/api/daily-logs/${id}`, { method: 'DELETE' })
};

// Food Entries API
export const foodEntries = {
    getByLog: (dailyLogId) => request(`/api/food-entries/${dailyLogId}`),
    create: (data) => request('/api/food-entries', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => request(`/api/food-entries/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id) => request(`/api/food-entries/${id}`, { method: 'DELETE' })
};

// Barcode API
export const barcode = {
    lookup: (code) => request(`/api/barcode/${code}`)
};

// Images API
export const images = {
    upload: async (file, userId = 1, description = '') => {
        const formData = new FormData();
        formData.append('image', file);
        formData.append('user_id', userId);
        formData.append('description', description);

        const response = await fetch(`${API_URL}/api/images/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Upload failed');
        }

        return response.json();
    },
    uploadMultiple: async (files, userId = 1, description = '') => {
        const formData = new FormData();

        // Add all files
        files.forEach(file => {
            formData.append('images', file);
        });

        formData.append('user_id', userId);
        formData.append('description', description);

        const response = await fetch(`${API_URL}/api/images/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Upload failed');
        }

        return response.json();
    },
    getAll: (userId = 1) => request(`/api/images?user_id=${userId}`),
    delete: (id) => request(`/api/images/${id}`, { method: 'DELETE' }),
    getImageUrl: (id) => `${API_URL}/api/images/${id}`
};

// AI API
export const ai = {
    analyzeImage: (imageId, notes = '', forceReanalyze = false) => request('/api/ai/analyze-image', {
        method: 'POST',
        body: JSON.stringify({
            image_id: imageId,
            notes: notes,
            force_reanalyze: forceReanalyze
        })
    }),
    chat: (message, history = []) => request('/api/chat', {
        method: 'POST',
        body: JSON.stringify({ message, history })
    }),
    calculateGoals: (data) => request('/api/ai/calculate-goals', {
        method: 'POST',
        body: JSON.stringify(data)
    })
};

// Nutrition API
export const nutrition = {
    getBreakdown: (date, userId = 1) => request(`/api/nutrition/${date}?user_id=${userId}`),
    getHistory: (startDate, endDate, userId = 1) =>
        request(`/api/nutrition/history?user_id=${userId}&start_date=${startDate}&end_date=${endDate}`),
    getTargets: (userId = 1) => request(`/api/nutrition/targets?user_id=${userId}`),
    setTarget: (data) => request('/api/nutrition/targets', {
        method: 'POST',
        body: JSON.stringify(data)
    }),
    deleteTarget: (id) => request(`/api/nutrition/targets/${id}`, { method: 'DELETE' })
};

// User Profile API
export const profile = {
    get: (userId = 1) => request(`/api/profile?user_id=${userId}`),
    create: (data) => request('/api/profile', { method: 'POST', body: JSON.stringify(data) }),
    update: (data) => request('/api/profile', { method: 'PUT', body: JSON.stringify(data) }),
    getCalculations: (userId = 1) => request(`/api/profile/calculations?user_id=${userId}`),
    updateDayTargets: (date, userId = 1) => request(`/api/profile/update-day-targets/${date}?user_id=${userId}`, { method: 'POST' })
};

// Weight Logs API
export const weightLogs = {
    getAll: (userId = 1, startDate = null, endDate = null) => {
        let url = `/api/weight-logs?user_id=${userId}`;
        if (startDate && endDate) {
            url += `&start_date=${startDate}&end_date=${endDate}`;
        }
        return request(url);
    },
    create: (data) => request('/api/weight-logs', { method: 'POST', body: JSON.stringify(data) }),
    delete: (id) => request(`/api/weight-logs/${id}`, { method: 'DELETE' }),
    getLatest: (userId = 1) => request(`/api/weight-logs/latest?user_id=${userId}`)
};

// Recently Used Foods API
export const recentFoods = {
    get: (userId = 1, limit = 20) => request(`/api/food-entries/recent?user_id=${userId}&limit=${limit}`)
};

// Exercises API
export const exercises = {
    getByLog: (dailyLogId) => request(`/api/exercises/${dailyLogId}`),
    create: (data) => request('/api/exercises', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => request(`/api/exercises/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id) => request(`/api/exercises/${id}`, { method: 'DELETE' })
};

// Supplements API
export const supplements = {
    getByLog: (dailyLogId) => request(`/api/supplements/${dailyLogId}`),
    getRecent: (userId = 1) => request(`/api/supplements/recent?user_id=${userId}`),
    create: (data) => request('/api/supplements', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => request(`/api/supplements/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id) => request(`/api/supplements/${id}`, { method: 'DELETE' })
};

// Workouts API
export const workouts = {
    // Sessions
    createSession: (data) => request('/api/workouts/sessions', {
        method: 'POST',
        body: JSON.stringify(data)
    }),
    getSessions: (dailyLogId) => request(`/api/workouts/sessions/${dailyLogId}`),
    updateSession: (sessionId, data) => request(`/api/workouts/sessions/${sessionId}`, {
        method: 'PUT',
        body: JSON.stringify(data)
    }),
    deleteSession: (sessionId) => request(`/api/workouts/sessions/${sessionId}`, {
        method: 'DELETE'
    }),
    getSessionDetails: (sessionId) => request(`/api/workouts/session-details/${sessionId}`),

    // Exercises
    createExercise: (data) => request('/api/workouts/exercises', {
        method: 'POST',
        body: JSON.stringify(data)
    }),
    getExercises: (sessionId) => request(`/api/workouts/exercises/${sessionId}`),
    deleteExercise: (exerciseId) => request(`/api/workouts/exercises/${exerciseId}`, {
        method: 'DELETE'
    }),

    // Sets
    createSet: (data) => request('/api/workouts/sets', {
        method: 'POST',
        body: JSON.stringify(data)
    }),
    getSets: (exerciseId) => request(`/api/workouts/sets/${exerciseId}`),
    updateSet: (setId, data) => request(`/api/workouts/sets/${setId}`, {
        method: 'PUT',
        body: JSON.stringify(data)
    }),
    deleteSet: (setId) => request(`/api/workouts/sets/${setId}`, {
        method: 'DELETE'
    }),

    // History & Analytics
    getHistory: (exerciseName, userId = 1, limit = 10) =>
        request(`/api/workouts/history/${encodeURIComponent(exerciseName)}?user_id=${userId}&limit=${limit}`),
    getStats: (exerciseName, userId = 1) =>
        request(`/api/workouts/stats/${encodeURIComponent(exerciseName)}?user_id=${userId}`),
    getRecentExercises: (userId = 1, limit = 15) =>
        request(`/api/workouts/recent-exercises?user_id=${userId}&limit=${limit}`),
    getDailySummary: (startDate, endDate, userId = 1) =>
        request(`/api/workouts/daily-summary?user_id=${userId}&start_date=${startDate}&end_date=${endDate}`),
    getByDate: (date, userId = 1) =>
        request(`/api/workouts/by-date/${date}?user_id=${userId}`)
};
