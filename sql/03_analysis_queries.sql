-- Cutting Phase SQL Analysis Queries
-- Database: data/fitness_cut.db
-- Table: daily_cut_data


-- 1. Preview the dataset
SELECT *
FROM daily_cut_data
LIMIT 10;


-- 2. Overall summary statistics
SELECT
    COUNT(*) AS total_logged_days,
    ROUND(MIN(weight_kg), 2) AS min_scale_weight,
    ROUND(MAX(weight_kg), 2) AS max_scale_weight,
    ROUND(AVG(weight_kg), 2) AS avg_scale_weight,
    ROUND(AVG(trend_weight_kg), 2) AS avg_trend_weight,
    ROUND(AVG(calories_kcal), 1) AS avg_calories,
    ROUND(AVG(target_calories_kcal), 1) AS avg_target_calories,
    ROUND(AVG(protein_g), 1) AS avg_protein,
    ROUND(AVG(target_protein_g), 1) AS avg_target_protein,
    ROUND(AVG(estimated_deficit_kcal), 1) AS avg_estimated_deficit,
    ROUND(AVG(steps), 0) AS avg_steps
FROM daily_cut_data;


-- 3. Start vs end body weight trend
SELECT
    MIN(date) AS start_date,
    MAX(date) AS end_date,
    ROUND(
        (SELECT trend_weight_kg FROM daily_cut_data ORDER BY date ASC LIMIT 1),
        2
    ) AS start_trend_weight,
    ROUND(
        (SELECT trend_weight_kg FROM daily_cut_data ORDER BY date DESC LIMIT 1),
        2
    ) AS end_trend_weight,
    ROUND(
        (SELECT trend_weight_kg FROM daily_cut_data ORDER BY date DESC LIMIT 1)
        -
        (SELECT trend_weight_kg FROM daily_cut_data ORDER BY date ASC LIMIT 1),
        2
    ) AS total_trend_weight_change
FROM daily_cut_data;


-- 4. Weekly averages
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


-- 5. Calorie target adherence
SELECT
    COUNT(*) AS total_days,
    SUM(CASE WHEN exceeded_calorie_target = 1 THEN 1 ELSE 0 END) AS days_over_calorie_target,
    ROUND(
        100.0 * SUM(CASE WHEN exceeded_calorie_target = 1 THEN 1 ELSE 0 END) / COUNT(*),
        1
    ) AS percent_days_over_calorie_target
FROM daily_cut_data;


-- 6. Protein target adherence
SELECT
    COUNT(*) AS total_days,
    SUM(CASE WHEN met_protein_target = 1 THEN 1 ELSE 0 END) AS days_met_protein_target,
    ROUND(
        100.0 * SUM(CASE WHEN met_protein_target = 1 THEN 1 ELSE 0 END) / COUNT(*),
        1
    ) AS percent_days_met_protein_target
FROM daily_cut_data;


-- 7. Days with the largest estimated calorie deficits
SELECT
    date,
    calories_kcal,
    expenditure_kcal,
    estimated_deficit_kcal,
    steps
FROM daily_cut_data
ORDER BY estimated_deficit_kcal DESC
LIMIT 10;


-- 8. Days with the smallest deficit or possible surplus
SELECT
    date,
    calories_kcal,
    expenditure_kcal,
    estimated_deficit_kcal,
    steps
FROM daily_cut_data
ORDER BY estimated_deficit_kcal ASC
LIMIT 10;


-- 9. Highest protein days
SELECT
    date,
    protein_g,
    target_protein_g,
    protein_difference,
    ROUND(protein_per_kg, 2) AS protein_per_kg
FROM daily_cut_data
ORDER BY protein_g DESC
LIMIT 10;


-- 10. Days with high steps
SELECT
    date,
    steps,
    calories_kcal,
    expenditure_kcal,
    estimated_deficit_kcal
FROM daily_cut_data
ORDER BY steps DESC
LIMIT 10;


-- 11. Average deficit by step range
SELECT
    CASE
        WHEN steps < 8000 THEN 'Below 8,000'
        WHEN steps BETWEEN 8000 AND 11999 THEN '8,000-11,999'
        WHEN steps BETWEEN 12000 AND 15999 THEN '12,000-15,999'
        ELSE '16,000+'
    END AS step_range,
    COUNT(*) AS days,
    ROUND(AVG(steps), 0) AS avg_steps,
    ROUND(AVG(calories_kcal), 1) AS avg_calories,
    ROUND(AVG(estimated_deficit_kcal), 1) AS avg_estimated_deficit
FROM daily_cut_data
GROUP BY step_range
ORDER BY avg_steps;


-- 12. Days where calories were over target but deficit was still positive
SELECT
    date,
    calories_kcal,
    target_calories_kcal,
    calorie_difference,
    expenditure_kcal,
    estimated_deficit_kcal
FROM daily_cut_data
WHERE calories_kcal > target_calories_kcal
  AND estimated_deficit_kcal > 0
ORDER BY calorie_difference DESC;