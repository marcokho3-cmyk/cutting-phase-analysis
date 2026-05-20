from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split


PROCESSED_DATA_PATH = Path("data/processed/processed_cut_data.csv")
MODEL_PATH = Path("models/weight_prediction_model.pkl")
PREDICTIONS_PATH = Path("data/processed/model_predictions.csv")


FEATURE_COLUMNS = [
    "trend_weight_kg",
    "calories_kcal",
    "protein_g",
    "fat_g",
    "carbs_g",
    "expenditure_kcal",
    "steps",
    "estimated_deficit_kcal",
    "protein_per_kg"
]

TARGET_COLUMN = "next_day_trend_weight"


def load_data(file_path):
    """Load processed cutting phase data."""
    df = pd.read_csv(file_path)
    df["date"] = pd.to_datetime(df["date"])
    return df


def prepare_model_data(df):
    """Create target variable and prepare data for modelling."""

    df = df.copy()

    # Target: tomorrow's trend weight
    df[TARGET_COLUMN] = df["trend_weight_kg"].shift(-1)

    # Drop rows where target or features are missing
    model_df = df.dropna(subset=FEATURE_COLUMNS + [TARGET_COLUMN]).copy()

    return model_df


def evaluate_model(model, X_test, y_test):
    """Calculate model performance metrics."""
    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))

    return mae, rmse, predictions


def train_models(model_df):
    """Train baseline, linear regression, and random forest models."""

    X = model_df[FEATURE_COLUMNS]
    y = model_df[TARGET_COLUMN]

    # No random shuffling because this is time-based data.
    # We keep the earlier part for training and the later part for testing.
    split_index = int(len(model_df) * 0.75)

    X_train = X.iloc[:split_index]
    X_test = X.iloc[split_index:]
    y_train = y.iloc[:split_index]
    y_test = y.iloc[split_index:]

    # Baseline model:
    # Predict tomorrow's trend weight as today's trend weight.
    baseline_predictions = X_test["trend_weight_kg"]
    baseline_mae = mean_absolute_error(y_test, baseline_predictions)
    baseline_rmse = np.sqrt(mean_squared_error(y_test, baseline_predictions))

    # Linear regression model
    linear_model = LinearRegression()
    linear_model.fit(X_train, y_train)
    linear_mae, linear_rmse, linear_predictions = evaluate_model(
        linear_model,
        X_test,
        y_test
    )

    # Random forest model
    forest_model = RandomForestRegressor(
        n_estimators=100,
        random_state=42,
        max_depth=3
    )
    forest_model.fit(X_train, y_train)
    forest_mae, forest_rmse, forest_predictions = evaluate_model(
        forest_model,
        X_test,
        y_test
    )

    results = {
        "baseline": {
            "model": None,
            "mae": baseline_mae,
            "rmse": baseline_rmse,
            "predictions": baseline_predictions.values
        },
        "linear_regression": {
            "model": linear_model,
            "mae": linear_mae,
            "rmse": linear_rmse,
            "predictions": linear_predictions
        },
        "random_forest": {
            "model": forest_model,
            "mae": forest_mae,
            "rmse": forest_rmse,
            "predictions": forest_predictions
        },
        "test_data": {
            "X_test": X_test,
            "y_test": y_test
        }
    }

    return results


def choose_best_model(results):
    """Choose the model with the lowest MAE, excluding the baseline."""

    candidate_models = ["linear_regression", "random_forest"]

    best_model_name = candidate_models[0]
    best_mae = results[best_model_name]["mae"]

    for model_name in candidate_models:
        model_mae = results[model_name]["mae"]

        if model_mae < best_mae:
            best_model_name = model_name
            best_mae = model_mae

    return best_model_name, results[best_model_name]["model"]


def save_model(model, model_path):
    """Save trained model to disk."""
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)


def save_predictions(model_df, results, best_model_name, predictions_path):
    """Save actual vs predicted values for dashboard visualisation."""

    X_test = results["test_data"]["X_test"]
    y_test = results["test_data"]["y_test"]

    predictions_df = model_df.loc[X_test.index, ["date", "trend_weight_kg"]].copy()
    predictions_df["actual_next_day_trend_weight"] = y_test.values
    predictions_df["baseline_prediction"] = results["baseline"]["predictions"]
    predictions_df["linear_regression_prediction"] = results["linear_regression"]["predictions"]
    predictions_df["random_forest_prediction"] = results["random_forest"]["predictions"]
    predictions_df["best_model_prediction"] = results[best_model_name]["predictions"]
    predictions_df["best_model_name"] = best_model_name

    predictions_path.parent.mkdir(parents=True, exist_ok=True)
    predictions_df.to_csv(predictions_path, index=False)


def print_results(results, best_model_name):
    """Print model results to terminal."""

    print("Model training complete.\n")

    print("Performance on test data:")
    print(
        f"Baseline MAE: {results['baseline']['mae']:.4f} kg | "
        f"RMSE: {results['baseline']['rmse']:.4f} kg"
    )
    print(
        f"Linear Regression MAE: {results['linear_regression']['mae']:.4f} kg | "
        f"RMSE: {results['linear_regression']['rmse']:.4f} kg"
    )
    print(
        f"Random Forest MAE: {results['random_forest']['mae']:.4f} kg | "
        f"RMSE: {results['random_forest']['rmse']:.4f} kg"
    )

    print(f"\nBest model selected: {best_model_name}")
    print(f"Model saved to: {MODEL_PATH}")
    print(f"Predictions saved to: {PREDICTIONS_PATH}")

    print(
        "\nNote: This is an exploratory model based on a small dataset. "
        "Results should be interpreted cautiously."
    )


def main():
    df = load_data(PROCESSED_DATA_PATH)
    model_df = prepare_model_data(df)

    results = train_models(model_df)

    best_model_name, best_model = choose_best_model(results)

    save_model(best_model, MODEL_PATH)
    save_predictions(model_df, results, best_model_name, PREDICTIONS_PATH)

    print_results(results, best_model_name)


if __name__ == "__main__":
    main()