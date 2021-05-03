SELECT cs_id, ROUND(avg(score)) AS Bld_Ensemble_Average_Score
FROM "Building_Model_Score"
GROUP BY cs_id;

SELECT cs_id, avg(score) AS Bld_Ensemble_Average_Score
FROM "Building_Model_Score"
GROUP BY cs_id;