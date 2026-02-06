from flask import Blueprint, jsonify
import requests

bp = Blueprint('barcode', __name__, url_prefix='/api/barcode')

@bp.route('/<barcode>', methods=['GET'])
def lookup_barcode(barcode):
    """Lookup product information by barcode using OpenFoodFacts API"""
    try:
        url = f'https://world.openfoodfacts.org/api/v0/product/{barcode}.json'
        response = requests.get(url, timeout=10)
        data = response.json()

        if data['status'] == 0:
            return jsonify({'error': 'Product not found'}), 404

        product = data['product']

        # Extract nutritional information
        nutriments = product.get('nutriments', {})

        result = {
            'name': product.get('product_name', 'Unknown Product'),
            'brand': product.get('brands', ''),
            'barcode': barcode,
            'serving_size': product.get('serving_size', '100g'),
            'calories': nutriments.get('energy-kcal_100g', 0),
            'protein_g': nutriments.get('proteins_100g', 0),
            'carbs_g': nutriments.get('carbohydrates_100g', 0),
            'fat_g': nutriments.get('fat_100g', 0),
            'fiber_g': nutriments.get('fiber_100g', 0),
            'sugar_g': nutriments.get('sugars_100g', 0),
            'sodium_mg': nutriments.get('sodium_100g', 0) * 1000 if nutriments.get('sodium_100g') else 0,
            'image_url': product.get('image_url', ''),
            'micronutrients': {
                'vitamin_a_mcg': nutriments.get('vitamin-a_100g', 0) * 1000000 if nutriments.get('vitamin-a_100g') else 0,
                'vitamin_c_mg': nutriments.get('vitamin-c_100g', 0) * 1000 if nutriments.get('vitamin-c_100g') else 0,
                'vitamin_d_mcg': nutriments.get('vitamin-d_100g', 0) * 1000000 if nutriments.get('vitamin-d_100g') else 0,
                'calcium_mg': nutriments.get('calcium_100g', 0) * 1000 if nutriments.get('calcium_100g') else 0,
                'iron_mg': nutriments.get('iron_100g', 0) * 1000 if nutriments.get('iron_100g') else 0,
                'potassium_mg': nutriments.get('potassium_100g', 0) * 1000 if nutriments.get('potassium_100g') else 0,
            }
        }

        return jsonify(result)

    except requests.RequestException as e:
        return jsonify({'error': f'Failed to fetch product data: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Error processing barcode: {str(e)}'}), 500
