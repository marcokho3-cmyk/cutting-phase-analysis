import sqlite3
from pathlib import Path

import pandas as pd


PROCESSED_DATA_PATH = Path("data/processed/processed_cut_data.csv")
DATABASE_PATH = Path("data/fitness_cut.db")
TABLE_NAME = "daily_cut_data"


def load_processed_data(file_path):
    """Load the processed cutting phase dataset."""
    return pd.read_csv(file_path)


def create_database(df, database_path, table_name):
    """Create a SQLite database and save the dataframe as a table."""

    database_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(database_path)

    df.to_sql(
        table_name,
        connection,
        if_exists="replace",
        index=False
    )

    connection.close()


def main():
    df = load_processed_data(PROCESSED_DATA_PATH)
    create_database(df, DATABASE_PATH, TABLE_NAME)

    print("Database created successfully.")
    print(f"Rows inserted: {len(df)}")
    print(f"Database path: {DATABASE_PATH}")
    print(f"Table name: {TABLE_NAME}")


if __name__ == "__main__":
    main()