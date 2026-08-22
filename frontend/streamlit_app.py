import streamlit as st
import requests
from datetime import date


# --------------------------------------------------
# 1. Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Sydney Housing Price Predictor",
    page_icon="🏠",
    layout="centered"
)


# --------------------------------------------------
# 2. Backend API
# --------------------------------------------------

API_URL = (
    "https://sydney-housing-price-backend.onrender.com/predict"
)


# --------------------------------------------------
# 3. Title and Introduction
# --------------------------------------------------

st.title("🏠 Sydney Housing Price Predictor")

st.write(
    "Enter the available property details below to "
    "estimate the sale price using the trained "
    "Gradient Boosting regression model."
)

st.info(
    "The predicted price is an ML-based estimate and "
    "should not be considered a professional property valuation."
)


# --------------------------------------------------
# 4. Property Details
# --------------------------------------------------

st.subheader("Property Details")

suburb = st.selectbox(
    "Suburb",
    [
        "Mosman",
        "Penrith",
        "Parramatta"
    ]
)

property_type = st.selectbox(
    "Property Type",
    [
        "House",
        "Unit"
    ]
)


col1, col2 = st.columns(2)

with col1:

    bedrooms = st.number_input(
        "Bedrooms",
        min_value=0,
        max_value=20,
        value=3,
        step=1
    )

with col2:

    bathrooms = st.number_input(
        "Bathrooms",
        min_value=0,
        max_value=20,
        value=2,
        step=1
    )


parking = st.number_input(
    "Parking Spaces",
    min_value=0,
    max_value=10,
    value=1,
    step=1
)


# --------------------------------------------------
# 5. Binary Features
# --------------------------------------------------
#
# Training representation:
# 1    = explicitly reported as present
# NaN  = not specified
#
# Therefore we do NOT create a "No = 0" option.
# --------------------------------------------------

st.subheader("Property Features")


garden_option = st.selectbox(
    "Garden",
    [
        "Not specified",
        "Yes"
    ]
)

swimming_pool_option = st.selectbox(
    "Swimming Pool",
    [
        "Not specified",
        "Yes"
    ]
)

water_view_option = st.selectbox(
    "Water View",
    [
        "Not specified",
        "Yes"
    ]
)


# Convert UI values to the representation
# used by the trained model.

garden = (
    1
    if garden_option == "Yes"
    else None
)

swimming_pool = (
    1
    if swimming_pool_option == "Yes"
    else None
)

water_view = (
    1
    if water_view_option == "Yes"
    else None
)


# --------------------------------------------------
# 6. Property Size
# --------------------------------------------------

st.subheader("Property Size")


land_size_m2 = st.number_input(
    "Land Size (m²)",
    min_value=0.0,
    value=500.0,
    step=10.0
)


building_size_option = st.selectbox(
    "Building Size",
    [
        "Enter value",
        "Not specified"
    ]
)


if building_size_option == "Enter value":

    building_size_m2 = st.number_input(
        "Building Size (m²)",
        min_value=0.0,
        value=100.0,
        step=10.0
    )

else:

    building_size_m2 = None


# --------------------------------------------------
# 7. Distance to Schools
# --------------------------------------------------

st.subheader("Nearby Schools")


nearest_primary_school_km = st.number_input(
    "Nearest Primary School (km)",
    min_value=0.0,
    value=1.0,
    step=0.01
)


nearest_secondary_school_km = st.number_input(
    "Nearest Secondary School (km)",
    min_value=0.0,
    value=1.0,
    step=0.01
)


# --------------------------------------------------
# 8. Sale Date
# --------------------------------------------------

st.subheader("Sale Information")


sale_date = st.date_input(
    "Sale Date",
    value=date.today()
)


# --------------------------------------------------
# 9. Prediction
# --------------------------------------------------

st.divider()


if st.button(
    "Predict Sale Price",
    type="primary",
    use_container_width=True
):

    # ----------------------------------------------
    # Construct JSON payload
    # ----------------------------------------------

    payload = {

        # Categorical features
        "suburb": suburb,
        "property_type": property_type,

        # Numeric features
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "parking": parking,
        "land_size_m2": land_size_m2,
        "building_size_m2": building_size_m2,
        "nearest_primary_school_km":
            nearest_primary_school_km,
        "nearest_secondary_school_km":
            nearest_secondary_school_km,

        # Binary features
        "garden": garden,
        "swimming_pool": swimming_pool,
        "water_view": water_view,

        # Date feature
        "sale_date": sale_date.isoformat()
    }


    # ----------------------------------------------
    # Send request to Flask API
    # ----------------------------------------------

    try:

        with st.spinner(
            "Generating prediction..."
        ):

            response = requests.post(
                API_URL,
                json=payload,
                timeout=120
            )


        # ------------------------------------------
        # Successful prediction
        # ------------------------------------------

        if response.status_code == 200:

            result = response.json()

            predicted_price = result[
                "predicted_price"
            ]

            st.success(
                "Prediction generated successfully!"
            )

            st.metric(
                label="Estimated Sale Price",
                value=f"${predicted_price:,.0f}"
            )


        # ------------------------------------------
        # API returned an error
        # ------------------------------------------

        else:

            st.error(
                f"API request failed "
                f"({response.status_code})"
            )

            st.code(
                response.text
            )


    # ----------------------------------------------
    # Connection / timeout errors
    # ----------------------------------------------

    except requests.exceptions.Timeout:

        st.error(
            "The prediction service took too long "
            "to respond. The Render backend may be "
            "starting after a period of inactivity. "
            "Please try again."
        )


    except requests.exceptions.RequestException as e:

        st.error(
            f"Could not connect to the prediction API: {e}"
        )
