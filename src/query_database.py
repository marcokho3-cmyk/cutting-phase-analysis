import sqlite3
from pathlib import Path

import pandas as pd


DATABASE_PATH = Path("data/fitness_cut.db")


QUERIES = {
    "overall_summary": """
        SELECT
            COUNT(*) AS total_logged_days,
            ROUND(AVG(calories_kcal), 1) AS avg_calories,
            ROUND(AVG(target_calories_kcal), 1) AS avg_target_calories,
            ROUND(AVG(protein_g), 1) AS avg_protein,
            ROUND(AVG(target_protein_g), 1) AS avg_target_protein,
            ROUND(AVG(estimated_deficit_kcal), 1) AS avg_estimated_deficit,
            ROUND(AVG(steps), 0) AS avg_steps
        FROM daily_cut_data;
    """,

    "weekly_averages": """
        SELECT
            week,
            COUNT(*) AS logged_days,
            ROUND(AVG(weight_kg), 2) AS avg_scale_weight,
            ROUND(AVG(trend_weight_kg), 2) AS avg_trend_weight,
            ROUND(AVG(calories_kcal), 1) AS avg_calories,
            ROUND(AVG(protein_g), 1) AS avg_protein,
            ROUND(AVG(estimated_deficit_kcal), 1) AS avg_estimated_deficit,
            ROUND(AVG(steps), 0) AS avg_steps
        FROM daily_cut_data
        GROUP BY week
        ORDER BY week;
    """,

    "protein_adherence": """
        SELECT
            COUNT(*) AS total_days,
            SUM(CASE WHEN met_protein_target = 1 THEN 1 ELSE 0 END) AS days_met_protein_target,
            ROUND(
                100.0 * SUM(CASE WHEN met_protein_target = 1 THEN 1 ELSE 0 END) / COUNT(*),
                1
            ) AS percent_days_met_protein_target
        FROM daily_cut_data;
    """,

    "calorie_adherence": """
        SELECT
            COUNT(*) AS total_days,
            SUM(CASE WHEN exceeded_calorie_target = 1 THEN 1 ELSE 0 END) AS days_over_calorie_target,
            ROUND(
                100.0 * SUM(CASE WHEN exceeded_calorie_target = 1 THEN 1 ELSE 0 END) / COUNT(*),
                1
            ) AS percent_days_over_calorie_target
        FROM daily_cut_data;
    """
}


def run_query(query_name):
    """Run a saved SQL query by name."""

    if query_name not in QUERIES:
        print("Query not found.")
        print("Available queries:")
        for name in QUERIES:
            print(f"- {name}")
        return

    connection = sqlite3.connect(DATABASE_PATH)
    result = pd.read_sql_query(QUERIES[query_name], connection)
    connection.close()

    print(f"\nQuery: {query_name}")
    print(result)


def main():
    for query_name in QUERIES:
        run_query(query_name)


if __name__ == "__main__":
    main()