import pandas as pd
from pathlib import Path


RAW_DATA_PATH = Path("data/raw/raw_cut_data.csv")
PROCESSED_DATA_PATH = Path("data/processed/processed_cut_data.csv")


def load_raw_data(file_path):
    """Load the raw cutting phase CSV file."""
    return pd.read_csv(file_path)


def clean_data(df):
    """Clean and prepare the cutting phase dataset."""

    # Make a copy so we do not accidentally modify the original dataframe
    df = df.copy()

    # Convert date column into proper datetime format
    df["date"] = pd.to_datetime(df["date"])

    # Sort by date
    df = df.sort_values("date").reset_index(drop=True)

    # Calculate estimated calorie deficit
    df["estimated_deficit_kcal"] = df["expenditure_kcal"] - df["calories_kcal"]

    # Compare actual intake with targets
    df["calorie_difference"] = df["calories_kcal"] - df["target_calories_kcal"]
    df["protein_difference"] = df["protein_g"] - df["target_protein_g"]
    df["fat_difference"] = df["fat_g"] - df["target_fat_g"]
    df["carbs_difference"] = df["carbs_g"] - df["target_carbs_g"]

    # Target adherence columns
    df["met_protein_target"] = df["protein_g"] >= df["target_protein_g"]
    df["exceeded_calorie_target"] = df["calories_kcal"] > df["target_calories_kcal"]

    # Protein relative to body weight
    df["protein_per_kg"] = df["protein_g"] / df["trend_weight_kg"]

    # Weekly grouping column
    df["week"] = df["date"].dt.to_period("W").astype(str)

    # Daily trend weight change
    df["trend_weight_change"] = df["trend_weight_kg"].diff()

    # Daily scale weight change
    df["scale_weight_change"] = df["weight_kg"].diff()

    return df


def save_processed_data(df, file_path):
    """Save cleaned data to processed folder."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(file_path, index=False)


def main():
    raw_df = load_raw_data(RAW_DATA_PATH)
    processed_df = clean_data(raw_df)
    save_processed_data(processed_df, PROCESSED_DATA_PATH)

    print("Cleaning complete.")
    print(f"Rows processed: {len(processed_df)}")
    print(f"Columns created: {len(processed_df.columns)}")
    print(f"Saved to: {PROCESSED_DATA_PATH}")


if __name__ == "__main__":
    main()