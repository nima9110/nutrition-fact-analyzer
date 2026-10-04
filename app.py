
import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import io

# Import project backend
from nutrition_backend import (
    clean_ocr_text,
    extract_nutrition,
    fix_serving_size,
    standardize_serving_size,
    check_missing_nutrition,
    normalize_nutrition,
    analyze_nutrition,
    overall_rating,
    safe_value
)

# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------

st.set_page_config(
    page_title="Nutrition Fact Analyzer",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------------------------------------------------------
# CUSTOM CSS
# ------------------------------------------------------------

st.markdown("""
<style>

    /* Main page */
    .stApp {
        background: #f7f9f7;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Hero */
    .hero {
        background: linear-gradient(135deg, #86c296, #1F5C45);
        padding: 2.2rem 2.5rem;
        border-radius: 24px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }

    .hero h1 {
        color: #f5a00f;
        font-size: 3rem;
        margin-bottom: 0.3rem;
        font-weight: 800;
    }

    .hero p {
        color: #e8f5ee;
        font-size: 1.15rem;
        margin-bottom: 0;
    }

    .tag {
        display: inline-block;
        background: rgba(255,255,255,0.15);
        color: white;
        padding: 0.35rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin-top: 1rem;
    }

    /* Section cards */
    .section-card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #e6ece8;
        box-shadow: 0 4px 18px rgba(0,0,0,0.06);
    }

    .section-title {
        font-size: 1.45rem;
        font-weight: 750;
        margin-bottom: 0.3rem;
        color: #17352A;
    }

    .section-subtitle {
        color: #66756d;
        margin-bottom: 1rem;
    }

    /* Nutrient cards */
    .nutrient-card {
        background: white;
        border-radius: 16px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #e1e8e3;
        min-height: 110px;
        box-shadow: 0 3px 12px rgba(0,0,0,0.05);
    }

    .nutrient-name {
        color: #66756d;
        font-size: 0.88rem;
        margin-bottom: 0.35rem;
    }

    .nutrient-value {
        color: #17352A;
        font-size: 1.45rem;
        font-weight: 800;
    }

    /* Rating */
    .rating-box {
        background: #ffffff;
        border-radius: 20px;
        padding: 1.5rem;
        text-align: center;
        border: 2px solid #dce8df;
        box-shadow: 0 5px 20px rgba(0,0,0,0.07);
    }

    .rating-title {
        color: #66756d;
        font-size: 0.9rem;
    }

    .rating-value {
        font-size: 2.2rem;
        font-weight: 850;
        color: #17352A;
        margin-top: 0.3rem;
    }

    /* Comparison */
    .comparison-result {
        background: #e6b909;
        color: white;
        padding: 1.5rem;
        border-radius: 18px;
        text-align: center;
        margin-top: 1.2rem;
    }

    .comparison-result h2 {
        color: white;
        margin-bottom: 0.4rem;
    }

    /* Understanding the result */
    .result-explanation {
        background: #f0f7f2;
        border-left: 5px solid #17352A;
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }

    .result-explanation-title {
        color: #17352A;
        font-size: 1.05rem;
        font-weight: 800;
        margin-bottom: 0.7rem;
    }

    .result-explanation-text {
        color: #30483d;
        font-size: 0.98rem;
        line-height: 1.6;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #78847e;
        font-size: 0.8rem;
        padding-top: 2rem;
        border-top: 1px solid #dfe6e1;
        margin-top: 3rem;
    }

    /* Streamlit tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #eef4ef;
        padding: 8px;
        border-radius: 14px;
    }

    .stTabs [data-baseweb="tab"] {
        color: #fcba03 !important;
        font-weight: 750 !important;
        font-size: 1rem !important;
        background: #ffffff !important;
        border-radius: 10px;
        padding: 10px 18px;
    }

    .stTabs [aria-selected="true"] {
        color: #ffffff !important;
        background: #17352A !important;
    }

    /* Make markdown headings visible */
    .stMarkdown h1,
    .stMarkdown h2,
    .stMarkdown h3,
    .stMarkdown h4 {
        color: #17352A !important;
    }

    /* File uploader labels */
    .stFileUploader label,
    .stCameraInput label {
        color: #17352A !important;
        font-weight: 650 !important;
    }

    /* Number input labels */
    .stNumberInput label {
        color: #17352A !important;
        font-weight: 650 !important;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 12px;
        font-weight: 650;
    }




/* ---------- STREAMLIT TABS ---------- */

button[data-baseweb="tab"] {
    color: #fcba03 !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
}

button[data-baseweb="tab"] p {
    color: #17352A !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #0B6B4F !important;
}


/* ---------- PRODUCT A / PRODUCT B ---------- */

.product-heading {
    background: #E8F5EF;
    border-left: 6px solid #0B6B4F;
    padding: 12px 18px;
    border-radius: 10px;
    margin: 12px 0 18px 0;
    color: #17352A !important;
    font-size: 1.25rem;
    font-weight: 700;
}


/* ---------- HEALTH SCREENING ---------- */

.health-title {
    color: #ebb802;
    font-size: 1.35rem;
    font-weight: 800;
    margin-top: 20px;
    margin-bottom: 12px;
}

.health-card {
    background: white;
    border-radius: 12px;
    padding: 16px;
    min-height: 105px;
    border: 1px solid #DCE9E2;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    margin-bottom: 12px;
}

.health-card-title {
    font-size: 0.9rem;
    color: #587067;
    font-weight: 600;
    margin-bottom: 8px;
}

.health-card-value {
    font-size: 1.08rem;
    color: #17352A;
    font-weight: 800;
}


/* ---------- UNDERSTANDING RESULT ---------- */

.result-explanation {
    background: #F4F8F5;
    border-left: 5px solid #0B6B4F;
    border-radius: 10px;
    padding: 16px 18px;
    margin-top: 12px;
    color: #263A32;
    line-height: 1.6;
}


/* ---------- COMPARISON WINNER ---------- */

.winner-card {
    background: #17352A;
    color: white;
    border-radius: 14px;
    padding: 22px;
    margin-top: 18px;
    text-align: center;
}

.winner-title {
    font-size: 1.45rem;
    font-weight: 800;
    margin-bottom: 8px;
}

.winner-name {
    font-size: 1.7rem;
    font-weight: 900;
    margin: 8px 0;
}

.winner-detail {
    font-size: 1rem;
    opacity: 0.95;
}


/* ---------- FILE UPLOADER LABELS ---------- */

[data-testid="stFileUploader"] label,
[data-testid="stFileUploader"] label p {
    color: #17352A !important;
    font-weight: 600 !important;
}


/* ---------- NUMBER INPUT LABELS ---------- */

[data-testid="stNumberInput"] label,
[data-testid="stNumberInput"] label p {
    color: #17352A !important;
    font-weight: 600 !important;
}


</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------
# HERO HEADER
# ------------------------------------------------------------

st.markdown("""
<div class="hero">
    <h1>🥗 Nutrition Fact Analyzer</h1>
    <p>Scan • Understand • Compare</p>
    <div class="tag">
        Data Science-Based Food Nutrition Analysis System
    </div>
</div>
""", unsafe_allow_html=True)


# ------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------

def preprocess_image(image):
    """
    Improve nutrition-label image before OCR.
    """
    image = image.convert("L")

    # Increase contrast
    image = ImageEnhance.Contrast(image).enhance(2.0)

    # Sharpen
    image = image.filter(ImageFilter.SHARPEN)

    # Resize for better OCR
    image = image.resize(
        (image.width * 3, image.height * 3)
    )

    return image


def process_image(uploaded_file):
    """
    Image -> OCR -> cleaned OCR -> structured nutrition data
    """

    image = Image.open(uploaded_file)

    processed = preprocess_image(image)

    text = pytesseract.image_to_string(
        processed,
        config="--psm 6"
    )

    cleaned_text = clean_ocr_text(text)

    nutrition = extract_nutrition(cleaned_text)

    # Fix / standardize serving information
    try:
        nutrition = fix_serving_size(nutrition)
    except Exception:
        pass

    try:
        nutrition = standardize_serving_size(nutrition)
    except Exception:
        pass

    return image, processed, text, cleaned_text, nutrition


def display_nutrient_card(name, value, unit=""):
    if value is None or str(value).strip() == "":
        value_text = "Not available"
    else:
        value_text = f"{value} {unit}".strip()

    st.markdown(
        f"""
        <div class="nutrient-card">
            <div class="nutrient-name">{name}</div>
            <div class="nutrient-value">{value_text}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def get_value(data, key):
    value = data.get(key)

    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except Exception:
        pass

    return value


def is_non_mass_serving(nutrition):
    """
    Detect servings such as:
    package, packet, piece, bottle, can, bar, etc.
    """

    serving = str(
        nutrition.get("serving_size", "")
    ).lower()

    keywords = [
        "package",
        "packet",
        "pack",
        "piece",
        "bar",
        "bottle",
        "can",
        "slice",
        "container"
    ]

    return any(word in serving for word in keywords)


def numeric_value(value):
    try:
        if value is None:
            return None

        if pd.isna(value):
            return None

        return float(value)
    except Exception:
        return None


def compare_products(product_a, product_b):
    """
    Compare only nutrients available for BOTH products.
    Missing values are NOT treated as zero.
    """

    nutrients = [
        ("Calories", "calories", "kcal", True),
        ("Sugar", "sugar", "g", False),
        ("Fat", "fats", "g", False),
        ("Protein", "protein", "g", True),
        ("Fibre", "fiber", "g", True),
        ("Sodium", "sodium", "mg", True)
    ]

    rows = []
    scores_a = 0
    scores_b = 0
    comparable = 0

    for label, key, unit, lower_is_better in nutrients:

        a = numeric_value(product_a.get(key))
        b = numeric_value(product_b.get(key))

        if a is None or b is None:
            winner = "Not available"
        else:
            comparable += 1

            if abs(a - b) < 1e-9:
                winner = "Equal"
            elif lower_is_better:
                winner = "Product A" if a < b else "Product B"
                if a < b:
                    scores_a += 1
                else:
                    scores_b += 1
            else:
                winner = "Product A" if a > b else "Product B"
                if a > b:
                    scores_a += 1
                else:
                    scores_b += 1

        rows.append({
            "Nutrient": label,
            "Product A": (
                f"{a:g} {unit}" if a is not None else "Not available"
            ),
            "Product B": (
                f"{b:g} {unit}" if b is not None else "Not available"
            ),
            "Better": winner
        })

    table = pd.DataFrame(rows)

    if comparable == 0:
        result = "Not enough comparable nutrition data"
    elif scores_a > scores_b:
        result = "Product A has the better overall nutrition profile"
    elif scores_b > scores_a:
        result = "Product B has the better overall nutrition profile"
    else:
        result = "Both products have a similar overall profile"

    return table, scores_a, scores_b, comparable, result


# ------------------------------------------------------------
# MAIN TABS
# ------------------------------------------------------------

tab1, tab2 = st.tabs([
    "📸 Analyze a Product",
    "⚖️ Compare Products"
])




def _flatten_analysis(data, prefix=""):
    """Flatten nested analysis dictionaries."""
    items = []

    if isinstance(data, dict):
        for key, value in data.items():
            new_prefix = f"{prefix} {key}".strip()

            if isinstance(value, dict):
                items.extend(_flatten_analysis(value, new_prefix))
            else:
                items.append((new_prefix, value))

    return items


def _find_analysis_value(data, keyword_groups):
    """
    Find a value in the analysis dictionary using flexible keywords.
    keyword_groups is checked in order.
    """
    flattened = _flatten_analysis(data)

    for group in keyword_groups:
        required_words = [
            str(word).lower().replace("_", " ").replace("-", " ")
            for word in group
        ]

        for key, value in flattened:
            normalized_key = (
                str(key)
                .lower()
                .replace("_", " ")
                .replace("-", " ")
            )

            if all(word in normalized_key for word in required_words):
                return value

    return None


def _health_card(title, value):
    if value is None:
        value = "Data Unavailable"

    return f"""
    <div class="health-card">
        <div class="health-card-title">{title}</div>
        <div class="health-card-value">{value}</div>
    </div>
    """

# ============================================================
# TAB 1 - SINGLE PRODUCT
# ============================================================

with tab1:

    st.markdown("""
    <div class="section-card">
        <div class="section-title">📸 Analyze a Nutrition Label</div>
        <div class="section-subtitle">
            Upload a nutrition facts label or capture one using your camera.
            OCR extracts the nutritional information automatically.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        camera_file = st.camera_input(
            "📷 Take a photo of the nutrition label"
        )

    with col2:
        uploaded_file = st.file_uploader(
            "📁 Upload a nutrition-label image",
            type=["png", "jpg", "jpeg", "webp"]
        )

    selected_file = camera_file if camera_file is not None else uploaded_file

    if selected_file is not None:

        with st.spinner("🔎 Reading and analyzing the nutrition label..."):

            try:
                (
                    original_image,
                    processed_image,
                    raw_text,
                    cleaned_text,
                    nutrition
                ) = process_image(selected_file)

                st.success("✅ Nutrition label processed successfully!")

                # ------------------------------------------------
                # OCR SECTION
                # ------------------------------------------------

                st.markdown("""
                <div class="section-card">
                    <div class="section-title">🔎 OCR & Extracted Information</div>
                    <div class="section-subtitle">
                        Text detected from the nutrition label.
                    </div>
                </div>
                """, unsafe_allow_html=True)

                col_img, col_text = st.columns([1, 1])

                with col_img:
                    st.image(
                        original_image,
                        caption="Nutrition Label",
                        use_container_width=True
                    )

                with col_text:
                    st.text_area(
                        "Extracted OCR text",
                        cleaned_text,
                        height=280
                    )

                # ------------------------------------------------
                # NUTRITION VALUES
                # ------------------------------------------------

                st.markdown("""
                <div class="section-card">
                    <div class="section-title">🧾 Extracted Nutrition Facts</div>
                </div>
                """, unsafe_allow_html=True)

                nutrient_cols = st.columns(4)

                nutrients_to_show = [
                    ("Calories", "calories", "kcal"),
                    ("Total Fat", "fats", "g"),
                    ("Saturated Fat", "saturated_fat", "g"),
                    ("Cholesterol", "cholesterol", "mg"),
                    ("Sodium", "sodium", "mg"),
                    ("Carbohydrates", "carbs", "g"),
                    ("Fibre", "fiber", "g"),
                    ("Sugar", "sugar", "g"),
                    ("Protein", "protein", "g"),
                    ("Potassium", "potassium", "mg"),
                ]

                for index, (label, key, unit) in enumerate(
                    nutrients_to_show
                ):
                    with nutrient_cols[index % 4]:
                        display_nutrient_card(
                            label,
                            get_value(nutrition, key),
                            unit
                        )

                # ------------------------------------------------
                # SERVING
                # ------------------------------------------------

                serving = nutrition.get(
                    "serving_size",
                    "Not available"
                )

                st.info(
                    f"🍽️ Serving information: **{serving}**"
                )

                # ------------------------------------------------
                # ANALYSIS
                # ------------------------------------------------

                st.markdown("""
                <div class="section-card">
                    <div class="section-title">📊 Nutrition Analysis</div>
                    <div class="section-subtitle">
                        The extracted nutrition values are evaluated
                        using the project's nutrition-analysis logic.
                    </div>
                </div>
                """, unsafe_allow_html=True)

                try:
                    analysis = analyze_nutrition(
                nutrition.get("calories"),
                nutrition.get("sugar"),
                nutrition.get("fats"),
                nutrition.get("saturated_fat"),
                nutrition.get("trans_fat"),
                nutrition.get("protein"),
                nutrition.get("fiber"),
                nutrition.get("sodium")
            )

                    # Show analysis dictionary in a clean table
                    if isinstance(analysis, dict):

                        analysis_rows = []

                        for key, value in analysis.items():

                            if isinstance(value, dict):
                                for subkey, subvalue in value.items():
                                    analysis_rows.append({
                                        "Indicator":
                                            f"{key} - {subkey}",
                                        "Result": subvalue
                                    })
                            else:
                                analysis_rows.append({
                                    "Indicator": key,
                                    "Result": value
                                })

                        if analysis_rows:
                            analysis_df = pd.DataFrame(
                                analysis_rows
                            )

                            st.dataframe(
                                analysis_df,
                                use_container_width=True,
                                hide_index=True
                            )

                    # Overall rating
                    try:
                        rating = overall_rating(analysis)
                    except Exception:
                        rating = "Available"

                    st.markdown(
                        f"""
                        <div class="rating-box">
                            <div class="rating-title">
                                OVERALL NUTRITION RATING
                            </div>
                            <div class="rating-value">
                                ⭐ {rating}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                except Exception as e:

                    st.warning(
                        "Nutrition analysis could not be displayed "
                        "for this particular label."
                    )

                # ------------------------------------------------
                # SUMMARY
                # ------------------------------------------------

                st.markdown("""
                <div class="section-card">
                    <div class="section-title">💡 Understanding the Result</div>
                </div>
                """, unsafe_allow_html=True)

                calories = numeric_value(
                    nutrition.get("calories")
                )
                sugar = numeric_value(
                    nutrition.get("sugar")
                )
                protein = numeric_value(
                    nutrition.get("protein")
                )
                sodium = numeric_value(
                    nutrition.get("sodium")
                )

                summary_parts = []

                if calories is not None:
                    summary_parts.append(
                        f"Calories: **{calories:g} kcal**"
                    )

                if sugar is not None:
                    summary_parts.append(
                        f"Sugar: **{sugar:g} g**"
                    )

                if protein is not None:
                    summary_parts.append(
                        f"Protein: **{protein:g} g**"
                    )

                if sodium is not None:
                    summary_parts.append(
                        f"Sodium: **{sodium:g} mg**"
                    )

                if summary_parts:
                    st.markdown(
                        " • ".join(summary_parts)
                    )

                # ------------------------------------------------
                # HUMAN-READABLE EXPLANATION
                # ------------------------------------------------

                explanation_parts = []

                if calories is not None:
                    if calories <= 150:
                        explanation_parts.append(
                            "The calorie value is relatively moderate for the "
                            "detected serving."
                        )
                    elif calories <= 300:
                        explanation_parts.append(
                            "The product provides a moderate amount of "
                            "calories for the detected serving."
                        )
                    else:
                        explanation_parts.append(
                            "The product is relatively calorie-dense for the "
                            "detected serving."
                        )

                if sugar is not None:
                    if sugar <= 5:
                        explanation_parts.append(
                            "The detected sugar level is relatively low."
                        )
                    elif sugar <= 15:
                        explanation_parts.append(
                            "The detected sugar level is moderate."
                        )
                    else:
                        explanation_parts.append(
                            "The detected sugar level is relatively high."
                        )

                if sodium is not None:
                    if sodium <= 140:
                        explanation_parts.append(
                            "The sodium level is relatively low."
                        )
                    elif sodium <= 400:
                        explanation_parts.append(
                            "The sodium level is moderate."
                        )
                    else:
                        explanation_parts.append(
                            "The sodium level is relatively high."
                        )

                if protein is not None:
                    if protein >= 10:
                        explanation_parts.append(
                            "The product provides a good amount of protein "
                            "for the detected serving."
                        )
                    elif protein >= 5:
                        explanation_parts.append(
                            "The product provides a moderate amount of protein."
                        )
                    else:
                        explanation_parts.append(
                            "The product provides a relatively small amount "
                            "of protein."
                        )

                if explanation_parts:
                    explanation_html = "<br><br>".join(
                        f"• {item}" for item in explanation_parts
                    )

                    st.markdown(
                        f"""
                        <div class="result-explanation">
                            <div class="result-explanation-title">
                                🧠 What does this mean?
                            </div>
                            <div class="result-explanation-text">
                                {explanation_html}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.info(
                        "Not enough extracted nutrition information is "
                        "available to generate a detailed explanation."
                    )

                st.caption(
                    "Values marked 'Not available' were not reliably "
                    "extracted from the label and are not treated as zero."
                )

            except Exception as e:

                st.error(
                    "Something went wrong while processing this image."
                )

                st.exception(e)


# ============================================================
# TAB 2 - PRODUCT COMPARISON
# ============================================================

with tab2:

    st.markdown("""
    <div class="section-card">
        <div class="section-title">⚖️ Product Comparison</div>
        <div class="section-subtitle">
            Compare two food products using calories, sugar, fat,
            protein, fibre and sodium.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:

        st.markdown(
            '<div class="section-title">🅰️ Product A</div>',
            unsafe_allow_html=True
        )

        file_a = st.file_uploader(
            "Upload Product A label",
            type=["png", "jpg", "jpeg", "webp"],
            key="product_a"
        )

    with col_b:

        st.markdown(
            '<div class="section-title">🅱️ Product B</div>',
            unsafe_allow_html=True
        )

        file_b = st.file_uploader(
            "Upload Product B label",
            type=["png", "jpg", "jpeg", "webp"],
            key="product_b"
        )

    if file_a is not None and file_b is not None:

        with st.spinner("⚖️ Processing both products..."):

            try:

                (
                    image_a,
                    processed_a,
                    raw_a,
                    cleaned_a,
                    product_a
                ) = process_image(file_a)

                (
                    image_b,
                    processed_b,
                    raw_b,
                    cleaned_b,
                    product_b
                ) = process_image(file_b)

                # ------------------------------------------------
                # SHOW PRODUCT IMAGES
                # ------------------------------------------------

                img_col_a, img_col_b = st.columns(2)

                with img_col_a:
                    st.image(
                        image_a,
                        caption="Product A",
                        use_container_width=True
                    )

                with img_col_b:
                    st.image(
                        image_b,
                        caption="Product B",
                        use_container_width=True
                    )

                # ------------------------------------------------
                # PACKAGE WEIGHT HANDLING
                # ------------------------------------------------

                package_weight_a = None
                package_weight_b = None

                if is_non_mass_serving(product_a):

                    st.warning(
                        "Product A uses a non-mass serving "
                        "such as package/piece."
                    )

                    package_weight_a = st.number_input(
                        "Enter Product A package weight (g)",
                        min_value=0.1,
                        step=1.0,
                        value=None,
                        key="weight_a"
                    )

                if is_non_mass_serving(product_b):

                    st.warning(
                        "Product B uses a non-mass serving "
                        "such as package/piece."
                    )

                    package_weight_b = st.number_input(
                        "Enter Product B package weight (g)",
                        min_value=0.1,
                        step=1.0,
                        value=None,
                        key="weight_b"
                    )

                # ------------------------------------------------
                # COMPARISON
                # ------------------------------------------------

                st.markdown("""
                <div class="section-card">
                    <div class="section-title">
                        📋 Nutrient-by-Nutrient Comparison
                    </div>
                </div>
                """, unsafe_allow_html=True)

                comparison_df, score_a, score_b, comparable, result = \
                    compare_products(product_a, product_b)

                st.dataframe(
                    comparison_df,
                    use_container_width=True,
                    hide_index=True
                )

                # ------------------------------------------------
                # SCORE
                # ------------------------------------------------

                score_col1, score_col2, score_col3 = st.columns(3)

                with score_col1:
                    st.metric(
                        "Product A Score",
                        score_a
                    )

                with score_col2:
                    st.metric(
                        "Product B Score",
                        score_b
                    )

                with score_col3:
                    st.metric(
                        "Comparable Nutrients",
                        comparable
                    )

                # ------------------------------------------------
                # FINAL RESULT
                # ------------------------------------------------

                st.markdown(
                    f"""
                    <div class="comparison-result">
                        <h2>🏆 Comparison Result</h2>
                        <div style="font-size:1.1rem;">
                            {result}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.caption(
                    "Comparison only uses nutrient values available "
                    "for both products. Missing values are not treated "
                    "as zero."
                )

            except Exception as e:

                st.error(
                    "Something went wrong while comparing the products."
                )

                st.exception(e)


# ------------------------------------------------------------
# FOOTER
# ------------------------------------------------------------

st.markdown("""
<div class="footer">
    <b>Nutrition Fact Analyzer</b><br>
    Data Science-Based Food Nutrition Analysis System<br><br>
    For informational purposes only. This system is not a substitute
    for professional medical advice.
</div>
""", unsafe_allow_html=True)
