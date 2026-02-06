"""
Nutritional calculations including BMR, TDEE, and calorie goals
"""

def calculate_bmr(weight_kg, height_cm, age, gender):
    """
    Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation

    Args:
        weight_kg: Weight in kilograms
        height_cm: Height in centimeters
        age: Age in years
        gender: 'male', 'female', or 'other'

    Returns:
        BMR in calories per day
    """
    if gender == 'male':
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    elif gender == 'female':
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
    else:
        # For 'other', use average of male and female formulas
        male_bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
        female_bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
        bmr = (male_bmr + female_bmr) / 2

    return bmr

def calculate_tdee(bmr, activity_level):
    """
    Calculate Total Daily Energy Expenditure

    Args:
        bmr: Basal Metabolic Rate
        activity_level: Activity level string

    Returns:
        TDEE in calories per day
    """
    activity_multipliers = {
        'sedentary': 1.2,           # Little or no exercise
        'lightly_active': 1.375,    # Light exercise 1-3 days/week
        'moderately_active': 1.55,  # Moderate exercise 3-5 days/week
        'very_active': 1.725,       # Hard exercise 6-7 days/week
        'extra_active': 1.9         # Very hard exercise & physical job
    }

    multiplier = activity_multipliers.get(activity_level, 1.2)
    return bmr * multiplier

def calculate_calorie_goal(tdee, goal):
    """
    Calculate daily calorie goal based on user's goal

    Args:
        tdee: Total Daily Energy Expenditure
        goal: 'lose', 'maintain', or 'gain'

    Returns:
        Daily calorie goal
    """
    if goal == 'lose':
        # 500 calorie deficit for ~1 lb per week loss
        return tdee - 500
    elif goal == 'gain':
        # 500 calorie surplus for ~1 lb per week gain
        return tdee + 500
    else:  # maintain
        return tdee

def calculate_macro_targets(calorie_goal, weight_kg, goal):
    """
    Calculate personalized macro targets based on user's goals and weight

    Args:
        calorie_goal: Daily calorie target
        weight_kg: User's weight in kilograms
        goal: 'lose', 'maintain', or 'gain'

    Returns:
        Dictionary with protein_g, carbs_g, fat_g targets
    """
    # Protein targets based on weight and goal (in g per kg body weight)
    protein_multipliers = {
        'lose': 2.0,      # Higher protein to preserve muscle during deficit
        'maintain': 1.6,  # Moderate protein for maintenance
        'gain': 1.8       # High protein for muscle building
    }

    protein_multiplier = protein_multipliers.get(goal, 1.6)
    protein_g = round(weight_kg * protein_multiplier)

    # Fat: 25-30% of total calories (using 27.5% average)
    fat_percentage = 0.275
    fat_g = round((calorie_goal * fat_percentage) / 9)

    # Carbs: Fill remaining calories
    # Calculate calories from protein and fat, then convert remainder to carbs
    protein_calories = protein_g * 4
    fat_calories = fat_g * 9
    remaining_calories = calorie_goal - protein_calories - fat_calories
    carbs_g = round(remaining_calories / 4)

    # Ensure carbs don't go negative
    if carbs_g < 50:
        carbs_g = 50
        # Recalculate fat to fit
        remaining_after_protein_carbs = calorie_goal - (protein_g * 4) - (carbs_g * 4)
        fat_g = round(remaining_after_protein_carbs / 9)

    return {
        'protein_g': protein_g,
        'carbs_g': carbs_g,
        'fat_g': fat_g
    }

def calculate_water_target(weight_kg, activity_level):
    """
    Calculate daily water target in ml based on weight and activity level

    Base: 35ml per kg body weight
    Activity multiplier adds extra hydration needs

    Args:
        weight_kg: User's weight in kilograms
        activity_level: Activity level string

    Returns:
        Daily water target in milliliters
    """
    # Base calculation: 35ml per kg
    base_water = weight_kg * 35

    # Activity multipliers for additional hydration needs
    activity_multipliers = {
        'sedentary': 1.0,           # No additional
        'lightly_active': 1.1,      # +10%
        'moderately_active': 1.15,  # +15%
        'very_active': 1.2,         # +20%
        'extra_active': 1.25        # +25%
    }

    multiplier = activity_multipliers.get(activity_level, 1.0)

    # Round to nearest 250ml (1 cup)
    water_target = round((base_water * multiplier) / 250) * 250

    return int(water_target)
