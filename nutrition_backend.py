import re
import pandas as pd
import numpy as np

df = pd.read_csv('/content/cleaned_nutrition_dataset.csv')

sugar_low = df['sugar'].quantile(0.33)
sugar_high = df['sugar'].quantile(0.66)
sodium_low = df['sodium'].quantile(0.33)
sodium_high = df['sodium'].quantile(0.66)
fat_low = df['fats'].quantile(0.33)
fat_high = df['fats'].quantile(0.66)
calorie_low = df['calories'].quantile(0.33)
calorie_high = df['calories'].quantile(0.66)

def nutrition_level(value, low, high):
    if value <= low:
        return "LOW"
    elif value <= high:
        return "MODERATE"
    else:
        return "HIGH"

def calorie_level(value):
    if value <= calorie_low:
        return "LOW"
    elif value <= calorie_high:
        return "MODERATE"
    else:
        return "HIGH"

def clean_ocr_text(text):

    replacements = {
        "Calorles": "Calories",
        "calorles": "Calories",
        "Sodlum": "Sodium",
        "sodlum": "Sodium",
        "Totai Fat": "Total Fat",
        "Totai fat": "Total Fat",
        "Saturat ed Fat": "Saturated Fat",
        "Prote in": "Protein",
        "F iber": "Fiber",
        "Fibre": "Fiber",
        "Cholesterol Omg": "Cholesterol 0mg",
        "Cholesterol 0mg": "Cholesterol 0mg"
    }

    for wrong, correct in replacements.items():
        text = text.replace(wrong, correct)

    return text

def extract_nutrition(text):

    nutrition = {
        "serving_size": None,
        "serving_unit": None,
        "calories": None,
        "fats": None,
        "saturated_fat": None,
        "trans_fat": None,
        "cholesterol": None,
        "sodium": None,
        "potassium": None,
        "carbs": None,
        "fiber": None,
        "sugar": None,
        "protein": None
    }

    # Serving size
    match = re.search(
        r'Serving\s*Size\s*[:\-]?\s*([\d.]+)\s*(g|ml)',
        text,
        re.IGNORECASE
    )

    if match:
        nutrition["serving_size"] = float(match.group(1))
        nutrition["serving_unit"] = match.group(2).lower()

    # Calories
    match = re.search(
        r'Calories\s*(?!from\s*Fat)\s*[:\-]?\s*([\d.]+)',
        text,
        re.IGNORECASE
    )

    if match:
        nutrition["calories"] = float(match.group(1))

    # Total Fat
    match = re.search(
        r'Total\s*Fat\s*[:\-]?\s*([\d.]+)',
        text,
        re.IGNORECASE
    )

    if match:
        nutrition["fats"] = float(match.group(1))

    # Saturated Fat
    match = re.search(
        r'Saturated\s*Fat\s*[:\-]?\s*([\d.]+)',
        text,
        re.IGNORECASE
    )

    if match:
        nutrition["saturated_fat"] = float(match.group(1))

    # Trans Fat
    match = re.search(
        r'Trans\s*Fat\s*[:\-]?\s*([\d.]+)',
        text,
        re.IGNORECASE
    )

    if match:
        nutrition["trans_fat"] = float(match.group(1))

    # Cholesterol
    match = re.search(
        r'Cholesterol\s*[:\-]?\s*([\d.]+)',
        text,
        re.IGNORECASE
    )

    if match:
        nutrition["cholesterol"] = float(match.group(1))

    # Sodium
    match = re.search(
        r'Sodium\s*[:\-]?\s*([\d.]+)',
        text,
        re.IGNORECASE
    )

    if match:
        nutrition["sodium"] = float(match.group(1))

    # Potassium
    match = re.search(
        r'Potassium\s*[:\-]?\s*([\d.]+)',
        text,
        re.IGNORECASE
    )

    if match:
        nutrition["potassium"] = float(match.group(1))

    # Carbohydrates
    match = re.search(
        r'Total\s*Carbohydrates?\s*[:\-]?\s*([\d.]+)',
        text,
        re.IGNORECASE
    )

    if match:
        nutrition["carbs"] = float(match.group(1))

    # Fibre / Fiber
    match = re.search(
        r'(?:Dietary\s*)?Fib(?:er|re)\s*[:\-]?\s*([\d.]+)',
        text,
        re.IGNORECASE
    )

    if match:
        nutrition["fiber"] = float(match.group(1))

    # Sugar
    match = re.search(
        r'(?:Total\s*)?Sugars?\s*[:\-]?\s*([\d.]+)',
        text,
        re.IGNORECASE
    )

    if match:
        nutrition["sugar"] = float(match.group(1))

    # Protein
    match = re.search(
        r'Protein\s*[:\-]?\s*([\d.]+)',
        text,
        re.IGNORECASE
    )

    if match:
        nutrition["protein"] = float(match.group(1))

    return nutrition

def fix_serving_size(nutrition, text):

    # If serving size was already detected, keep it
    if nutrition["serving_size"] is not None:
        return nutrition

    # Look for patterns such as:
    # Serving size 2/3 cup (55g)
    # Serving size 1 cup (100 g)
    match = re.search(
        r'Serving\s*Size.*?\(\s*([\d.]+)\s*(g|ml)\s*\)',
        text,
        re.IGNORECASE
    )

    if match:
        nutrition["serving_size"] = float(match.group(1))
        nutrition["serving_unit"] = match.group(2).lower()

    return nutrition

def standardize_serving_size(serving_size, serving_unit):

    if serving_size is None or serving_unit is None:
        return None, None

    serving_unit = serving_unit.lower().strip()

    if serving_unit in ["g", "gram", "grams"]:
        serving_unit = "g"

    elif serving_unit in ["ml", "milliliter", "milliliters", "millilitre", "millilitres"]:
        serving_unit = "ml"

    return serving_size, serving_unit

def check_missing_nutrition(nutrition):

    important_fields = [
        "calories",
        "sugar",
        "fats",
        "protein",
        "fiber",
        "sodium"
    ]

    missing = []

    for field in important_fields:
        if nutrition[field] is None:
            missing.append(field)

    return missing

def normalize_to_100g(nutrition):

    serving_size = nutrition["serving_size"]

    if serving_size is None or serving_size <= 0:
        return None

    normalized = {}

    nutrients = {
        "Calories": "calories",
        "Sugar": "sugar",
        "Total Fat": "fats",
        "Protein": "protein",
        "Fibre": "fiber",
        "Sodium": "sodium"
    }

    for display_name, field_name in nutrients.items():

        value = nutrition[field_name]

        if value is not None:
            normalized[display_name] = (value / serving_size) * 100
        else:
            normalized[display_name] = None

    return normalized

def normalize_to_100ml(nutrition):

    serving_size = nutrition["serving_size"]

    if serving_size is None or serving_size <= 0:
        return None

    normalized = {}

    nutrients = {
        "Calories": "calories",
        "Sugar": "sugar",
        "Total Fat": "fats",
        "Protein": "protein",
        "Fibre": "fiber",
        "Sodium": "sodium"
    }

    for display_name, field_name in nutrients.items():

        value = nutrition[field_name]

        if value is not None:
            normalized[display_name] = (value / serving_size) * 100
        else:
            normalized[display_name] = None

    return normalized

def normalize_nutrition(nutrition):

    unit = nutrition["serving_unit"]

    if unit == "g":
        return normalize_to_100g(nutrition), "per 100 g"

    elif unit == "ml":
        return normalize_to_100ml(nutrition), "per 100 ml"

    else:
        return None, "Unknown serving unit"

def safe_value(value):
    if value is None:
        return 0
    return value

def analyze_nutrition(calories, sugar, fats, saturated_fat,
                      trans_fat, protein, fiber, sodium):

    # -----------------------------------------
    # Basic nutrition analysis
    # -----------------------------------------

    result = {
        "Calories": calories,
        "Calories Level": calorie_level(calories),

        "Sugar": sugar,
        "Sugar Level": nutrition_level(
            sugar, sugar_low, sugar_high
        ),

        "Total Fat": fats,
        "Fat Level": nutrition_level(
            fats, fat_low, fat_high
        ),

        "Saturated Fat": saturated_fat,
        "Trans Fat": trans_fat,

        "Protein": protein,
        "Fibre": fiber,

        "Sodium": sodium,
        "Sodium Level": nutrition_level(
            sodium, sodium_low, sodium_high
        )
    }

    # -----------------------------------------
    # Health Screening Indicators
    # These are nutrition-based project indicators,
    # NOT medical diagnoses.
    # -----------------------------------------

    # Diabetes screening
    if sugar is None:
        diabetes_risk = "Data Unavailable"
    elif sugar <= 5:
        diabetes_risk = "Low Risk"
    elif sugar <= 10:
        diabetes_risk = "Moderate Risk"
    else:
        diabetes_risk = "Higher Risk"

    # Hypertension screening
    if sodium is None:
        hypertension_risk = "Data Unavailable"
    elif sodium <= 120:
        hypertension_risk = "Low Risk"
    elif sodium <= 300:
        hypertension_risk = "Moderate Risk"
    else:
        hypertension_risk = "Higher Risk"

    # Heart health screening
    if fats is None or saturated_fat is None or sodium is None:
        heart_health = "Data Unavailable"
    elif saturated_fat <= 3 and sodium <= 300:
        heart_health = "Favorable"
    elif saturated_fat <= 6 and sodium <= 500:
        heart_health = "Moderate"
    else:
        heart_health = "Needs Attention"

    # Weight management screening
    if calories is None:
        weight_management = "Data Unavailable"
    elif calories <= 150:
        weight_management = "Suitable"
    elif calories <= 300:
        weight_management = "Moderate"
    else:
        weight_management = "Higher Calorie"

    # Overall nutrition screening
    risk_count = 0

    if diabetes_risk == "Higher Risk":
        risk_count += 1

    if hypertension_risk == "Higher Risk":
        risk_count += 1

    if heart_health == "Needs Attention":
        risk_count += 1

    if risk_count == 0:
        overall_health = "Good"
    elif risk_count == 1:
        overall_health = "Moderate"
    else:
        overall_health = "Needs Attention"

    # Add health screening results
    result.update({
        "Diabetes Screening": diabetes_risk,
        "Hypertension Screening": hypertension_risk,
        "Heart Health Screening": heart_health,
        "Weight Management Screening": weight_management,
        "Overall Health Class": overall_health
    })

    return result

def overall_rating(analysis):

    high_count = 0

    if analysis["Calories Level"] == "HIGH":
        high_count += 1

    if analysis["Sugar Level"] == "HIGH":
        high_count += 1

    if analysis["Fat Level"] == "HIGH":
        high_count += 1

    if analysis["Sodium Level"] == "HIGH":
        high_count += 1

    if high_count == 0:
        return "GOOD"

    elif high_count <= 2:
        return "MODERATE"

    else:
        return "HIGH"



def detect_non_mass_serving(serving_text):
    """Detect non-mass serving descriptions."""
    if not serving_text:
        return False
    text = str(serving_text).lower()
    non_mass_patterns = [
        "package", "packet", "pack", "piece",
        "bar", "bottle", "can", "slice"
    ]
    return any(pattern in text for pattern in non_mass_patterns)
