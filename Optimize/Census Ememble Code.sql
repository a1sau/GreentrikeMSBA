SELECT bg_geo_id, ROUND(avg(score)) AS Census_Ensemble_Average_Score
FROM "BG_Model_Score"
GROUP BY bg_geo_id;

SELECT bg_geo_id, avg(score) AS Census_Ensemble_Average_Score
FROM "BG_Model_Score"
GROUP BY bg_geo_id;