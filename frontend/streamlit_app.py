if response.status_code == 200:

    result = response.json()

    if "predicted_price" in result:

        predicted_price = result["predicted_price"]

        st.success(
            "Prediction generated successfully!"
        )

        st.metric(
            label="Estimated Sale Price",
            value=f"${predicted_price:,.0f}"
        )

    else:

        st.error(
            "The API responded successfully, "
            "but no predicted price was returned."
        )
