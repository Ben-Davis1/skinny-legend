import anthropic
import os
import base64
import json

client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

def analyze_food_image(image_path, custom_notes='', additional_images=None):
    """Analyze a food image (or multiple images) and extract nutritional information"""
    try:
        # Helper function to encode image
        def encode_image(path):
            with open(path, 'rb') as f:
                return base64.standard_b64encode(f.read()).decode('utf-8')

        def get_media_type(path):
            ext = path.split('.')[-1].lower()
            media_type_map = {
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg',
                'png': 'image/png',
                'gif': 'image/gif',
                'webp': 'image/webp'
            }
            return media_type_map.get(ext, 'image/jpeg')

        # Build content array with all images
        content = []

        # Add primary image
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": get_media_type(image_path),
                "data": encode_image(image_path)
            }
        })

        # Add additional images if provided
        if additional_images:
            for img_path in additional_images:
                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": get_media_type(img_path),
                        "data": encode_image(img_path)
                    }
                })

        # Build prompt for Claude
        if additional_images and len(additional_images) > 0:
            prompt = f"""Analyze these {len(additional_images) + 1} images from different angles and provide detailed nutritional information.

Using multiple views, estimate the portion size and nutritional content more accurately.

IMPORTANT: Identify ALL items in the images including:
- Food items (main dishes, sides, snacks, desserts)
- Beverages (drinks, smoothies, juices, coffee, tea, soda, etc.)
- Each item should be listed separately with its own nutritional data."""
        else:
            prompt = """Analyze this image and provide detailed nutritional information.

IMPORTANT: Identify ALL items in the image including:
- Food items (main dishes, sides, snacks, desserts)
- Beverages (drinks, smoothies, juices, coffee, tea, soda, alcohol, etc.)
- Each item should be listed separately with its own nutritional data."""

        # Add custom instructions if provided
        if custom_notes:
            prompt += f"\n\nIMPORTANT USER NOTES: {custom_notes}\nPlease take these notes into account when analyzing the image(s)."

        # Add JSON format instructions
        prompt += """

CRITICAL: You MUST respond with ONLY valid JSON. Do not include any text before or after the JSON.

Return ONLY this JSON structure with your estimates:
{
    "items": [
        {
            "name": "food name",
            "serving_size": "estimated size (e.g., '1 cup', '100g', '1 medium apple')",
            "calories": 0,
            "protein_g": 0,
            "carbs_g": 0,
            "fat_g": 0,
            "fiber_g": 0,
            "sugar_g": 0,
            "micronutrients": {
                "vitamin_a_mcg": 0,
                "vitamin_c_mg": 0,
                "vitamin_d_mcg": 0,
                "calcium_mg": 0,
                "iron_mg": 0,
                "potassium_mg": 0,
                "sodium_mg": 0
            }
        }
    ],
    "confidence": "high|medium|low",
    "notes": "any observations about portion size or angles viewed"
}

Replace the 0 values with your estimates. Be as accurate as possible."""

        # Add the text prompt to content
        content.append({
            "type": "text",
            "text": prompt
        })

        # Call Claude API (using latest Haiku - most cost-efficient)
        message = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": content
                }
            ]
        )

        # Parse response
        response_text = message.content[0].text

        # Debug: Log the raw response
        print(f"Claude Response: {response_text[:500]}...")  # First 500 chars

        # Extract JSON from response (handle potential markdown code blocks)
        json_str = None
        if '```json' in response_text:
            json_start = response_text.find('```json') + 7
            json_end = response_text.find('```', json_start)
            json_str = response_text[json_start:json_end].strip()
        elif '```' in response_text:
            json_start = response_text.find('```') + 3
            json_end = response_text.find('```', json_start)
            json_str = response_text[json_start:json_end].strip()
        else:
            json_str = response_text.strip()

        # Try to parse JSON
        try:
            result = json.loads(json_str)
            return result
        except json.JSONDecodeError as json_err:
            # If JSON parsing fails, create a fallback response
            print(f"JSON Parse Error: {json_err}")
            print(f"Attempted to parse: {json_str[:200]}...")

            # Return a structured error response
            return {
                "items": [],
                "confidence": "low",
                "notes": f"Could not parse AI response. Raw response: {response_text[:200]}...",
                "error": "json_parse_failed"
            }

    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse JSON response: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to analyze image: {str(e)}")

def get_food_suggestions(user_message, conversation_history=None):
    """Get food entry suggestions from natural language"""
    try:
        # Build conversation
        messages = []

        if conversation_history:
            messages.extend(conversation_history)

        # System-like message as first user message if history is empty
        if not messages:
            messages.append({
                "role": "user",
                "content": """You are a nutrition assistant that extracts food information from user descriptions.

CRITICAL RULES:
1. ONLY respond with valid JSON - no other text
2. Extract ALL food items mentioned
3. Provide realistic nutritional estimates based on typical servings
4. Break down mixed dishes into individual components

Response format (respond with ONLY this JSON):
{
    "items": [
        {
            "name": "Shokopan Toast with Flora Butter",
            "serving_size": "2 slices",
            "calories": 280,
            "protein_g": 8,
            "carbs_g": 45,
            "fat_g": 8,
            "fiber_g": 3,
            "sugar_g": 6,
            "meal_type": "breakfast"
        }
    ],
    "actions": {
        "water_ml": 0,
        "exercise": {"type": "", "duration_minutes": 0, "notes": ""}
    },
    "needs_clarification": false,
    "message": "I found 2 slices of shokopan toast with Flora butter from your breakfast. Would you like to add this?"
}

Meal type detection:
- "breakfast", "morning" = "breakfast"
- "lunch", "midday" = "lunch"
- "dinner", "evening" = "dinner"
- Otherwise = "snack"

EXAMPLES:

User: "I had 2 eggs and toast for breakfast"
Response:
{
    "items": [
        {"name": "Scrambled Eggs", "serving_size": "2 eggs", "calories": 180, "protein_g": 12, "carbs_g": 2, "fat_g": 14, "fiber_g": 0, "sugar_g": 1, "meal_type": "breakfast"},
        {"name": "Toast", "serving_size": "2 slices", "calories": 160, "protein_g": 6, "carbs_g": 30, "fat_g": 2, "fiber_g": 2, "sugar_g": 4, "meal_type": "breakfast"}
    ],
    "actions": {"water_ml": 0, "exercise": {"type": "", "duration_minutes": 0, "notes": ""}},
    "needs_clarification": false,
    "message": "I found eggs and toast from your breakfast. Would you like to add these items?"
}

User: "200g chicken breast and salad for lunch"
Response:
{
    "items": [
        {"name": "Chicken Breast", "serving_size": "200g", "calories": 330, "protein_g": 62, "carbs_g": 0, "fat_g": 7, "fiber_g": 0, "sugar_g": 0, "meal_type": "lunch"},
        {"name": "Mixed Salad", "serving_size": "1 bowl", "calories": 50, "protein_g": 2, "carbs_g": 8, "fat_g": 1, "fiber_g": 3, "sugar_g": 4, "meal_type": "lunch"}
    ],
    "actions": {"water_ml": 0, "exercise": {"type": "", "duration_minutes": 0, "notes": ""}},
    "needs_clarification": false,
    "message": "I found chicken breast and salad from your lunch. Ready to add?"
}

Remember: ONLY JSON, no explanations."""
            })
            messages.append({
                "role": "assistant",
                "content": '{"items": [], "actions": {"water_ml": 0, "exercise": {"type": "", "duration_minutes": 0, "notes": ""}}, "needs_clarification": false, "message": "I understand. I will respond with only JSON format."}'
            })

        # Add user message
        messages.append({
            "role": "user",
            "content": user_message
        })

        # Call Claude (using Sonnet for better instruction following)
        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=2048,
            messages=messages
        )

        response_text = message.content[0].text

        # Debug: Log the raw response
        print(f"Chat Response: {response_text[:300]}...")

        # Try to extract JSON
        try:
            if '```json' in response_text:
                json_start = response_text.find('```json') + 7
                json_end = response_text.find('```', json_start)
                json_str = response_text[json_start:json_end].strip()
            elif '```' in response_text:
                json_start = response_text.find('```') + 3
                json_end = response_text.find('```', json_start)
                json_str = response_text[json_start:json_end].strip()
            else:
                # Try to parse the whole response
                json_str = response_text.strip()

            result = json.loads(json_str)
        except json.JSONDecodeError as e:
            # If JSON parsing fails, return a helpful message
            print(f"Chat JSON Parse Error: {e}")
            print(f"Attempted to parse: {json_str[:200] if json_str else 'None'}...")
            print(f"Full response: {response_text}")

            # Try to be helpful even when parsing fails
            result = {
                "items": [],
                "needs_clarification": True,
                "message": "I understand you mentioned some food, but I'm having trouble parsing the details. Could you try describing it more simply? For example: 'I had 2 eggs and toast for breakfast' or 'chicken breast 200g for lunch'"
            }

        return result

    except Exception as e:
        raise Exception(f"Failed to process message: {str(e)}")

def estimate_micronutrients(food_name, calories, protein_g, carbs_g, fat_g):
    """Estimate micronutrients based on food name and macros"""
    try:
        prompt = f"""Based on this food item, estimate the micronutrient content:

Food: {food_name}
Calories: {calories}
Protein: {protein_g}g
Carbs: {carbs_g}g
Fat: {fat_g}g

CRITICAL: You MUST respond with ONLY valid JSON. Do not include any text before or after the JSON.

Provide realistic micronutrient estimates in this exact JSON format:
{{
    "vitamin_a_mcg": 0,
    "vitamin_c_mg": 0,
    "vitamin_d_mcg": 0,
    "calcium_mg": 0,
    "iron_mg": 0,
    "potassium_mg": 0,
    "sodium_mg": 0
}}

Use your knowledge of typical micronutrient content for this food. If the food typically has none of a nutrient, use 0."""

        message = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text

        # Extract JSON
        json_str = response_text.strip()
        if '```json' in response_text:
            json_start = response_text.find('```json') + 7
            json_end = response_text.find('```', json_start)
            json_str = response_text[json_start:json_end].strip()
        elif '```' in response_text:
            json_start = response_text.find('```') + 3
            json_end = response_text.find('```', json_start)
            json_str = response_text[json_start:json_end].strip()

        result = json.loads(json_str)
        return result

    except Exception as e:
        print(f"Failed to estimate micronutrients: {str(e)}")
        # Return empty micronutrients on error
        return {
            "vitamin_a_mcg": 0,
            "vitamin_c_mg": 0,
            "vitamin_d_mcg": 0,
            "calcium_mg": 0,
            "iron_mg": 0,
            "potassium_mg": 0,
            "sodium_mg": 0
        }

def estimate_supplement_micronutrients(supplement_name, dosage):
    """Estimate micronutrient contribution from a supplement"""
    try:
        prompt = f"""Based on this supplement, determine which micronutrients it provides and in what amounts:

Supplement: {supplement_name}
Dosage: {dosage}

CRITICAL: You MUST respond with ONLY valid JSON. Do not include any text before or after the JSON.

Common conversions:
- IU to mcg for Vitamin D: 1 IU = 0.025 mcg
- IU to mcg for Vitamin A: 1 IU = 0.3 mcg
- mg stays as mg

Provide the micronutrient amounts in this exact JSON format:
{{
    "vitamin_a_mcg": 0,
    "vitamin_c_mg": 0,
    "vitamin_d_mcg": 0,
    "calcium_mg": 0,
    "iron_mg": 0,
    "potassium_mg": 0,
    "sodium_mg": 0
}}

Only include amounts for nutrients this supplement actually provides. Use 0 for nutrients it doesn't provide."""

        message = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text

        # Extract JSON
        json_str = response_text.strip()
        if '```json' in response_text:
            json_start = response_text.find('```json') + 7
            json_end = response_text.find('```', json_start)
            json_str = response_text[json_start:json_end].strip()
        elif '```' in response_text:
            json_start = response_text.find('```') + 3
            json_end = response_text.find('```', json_start)
            json_str = response_text[json_start:json_end].strip()

        result = json.loads(json_str)
        return result

    except Exception as e:
        print(f"Failed to estimate supplement micronutrients: {str(e)}")
        return {
            "vitamin_a_mcg": 0,
            "vitamin_c_mg": 0,
            "vitamin_d_mcg": 0,
            "calcium_mg": 0,
            "iron_mg": 0,
            "potassium_mg": 0,
            "sodium_mg": 0
        }
