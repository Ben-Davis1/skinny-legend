-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Daily logs table
CREATE TABLE IF NOT EXISTS daily_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date DATE NOT NULL UNIQUE,
    total_calories REAL DEFAULT 0,
    total_water_ml INTEGER DEFAULT 0,
    exercise_minutes INTEGER DEFAULT 0,
    notes TEXT,
    calorie_goal REAL,
    protein_target_g REAL,
    carbs_target_g REAL,
    fat_target_g REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Food entries table
CREATE TABLE IF NOT EXISTS food_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    daily_log_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    calories REAL NOT NULL,
    protein_g REAL DEFAULT 0,
    carbs_g REAL DEFAULT 0,
    fat_g REAL DEFAULT 0,
    fiber_g REAL DEFAULT 0,
    sugar_g REAL DEFAULT 0,
    meal_type TEXT CHECK(meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
    image_path TEXT,
    barcode TEXT,
    serving_size TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (daily_log_id) REFERENCES daily_logs (id) ON DELETE CASCADE
);

-- Micronutrients table
CREATE TABLE IF NOT EXISTS micronutrients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    food_entry_id INTEGER NOT NULL,
    vitamin_a_mcg REAL DEFAULT 0,
    vitamin_c_mg REAL DEFAULT 0,
    vitamin_d_mcg REAL DEFAULT 0,
    vitamin_e_mg REAL DEFAULT 0,
    vitamin_k_mcg REAL DEFAULT 0,
    vitamin_b6_mg REAL DEFAULT 0,
    vitamin_b12_mcg REAL DEFAULT 0,
    folate_mcg REAL DEFAULT 0,
    calcium_mg REAL DEFAULT 0,
    iron_mg REAL DEFAULT 0,
    magnesium_mg REAL DEFAULT 0,
    potassium_mg REAL DEFAULT 0,
    zinc_mg REAL DEFAULT 0,
    sodium_mg REAL DEFAULT 0,
    FOREIGN KEY (food_entry_id) REFERENCES food_entries (id) ON DELETE CASCADE
);

-- Vitamin targets table
CREATE TABLE IF NOT EXISTS vitamin_targets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    nutrient_name TEXT NOT NULL,
    target_amount REAL NOT NULL,
    unit TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id),
    UNIQUE(user_id, nutrient_name)
);

-- Saved images table
CREATE TABLE IF NOT EXISTS saved_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    image_path TEXT NOT NULL,
    description TEXT,
    analyzed BOOLEAN DEFAULT 0,
    image_group_id TEXT,
    is_primary BOOLEAN DEFAULT 1,
    analysis_result TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- User profile table
CREATE TABLE IF NOT EXISTS user_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    age INTEGER,
    weight_kg REAL,
    height_cm REAL,
    gender TEXT CHECK(gender IN ('male', 'female', 'other')),
    activity_level TEXT CHECK(activity_level IN ('sedentary', 'lightly_active', 'moderately_active', 'very_active', 'extra_active')),
    goal TEXT CHECK(goal IN ('lose', 'maintain', 'gain')),
    tdee REAL,
    bmr REAL,
    protein_target_g REAL DEFAULT 150,
    carbs_target_g REAL DEFAULT 200,
    fat_target_g REAL DEFAULT 70,
    water_target_ml INTEGER,
    use_custom_targets BOOLEAN DEFAULT 0,
    custom_calorie_goal REAL,
    custom_protein_target_g REAL,
    custom_carbs_target_g REAL,
    custom_fat_target_g REAL,
    custom_water_target_ml INTEGER,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Insert default user
INSERT OR IGNORE INTO users (id, name) VALUES (1, 'Default User');

-- Supplements/Vitamins/Medications table
CREATE TABLE IF NOT EXISTS supplements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    daily_log_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    dosage TEXT,
    type TEXT CHECK(type IN ('vitamin', 'medication', 'supplement')) DEFAULT 'supplement',
    time_taken TEXT,
    notes TEXT,
    vitamin_a_mcg REAL DEFAULT 0,
    vitamin_c_mg REAL DEFAULT 0,
    vitamin_d_mcg REAL DEFAULT 0,
    calcium_mg REAL DEFAULT 0,
    iron_mg REAL DEFAULT 0,
    potassium_mg REAL DEFAULT 0,
    sodium_mg REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (daily_log_id) REFERENCES daily_logs (id) ON DELETE CASCADE
);

-- Weight logs table
CREATE TABLE IF NOT EXISTS weight_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date DATE NOT NULL,
    weight_kg REAL NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    UNIQUE(user_id, date)
);

-- Exercises table
CREATE TABLE IF NOT EXISTS exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    daily_log_id INTEGER NOT NULL,
    exercise_type TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (daily_log_id) REFERENCES daily_logs (id) ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_daily_logs_date ON daily_logs(date);
CREATE INDEX IF NOT EXISTS idx_daily_logs_user_id ON daily_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_food_entries_daily_log_id ON food_entries(daily_log_id);
CREATE INDEX IF NOT EXISTS idx_saved_images_user_id ON saved_images(user_id);
CREATE INDEX IF NOT EXISTS idx_supplements_daily_log_id ON supplements(daily_log_id);
CREATE INDEX IF NOT EXISTS idx_weight_logs_user_date ON weight_logs(user_id, date);
CREATE INDEX IF NOT EXISTS idx_exercises_daily_log_id ON exercises(daily_log_id);
