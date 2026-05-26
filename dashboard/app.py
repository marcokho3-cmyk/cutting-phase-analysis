from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


DATA_PATH = Path("data/processed/processed_cut_data.csv")
PREDICTIONS_PATH = Path("data/processed/model_predictions.csv")

st.set_page_config(
    page_title="Cutting Phase Analytics Dashboard",
    layout="wide"
)


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["date"] = pd.to_datetime(df["date"])

    # Rename columns for cleaner chart legends and dashboard labels
    df = df.rename(columns={
        "weight_kg": "Scale Weight",
        "trend_weight_kg": "Trend Weight",
        "calories_kcal": "Calories",
        "target_calories_kcal": "Target Calories",
        "protein_g": "Protein",
        "target_protein_g": "Target Protein",
        "estimated_deficit_kcal": "Estimated Deficit",
        "steps": "Steps",
        "week": "Week",
        "trend_weight_change": "Trend Weight Change",
        "scale_weight_change": "Scale Weight Change",
        "protein_per_kg": "Protein per kg",
        "met_protein_target": "Met Protein Target",
        "exceeded_calorie_target": "Exceeded Calorie Target"
    })

    return df

@st.cache_data
def load_predictions():
    predictions_df = pd.read_csv(PREDICTIONS_PATH)
    predictions_df["date"] = pd.to_datetime(predictions_df["date"])
    return predictions_df

df = load_data()
predictions_df = load_predictions()

st.title("Cutting Phase Analytics Dashboard")

st.write(
    """
    This dashboard analyses body weight trends, calorie intake, macro adherence,
    activity levels, and estimated calorie deficit during a cutting phase.
    """
)


# Sidebar filters
st.sidebar.header("Filters")

min_date = df["date"].min()
max_date = df["date"].max()

date_range = st.sidebar.date_input(
    "Select date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = df[
        (df["date"] >= pd.to_datetime(start_date)) &
        (df["date"] <= pd.to_datetime(end_date))
    ].copy()
else:
    filtered_df = df.copy()


# Safety check in case the date filter returns nothing
if filtered_df.empty:
    st.warning("No data available for the selected date range.")
    st.stop()


# KPI calculations
start_trend_weight = filtered_df["Trend Weight"].iloc[0]
end_trend_weight = filtered_df["Trend Weight"].iloc[-1]
trend_weight_change = end_trend_weight - start_trend_weight

avg_calories = filtered_df["Calories"].mean()
avg_protein = filtered_df["Protein"].mean()
avg_deficit = filtered_df["Estimated Deficit"].mean()
avg_steps = filtered_df["Steps"].mean()

protein_hit_rate = filtered_df["Met Protein Target"].mean() * 100
calorie_exceed_rate = filtered_df["Exceeded Calorie Target"].mean() * 100


# Tabs
overview_tab, nutrition_tab, weight_tab, activity_tab, weekly_tab, ml_tab = st.tabs(
    [
        "Overview",
        "Nutrition",
        "Weight Progress",
        "Activity & Deficit",
        "Weekly Summary",
        "ML Prediction"
    ]
)


with overview_tab:
    st.subheader("Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Trend Weight Change",
        f"{trend_weight_change:.2f} kg"
    )

    col2.metric(
        "Average Calories",
        f"{avg_calories:.0f} kcal"
    )

    col3.metric(
        "Average Deficit",
        f"{avg_deficit:.0f} kcal"
    )

    col4.metric(
        "Average Steps",
        f"{avg_steps:.0f}"
    )

    col5, col6, col7, col8 = st.columns(4)

    col5.metric(
        "Start Trend Weight",
        f"{start_trend_weight:.2f} kg"
    )

    col6.metric(
        "End Trend Weight",
        f"{end_trend_weight:.2f} kg"
    )

    col7.metric(
        "Protein Target Hit Rate",
        f"{protein_hit_rate:.1f}%"
    )

    col8.metric(
        "Days Over Calorie Target",
        f"{calorie_exceed_rate:.1f}%"
    )

    st.info(
        f"""
        Across the selected period, trend weight changed by **{trend_weight_change:.2f} kg**.
        Average estimated daily deficit was **{avg_deficit:.0f} kcal**, with average daily
        intake of **{avg_calories:.0f} kcal**.
        """
    )

    st.info(
        f"""
        Protein target was met on **{protein_hit_rate:.1f}%** of logged days, while calorie
        target was exceeded on **{calorie_exceed_rate:.1f}%** of logged days.
        """
    )


with nutrition_tab:
    st.subheader("Calories and Protein")

    fig_calories = px.line(
        filtered_df,
        x="date",
        y=["Calories", "Target Calories"],
        title="Calories vs Target Calories",
        labels={
            "value": "Calories (kcal)",
            "date": "Date",
            "variable": "Metric"
        }
    )

    st.plotly_chart(fig_calories, use_container_width=True)

    fig_protein = px.line(
        filtered_df,
        x="date",
        y=["Protein", "Target Protein"],
        title="Protein vs Target Protein",
        labels={
            "value": "Protein (g)",
            "date": "Date",
            "variable": "Metric"
        }
    )

    st.plotly_chart(fig_protein, use_container_width=True)

    fig_protein_per_kg = px.line(
        filtered_df,
        x="date",
        y="Protein per kg",
        title="Protein Intake per kg of Trend Body Weight",
        labels={
            "Protein per kg": "Protein (g/kg)",
            "date": "Date"
        }
    )

    st.plotly_chart(fig_protein_per_kg, use_container_width=True)


with weight_tab:
    st.subheader("Weight Progress")

    fig_weight = px.line(
        filtered_df,
        x="date",
        y=["Scale Weight", "Trend Weight"],
        title="Daily Scale Weight vs Trend Weight",
        labels={
            "value": "Weight (kg)",
            "date": "Date",
            "variable": "Metric"
        }
    )

    st.plotly_chart(fig_weight, use_container_width=True)

    fig_weight_change = px.bar(
        filtered_df,
        x="date",
        y="Trend Weight Change",
        title="Daily Trend Weight Change",
        labels={
            "Trend Weight Change": "Change in Trend Weight (kg)",
            "date": "Date"
        }
    )

    st.plotly_chart(fig_weight_change, use_container_width=True)

    st.info(
        """
        Daily scale weight fluctuates due to water, food volume, sodium, and other short-term
        factors. Trend weight gives a smoother view of the overall cutting progress.
        """
    )


with activity_tab:
    st.subheader("Deficit and Activity")

    fig_deficit = px.bar(
        filtered_df,
        x="date",
        y="Estimated Deficit",
        title="Estimated Daily Calorie Deficit",
        labels={
            "Estimated Deficit": "Estimated Deficit (kcal)",
            "date": "Date"
        }
    )

    st.plotly_chart(fig_deficit, use_container_width=True)

    fig_steps = px.line(
        filtered_df,
        x="date",
        y="Steps",
        title="Daily Step Count",
        labels={
            "Steps": "Steps",
            "date": "Date"
        }
    )

    st.plotly_chart(fig_steps, use_container_width=True)

    fig_steps_deficit = px.scatter(
        filtered_df,
        x="Steps",
        y="Estimated Deficit",
        trendline="ols",
        title="Steps vs Estimated Calorie Deficit",
        labels={
            "Steps": "Daily Steps",
            "Estimated Deficit": "Estimated Deficit (kcal)"
        }
    )

    st.plotly_chart(fig_steps_deficit, use_container_width=True)

    st.info(
        """
        This scatterplot helps explore whether higher activity days were generally associated
        with larger estimated calorie deficits. The trend line is exploratory, not proof of
        causation.
        """
    )


with weekly_tab:
    st.subheader("Weekly Summary")

    weekly_df = (
        filtered_df
        .groupby("Week")
        .agg({
            "Scale Weight": "mean",
            "Trend Weight": "mean",
            "Calories": "mean",
            "Protein": "mean",
            "Estimated Deficit": "mean",
            "Steps": "mean"
        })
        .reset_index()
    )

    # Round values for cleaner dashboard display
    weekly_display_df = weekly_df.copy()
    weekly_display_df["Scale Weight"] = weekly_display_df["Scale Weight"].round(2)
    weekly_display_df["Trend Weight"] = weekly_display_df["Trend Weight"].round(2)
    weekly_display_df["Calories"] = weekly_display_df["Calories"].round(0)
    weekly_display_df["Protein"] = weekly_display_df["Protein"].round(1)
    weekly_display_df["Estimated Deficit"] = weekly_display_df["Estimated Deficit"].round(0)
    weekly_display_df["Steps"] = weekly_display_df["Steps"].round(0)

    st.dataframe(weekly_display_df, use_container_width=True)

    fig_weekly_weight = px.line(
        weekly_df,
        x="Week",
        y="Trend Weight",
        title="Weekly Average Trend Weight",
        labels={
            "Trend Weight": "Average Trend Weight (kg)",
            "Week": "Week"
        }
    )

    st.plotly_chart(fig_weekly_weight, use_container_width=True)

    fig_weekly_deficit = px.bar(
        weekly_df,
        x="Week",
        y="Estimated Deficit",
        title="Weekly Average Estimated Deficit",
        labels={
            "Estimated Deficit": "Average Estimated Deficit (kcal)",
            "Week": "Week"
        }
    )

    st.plotly_chart(fig_weekly_deficit, use_container_width=True)

with ml_tab:
    st.subheader("Machine Learning Prediction")

    st.write(
        """
        This section compares actual next-day trend weight with predictions from simple
        regression models. Because the dataset is small, this model should be interpreted
        as an exploratory extension rather than a production-level prediction system.
        """
    )

    best_model_name = predictions_df["best_model_name"].iloc[0]
    model_name_display = best_model_name.replace("_", " ").title()

    st.info(
        f"""
        Best model selected from the training script: **{model_name_display}**.
        The model predicts next-day trend weight using nutrition, expenditure,
        activity, and current trend weight features.
        """
    )

    # Rename columns for cleaner chart labels
    ml_chart_df = predictions_df.rename(columns={
        "date": "Date",
        "trend_weight_kg": "Current Trend Weight",
        "actual_next_day_trend_weight": "Actual Next-Day Trend Weight",
        "baseline_prediction": "Baseline Prediction",
        "linear_regression_prediction": "Linear Regression Prediction",
        "random_forest_prediction": "Random Forest Prediction",
        "best_model_prediction": "Best Model Prediction",
        "best_model_name": "Best Model"
    })

    show_all_models = st.checkbox(
        "Show all model predictions",
        value=False
    )

    if show_all_models:
        prediction_columns = [
            "Actual Next-Day Trend Weight",
            "Baseline Prediction",
            "Linear Regression Prediction",
            "Random Forest Prediction"
        ]
    else:
        prediction_columns = [
            "Actual Next-Day Trend Weight",
            "Baseline Prediction",
            "Best Model Prediction"
        ]

    fig_predictions = px.line(
        ml_chart_df,
        x="Date",
        y=prediction_columns,
        title="Actual vs Predicted Next-Day Trend Weight",
        labels={
            "value": "Trend Weight (kg)",
            "Date": "Date",
            "variable": "Prediction Type"
        }
    )

    st.plotly_chart(fig_predictions, use_container_width=True)

    st.caption(
        """
        The default chart shows the actual values, a simple baseline, and the best selected model.
        Use the checkbox to compare the individual trained models. When the best model is Linear
        Regression, the Best Model Prediction would overlap with the Linear Regression line, so it
        is hidden in the full comparison view.
        """
    )

    predictions_display = ml_chart_df.copy()

    numeric_columns = [
        "Current Trend Weight",
        "Actual Next-Day Trend Weight",
        "Baseline Prediction",
        "Linear Regression Prediction",
        "Random Forest Prediction",
        "Best Model Prediction"
    ]

    for column in numeric_columns:
        predictions_display[column] = predictions_display[column].round(3)

    st.dataframe(predictions_display, use_container_width=True)